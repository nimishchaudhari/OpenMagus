import pytest
from unittest.mock import MagicMock
from core.knowledge_agent import KnowledgeAgent

@pytest.fixture
def knowledge():
    agent = KnowledgeAgent()
    agent.redis_client = MagicMock()
    return agent

def test_storing_knowledge(knowledge):
    data = {"key": "example", "value": "data"}
    knowledge.redis_client.set.return_value = True

    response = knowledge.store_knowledge(data)

    knowledge.redis_client.set.assert_called_once()
    assert response.get("status") == "knowledge stored"
