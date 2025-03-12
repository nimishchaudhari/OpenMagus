from agents.coordinator import CoordinatorAgent
from agents.planner import PlannerAgent
from agents.knowledge import KnowledgeAgent
from agents.executor import ExecutorAgent
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from tools.registry import ToolRegistry
from tools.browser_automation import BrowserAutomation
from tools.data_processing import DataProcessing
from tools.api_connectors import APIConnectors
from tools.deployment_systems import DeploymentSystems
from router.model_router import ModelRouter
from models.primary_llm import PrimaryLLM
from models.secondary_llm import SecondaryLLM
from models.task_specific_models import TaskSpecificModels

# Create instances of the agents and memory systems
coordinator = CoordinatorAgent()
planner = PlannerAgent()
knowledge = KnowledgeAgent()
executor = ExecutorAgent()
episodic_memory = EpisodicMemory()
semantic_memory = SemanticMemory()
procedural_memory = ProceduralMemory()
tool_registry = ToolRegistry()
browser_automation = BrowserAutomation()
data_processing = DataProcessing()
api_connectors = APIConnectors()
deployment_systems = DeploymentSystems()
model_router = ModelRouter()
primary_llm = PrimaryLLM()
secondary_llm = SecondaryLLM()
task_specific_models = TaskSpecificModels()

# Example usage
request = "Example request"
response = coordinator.handle_request(request)
print(response)
