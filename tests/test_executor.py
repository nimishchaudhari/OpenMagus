import pytest
from unittest.mock import MagicMock
from core.executor_agent import ExecutorAgent

@pytest.fixture
def executor():
    agent = ExecutorAgent()
    agent.api_client = MagicMock()
    return agent

def test_executing_task(executor):
    task = {"id": "1", "action": "example action"}
    executor.api_client.post.return_value = {"status": "success"}

    response = executor.execute_task(task)

    executor.api_client.post.assert_called_once()
    assert response.get("status") == "task executed"
