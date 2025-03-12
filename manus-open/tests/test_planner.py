import pytest
from unittest.mock import MagicMock
from core.planner import PlannerAgent

@pytest.fixture
def planner():
    # Instantiate your PlannerAgent and set up any dependencies as mocks
    knowledge_agent = MagicMock()
    executor_agent = MagicMock()
    procedural_memory = MagicMock()

    agent = PlannerAgent(knowledge_agent, executor_agent, procedural_memory)
    return agent

def test_handle_task(planner):
    # Simulate an input task
    task = {"task": "example", "data": "test"}
    session_id = 1
    # Suppose the planner should query knowledge and plan the task
    planner.knowledge_agent.query_knowledge.return_value = {"knowledge": "example"}
    planner.plan_task.return_value = {"plan": "example"}

    planner.handle_task(task, session_id)

    # Assert that the knowledge was queried
    planner.knowledge_agent.query_knowledge.assert_called_once()
    # Assert that the task was planned
    planner.plan_task.assert_called_once()
