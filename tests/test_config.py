import pytest
from core.config_agent import ConfigAgent

@pytest.fixture
def config():
    agent = ConfigAgent()
    return agent

def test_loading_config(config):
    config_data = config.load_config()
    assert isinstance(config_data, dict)
    assert "database_url" in config_data
