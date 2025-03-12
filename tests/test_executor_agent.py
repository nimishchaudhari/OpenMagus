import unittest
from unittest.mock import MagicMock, patch
from core.executor_agent import ExecutorAgent
import logging
import time

class TestExecutorAgent(unittest.TestCase):

    def setUp(self):
        self.executor = ExecutorAgent(max_workers=2)
        self.executor.api_client = MagicMock()

    def test_execute_task(self):
        task = {"id": 1, "action": "test_action", "data": "test_data"}
        self.executor.execute_task(task)
        time.sleep(1)  # Give some time for the task to be processed
        self.executor.api_client.post.assert_called_once_with("test_action", data=task)

    def test_error_handling(self):
        task = {"id": 1, "action": "test_action", "data": "test_data"}
        self.executor.api_client.post.side_effect = Exception("Test exception")
        self.executor.execute_task(task)
        time.sleep(1)  # Give some time for the task to be processed
        self.assertEqual(self.executor.api_client.post.call_count, 3)

    def test_parallel_execution(self):
        tasks = [{"id": i, "action": "test_action", "data": f"test_data_{i}"} for i in range(5)]
        for task in tasks:
            self.executor.execute_task(task)
        time.sleep(2)  # Give some time for the tasks to be processed
        self.assertEqual(self.executor.api_client.post.call_count, 5)

    def test_monitoring_and_observability(self):
        task = {"id": 1, "action": "test_action", "data": "test_data"}
        self.executor.execute_task(task)
        time.sleep(1)  # Give some time for the task to be processed
        self.assertEqual(self.executor.task_counter._value.get(), 1)
        self.assertGreater(self.executor.task_duration._sum.get(), 0)

    def test_content_sanitization(self):
        task = {"id": 1, "action": "test_action", "data": "<script>alert('test')</script>"}
        self.executor.execute_task(task)
        time.sleep(1)  # Give some time for the task to be processed
        self.executor.api_client.post.assert_called_once_with("test_action", data={"id": 1, "action": "test_action", "data": "alert('test')"})

if __name__ == '__main__':
    unittest.main()
