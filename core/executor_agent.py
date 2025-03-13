import asyncio
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

class ExecutorAgent:
    """Agent responsible for executing tasks and managing the task queue"""
    
    def __init__(self):
        """Initialize the executor agent"""
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_queue = asyncio.Queue()
        self.workers = []
        self.running = False
        logging.info("Executor agent initialized")

    async def add_task(self, task_data: Dict[str, Any]) -> str:
        """Add a task to the queue"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "data": task_data,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} added to queue")
        return task_id

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        try:
            task_id = task["id"]
            self.tasks[task_id]["status"] = "running"
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            result = {
                "task_id": task_id,
                "status": "completed",
                "result": f"Executed task {task_id}"
            }
            
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["result"] = result
            return result
            
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = str(e)
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }

    async def worker(self):
        """Worker process for executing tasks from queue"""
        while self.running:
            try:
                task = await self.task_queue.get()
                await self.execute_task(task)
                self.task_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker error: {e}")

    async def start(self, num_workers: int = 3):
        """Start the executor with specified number of workers"""
        self.running = True
        self.workers = [
            asyncio.create_task(self.worker())
            for _ in range(num_workers)
        ]
        logging.info(f"Started {num_workers} workers")

    async def stop(self):
        """Stop all workers and cleanup"""
        self.running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        logging.info("Executor stopped")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "cancelled"
            return True
        return False
