import pytest
from unittest.mock import MagicMock
from core.knowledge import KnowledgeAgent

@pytest.fixture
def knowledge():
    # Instantiate your KnowledgeAgent and set up any dependencies as mocks
    semantic_memory = MagicMock()

    agent = KnowledgeAgent(semantic_memory)
    return agent

def test_query_knowledge(knowledge):
    # Simulate an input task
    task = {"task": "example", "data": "test"}
    # Suppose the knowledge agent should query semantic memory
    knowledge.semantic_memory.query.return_value = {"knowledge": "example"}

    result = knowledge.query_knowledge(task)

    # Assert that the semantic memory was queried
    knowledge.semantic_memory.query.assert_called_once()
    # Assert that the result is as expected
    assert result == {"knowledge": "example"}
