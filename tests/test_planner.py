import pytest
from unittest.mock import MagicMock
from core.planner_agent import PlannerAgent

@pytest.fixture
def planner():
    agent = PlannerAgent()
    agent.neo4j_client = MagicMock()
    return agent

def test_planning_task(planner):
    task = {"id": "1", "description": "example task"}
    planner.neo4j_client.run.return_value = [{"n": "example"}]

    response = planner.plan_task(task)

    planner.neo4j_client.run.assert_called_once()
    assert response.get("status") == "task planned"
