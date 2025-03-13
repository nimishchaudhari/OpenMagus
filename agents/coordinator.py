from typing import Dict, Any, Optional, List
from aiohttp import ClientSession
from agents.planner import PlannerAgent
from agents.knowledge import KnowledgeAgent
from agents.executor import ExecutorAgent
from memory.episodic_memory import EpisodicMemory, Session
from memory.semantic_memory import SemanticMemory, KnowledgeEntry
from memory.procedural_memory import ProceduralMemory, Workflow, WorkflowStep
from router.model_router import ModelRouter, ModelConfig, TaskConfig
import logging
import asyncio
from datetime import datetime
import uuid
import json
from dataclasses import dataclass, asdict

@dataclass
class TaskState:
    """Represents the current state of a task"""
    task_id: str
    status: str  # 'pending', 'planning', 'executing', 'completed', 'failed'
    created_at: str
    updated_at: str
    plan: Optional[Dict[str, Any]] = None
    knowledge: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CoordinatorAgent:
    """Coordinates interactions between different agent types and manages task flow"""
    
    def __init__(self):
        """Initialize coordinator with agents and memory systems"""
        # Initialize memory systems
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Initialize model router
        self.model_router = ModelRouter()
        self._setup_model_routing()
        
        # Initialize agents
        self.planner = PlannerAgent()
        self.knowledge = KnowledgeAgent()
        self.executor = ExecutorAgent()
        
        # Task management
        self.tasks: Dict[str, TaskState] = {}
        self.task_lock = asyncio.Lock()
        self.initialized = False
        
        logging.info("Coordinator agent initialized successfully")

    def _setup_model_routing(self):
        """Configure model routing for different task types"""
        # Add model configurations
        planning_model = ModelConfig(
            model_name="gpt-4",
            provider="openai",
            api_key="your-api-key",
            temperature=0.7,
            parameters={"top_p": 0.9}
        )
        self.model_router.add_model(planning_model)
        
        # Add task configurations
        planning_task = TaskConfig(
            task_type="planning",
            required_capabilities=["reasoning", "planning"],
            priority_models=["gpt-4"],
            fallback_models=["gpt-3.5-turbo"]
        )
        self.model_router.add_task_config(planning_task)

    async def initialize(self):
        """Initialize async components after event loop is running"""
        if not self.initialized:
            await self.executor.start(num_workers=3)
            self.initialized = True

    async def _store_session(self, task_id: str, task_state: TaskState):
        """Store task session in episodic memory"""
        session = Session(
            session_id=task_id,
            timestamp=datetime.utcnow().isoformat(),
            context={"task_type": task_state.status},
            actions=[asdict(task_state)],
            outcome=task_state.result or {},
            metadata={"error": task_state.error} if task_state.error else {}
        )
        await asyncio.to_thread(self.episodic_memory.store_session, session)

    async def _store_workflow(self, task_id: str, task_state: TaskState):
        """Store task workflow in procedural memory"""
        if not task_state.plan:
            return
            
        steps = []
        for step in task_state.plan.get("steps", []):
            workflow_step = WorkflowStep(
                action=step["action"],
                parameters=step.get("parameters", {}),
                dependencies=step.get("dependencies", []),
                metadata={"task_id": task_id}
            )
            steps.append(workflow_step)
            
        workflow = Workflow(
            workflow_id=task_id,
            name=f"Task_{task_id}",
            steps=steps,
            metadata={"status": task_state.status}
        )
        await asyncio.to_thread(self.procedural_memory.record_workflow, workflow)

    async def _store_knowledge(self, task_state: TaskState):
        """Store task knowledge in semantic memory"""
        if not task_state.knowledge:
            return
            
        entry = KnowledgeEntry(
            content=json.dumps(task_state.knowledge),
            metadata={"task_id": task_state.task_id}
        )
        await asyncio.to_thread(self.semantic_memory.store_knowledge, entry)

    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task requests"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # Generate task ID and create initial state
            task_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()
            
            task_state = TaskState(
                task_id=task_id,
                status="pending",
                created_at=current_time,
                updated_at=current_time
            )
            
            # Store initial task state
            async with self.task_lock:
                self.tasks[task_id] = task_state
            
            # Update task status
            task_state.status = "planning"
            task_state.updated_at = datetime.utcnow().isoformat()
            
            # Create execution plan
            plan = await self.planner.create_plan(request_data)
            task_state.plan = plan
            
            # Retrieve relevant knowledge
            task_state.status = "gathering_knowledge"
            task_state.updated_at = datetime.utcnow().isoformat()
            
            knowledge = await self.knowledge.retrieve_knowledge(plan)
            task_state.knowledge = knowledge
            
            # Store information in memory systems
            await asyncio.gather(
                self._store_session(task_id, task_state),
                self._store_workflow(task_id, task_state),
                self._store_knowledge(task_state)
            )
            
            # Execute plan
            task_state.status = "executing"
            task_state.updated_at = datetime.utcnow().isoformat()
            
            await self.executor.add_task(plan, knowledge)
            result = await self.executor.execute_plan(plan, knowledge)
            
            # Update final state
            task_state.status = "completed"
            task_state.result = result
            task_state.updated_at = datetime.utcnow().isoformat()
            
            # Final memory update
            await self._store_session(task_id, task_state)
            
            return {
                "task_id": task_id,
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            if 'task_id' in locals() and 'task_state' in locals():
                task_state.status = "failed"
                task_state.error = str(e)
                task_state.updated_at = datetime.utcnow().isoformat()
                await self._store_session(task_id, task_state)
                
            return {
                "task_id": task_id if 'task_id' in locals() else None,
                "status": "error",
                "error": str(e)
            }

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a task"""
        if task_id in self.tasks:
            task_state = self.tasks[task_id]
            return {
                "task_id": task_id,
                "status": task_state.status,
                "created_at": task_state.created_at,
                "updated_at": task_state.updated_at,
                "result": task_state.result,
                "error": task_state.error
            }
        return None

    async def close(self):
        """Shutdown coordinator and cleanup resources"""
        if self.initialized:
            await self.executor.close()
            self.semantic_memory.clear_cache()
            await self.model_router.shutdown()
            self.initialized = False
            logging.info("Coordinator shutdown complete")
