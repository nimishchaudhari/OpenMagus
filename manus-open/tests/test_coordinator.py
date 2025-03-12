import pytest
from unittest.mock import MagicMock
from core.coordinator import CoordinatorAgent

@pytest.fixture
def coordinator():
    # Instantiate your CoordinatorAgent and set up any dependencies as mocks
    planner_agent = MagicMock()
    knowledge_agent = MagicMock()
    executor_agent = MagicMock()
    episodic_memory = MagicMock()
    semantic_memory = MagicMock()
    procedural_memory = MagicMock()
    model_router = MagicMock()

    agent = CoordinatorAgent(planner_agent, knowledge_agent, executor_agent, episodic_memory, semantic_memory, procedural_memory, model_router)
    return agent

def test_routing_request(coordinator):
    # Simulate an input request
    request = {"task": "example", "data": "test"}
    # Suppose the coordinator should store the session in redis and route the task
    coordinator.episodic_memory.store_session.return_value = 1

    response = coordinator.handle_request(request)

    # Assert that the session was stored
    coordinator.episodic_memory.store_session.assert_called_once()
    # Assert that the response is as expected
    assert response.get("status") == "task routed"
