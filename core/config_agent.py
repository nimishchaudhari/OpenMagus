class ConfigAgent:
    def __init__(self):
        self.capabilities = {
            "executor": ["execute_task"],
            "coordinator": ["coordinate_tasks"],
            "planner": ["plan_tasks"],
            "knowledge": ["access_knowledge"],
            "config": ["load_config"]
        }

    def load_config(self, agent_name):
        if agent_name not in self.capabilities:
            raise ValueError(f"Unknown agent: {agent_name}")

        return {
            "database_url": "sqlite:///example.db",
            "capabilities": self.capabilities[agent_name],
            # Add other configuration settings here
        }

    def validate_capability(self, agent_name, capability):
        if capability not in self.capabilities.get(agent_name, []):
            raise PermissionError(f"Agent {agent_name} does not have the capability {capability}")
