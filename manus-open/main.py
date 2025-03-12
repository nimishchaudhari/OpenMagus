from core import CoordinatorAgent, PlannerAgent, KnowledgeAgent, ExecutorAgent
from tools import ToolRegistry
from memory import EpisodicMemory, SemanticMemory, ProceduralMemory
from models import PrimaryLLM, SecondaryLLM, TaskSpecificModels
from router import ModelRouter

def main():
    # Initialize agents
    coordinator = CoordinatorAgent()
    planner = PlannerAgent()
    knowledge = KnowledgeAgent()
    executor = ExecutorAgent()

    # Initialize tools
    tool_registry = ToolRegistry()

    # Initialize memory systems
    episodic_memory = EpisodicMemory()
    semantic_memory = SemanticMemory()
    procedural_memory = ProceduralMemory()

    # Initialize models
    primary_llm = PrimaryLLM()
    secondary_llm = SecondaryLLM()
    task_specific_models = TaskSpecificModels()

    # Initialize model router
    model_router = ModelRouter()

    # Main loop
    while True:
        request = input("Enter a request: ")
        coordinator.receive_request(request)
        # Add more logic here

if __name__ == "__main__":
    main()
