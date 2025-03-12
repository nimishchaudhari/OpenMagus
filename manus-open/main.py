from core.coordinator import CoordinatorAgent
from core.planner import PlannerAgent
from core.knowledge import KnowledgeAgent
from core.executor import ExecutorAgent
from memory.episodic_memory import EpisodicMemory
from memory.semantic_memory import SemanticMemory
from memory.procedural_memory import ProceduralMemory
from tools.tool_registry import ToolRegistry
from tools.browser_automation import BrowserAutomation
from tools.data_processing import DataProcessing
from tools.api_connectors import APIConnectors
from tools.deployment_systems import DeploymentSystems
from router.model_router import ModelRouter

def main():
    # Initialize memory systems
    episodic_memory = EpisodicMemory()
    semantic_memory = SemanticMemory()
    procedural_memory = ProceduralMemory()

    # Initialize tools
    tool_registry = ToolRegistry()
    tool_registry.register_tool('browser_automation', BrowserAutomation())
    tool_registry.register_tool('data_processing', DataProcessing())
    tool_registry.register_tool('api_connectors', APIConnectors())
    tool_registry.register_tool('deployment_systems', DeploymentSystems())

    # Initialize agents
    knowledge_agent = KnowledgeAgent(semantic_memory)
    executor_agent = ExecutorAgent(tool_registry, procedural_memory)
    planner_agent = PlannerAgent(knowledge_agent, executor_agent, procedural_memory)
    coordinator_agent = CoordinatorAgent(planner_agent, knowledge_agent, executor_agent, episodic_memory, semantic_memory, procedural_memory, ModelRouter(None, None, {}))

    # Start the application
    request = {"task": "example", "data": "test"}
    response = coordinator_agent.handle_request(request)
    print(response)

if __name__ == "__main__":
    main()
