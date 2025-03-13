import threading
import queue
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from prometheus_client import Counter, Histogram, CollectorRegistry
import bleach

class ExecutorAgent:
    def __init__(self, max_workers=5):
        self.api_client = None
        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

        # Monitoring and observability
        self.registry = CollectorRegistry()
        self.task_counter = Counter('executor_tasks_total', 'Total number of tasks executed', registry=self.registry)
        self.task_duration = Histogram('executor_task_duration_seconds', 'Duration of task execution', registry=self.registry)

    def execute_task(self, task):
        self.task_queue.put(task)

    def _worker(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            self.executor.submit(self._process_task, task)
            self.task_queue.task_done()
    logging.info(f"Task {task['id']} added to queue")

    def _process_task(self, task):
        retries = 3
        delay = 1
        for attempt in range(retries):
            try:
                # Sanitize user inputs
                sanitized_task = {k: bleach.clean(v) if isinstance(v, str) else v for k, v in task.items()}

                with self.task_duration.time():
                    response = self.api_client.post(sanitized_task["action"], data=sanitized_task)
                    self.task_counter.inc()
                    logging.info(f"Task {sanitized_task['id']} executed successfully")
                    return {"status": "task executed"}
            except Exception as e:
                logging.error(f"Task {task['id']} failed on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    logging.error(f"Task {task['id']} failed after {retries} attempts")
                    return {"status": "task failed"}
