from core import CoordinatorAgent, PlannerAgent, KnowledgeAgent, ExecutorAgent
from tools import ToolRegistry, BrowserAutomation, DataProcessing, APIConnectors, DeploymentSystems
from memory import EpisodicMemory, SemanticMemory, ProceduralMemory
from router import ModelRouter
from models import LiteLLM
from config import LLM_API_KEY, LLM_MODEL
import argparse

def main():
    # Initialize agents
    coordinator = CoordinatorAgent()
    planner = PlannerAgent()
    knowledge = KnowledgeAgent()
    executor = ExecutorAgent()

    # Initialize tools
    tool_registry = ToolRegistry()
    browser_automation = BrowserAutomation()
    data_processing = DataProcessing()
    api_connectors = APIConnectors()
    deployment_systems = DeploymentSystems()

    # Initialize memory systems
    episodic_memory = EpisodicMemory()
    semantic_memory = SemanticMemory()
    procedural_memory = ProceduralMemory()

    # Initialize model router
    model_router = ModelRouter()

    # Initialize LiteLLM with configuration
    lite_llm = LiteLLM(api_key=LLM_API_KEY, model=LLM_MODEL)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="OpenManus Multi-Agent Framework")
    parser.add_argument("request", type=str, help="User request")
    args = parser.parse_args()

    # Handle user request
    coordinator.receive_request(args.request)

if __name__ == "__main__":
    main()
