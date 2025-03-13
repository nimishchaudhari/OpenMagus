class ConfigAgent:
    def __init__(self):
        self.capabilities = {
            "executor": ["execute_task"],
            "coordinator": ["coordinate_tasks"],
            "planner": ["plan_tasks"],
            "knowledge": ["access_knowledge"],
            "config": ["load_config"]
        }

    def load_config(self, agent_name=None):
        """
        Load configuration for an agent or general configuration if no agent specified
        """
        if agent_name is not None and agent_name not in self.capabilities:
            raise ValueError(f"Unknown agent: {agent_name}")

        config = {
            "database_url": "sqlite:///example.db",
            # Add other general configuration settings here
        }

        if agent_name:
            config["capabilities"] = self.capabilities[agent_name]

        return config

    def validate_capability(self, agent_name, capability):
        if capability not in self.capabilities.get(agent_name, []):
            raise PermissionError(f"Agent {agent_name} does not have the capability {capability}")
