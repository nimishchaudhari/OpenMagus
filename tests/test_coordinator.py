import pytest
from unittest.mock import MagicMock
from core.coordinator_agent import CoordinatorAgent

@pytest.fixture
def coordinator():
    agent = CoordinatorAgent()
    agent.redis_client = MagicMock()
    return agent

def test_routing_request(coordinator):
    request = {"task": "example", "data": "test"}
    coordinator.redis_client.set.return_value = True

    response = coordinator.handle_request(request)

    coordinator.redis_client.set.assert_called_once()
    assert response.get("status") == "task routed"
