from typing import Dict, Any, List, Optional
from memory.episodic_memory import EpisodicMemory
from memory.semantic_memory import SemanticMemory
from memory.procedural_memory import ProceduralMemory, Workflow, WorkflowStep
from router.model_router import ModelRouter, ModelConfig, TaskConfig
import logging
import asyncio
from datetime import datetime
import json
from dataclasses import dataclass
import uuid

@dataclass
class PlanStep:
    """Represents a single step in an execution plan"""
    step_id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: int  # in seconds
    retry_policy: Dict[str, Any]

@dataclass
class Plan:
    """Represents a complete execution plan"""
    plan_id: str
    task: str
    context: Dict[str, Any]
    steps: List[PlanStep]
    requirements: Dict[str, Any]
    metadata: Dict[str, Any]
    version: str
    created_at: str

class PlannerAgent:
    """Agent responsible for creating and optimizing execution plans"""
    
    def __init__(self):
        """Initialize planner with required components"""
        # Initialize memory systems
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Initialize model router
        self.model_router = ModelRouter()
        self._setup_model_routing()
        
        logging.info("Planner agent initialized successfully")

    def _setup_model_routing(self):
        """Configure model routing for planning tasks"""
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
            task_type="task_planning",
            required_capabilities=["planning", "reasoning"],
            priority_models=["gpt-4"],
            fallback_models=["gpt-3.5-turbo"]
        )
        self.model_router.add_task_config(planning_task)

    async def _analyze_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task requirements and constraints"""
        try:
            # Prepare context for analysis
            context = {
                "task": request.get("task", ""),
                "requirements": request.get("requirements", {}),
                "constraints": request.get("constraints", {}),
                "context": request.get("context", {})
            }
            
            # Use model router for task analysis
            prompt = f"Analyze task requirements and constraints:\n{json.dumps(context, indent=2)}"
            response = await self.model_router.route_task(
                "task_planning",
                prompt,
                parameters={"max_tokens": 1000}
            )
            
            if not response:
                raise ValueError("Failed to analyze task")
                
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing task: {e}")
            return {"error": str(e)}

    async def _generate_plan_steps(self, analysis: Dict[str, Any],
                                 request: Dict[str, Any]) -> List[PlanStep]:
        """Generate detailed plan steps based on task analysis"""
        try:
            # Query procedural memory for similar workflows
            similar_workflows = await asyncio.to_thread(
                self.procedural_memory.find_similar_workflows,
                [analysis.get("task_type", "")],
                limit=3
            )
            
            # Prepare context for step generation
            context = {
                "analysis": analysis,
                "similar_workflows": similar_workflows,
                "requirements": request.get("requirements", {}),
                "constraints": request.get("constraints", {})
            }
            
            # Use model router to generate steps
            prompt = f"Generate plan steps based on analysis:\n{json.dumps(context, indent=2)}"
            response = await self.model_router.route_task(
                "task_planning",
                prompt,
                parameters={"max_tokens": 2000}
            )
            
            if not response:
                raise ValueError("Failed to generate plan steps")
                
            steps_data = json.loads(response.choices[0].message.content)
            
            # Convert to PlanStep objects
            steps = []
            for step_data in steps_data:
                step = PlanStep(
                    step_id=str(uuid.uuid4()),
                    action=step_data["action"],
                    parameters=step_data.get("parameters", {}),
                    dependencies=step_data.get("dependencies", []),
                    estimated_duration=step_data.get("estimated_duration", 300),
                    retry_policy=step_data.get("retry_policy", {
                        "max_attempts": 3,
                        "delay_seconds": 5
                    })
                )
                steps.append(step)
            
            return steps
            
        except Exception as e:
            logging.error(f"Error generating plan steps: {e}")
            return []

    async def _optimize_plan(self, steps: List[PlanStep], 
                           requirements: Dict[str, Any]) -> List[PlanStep]:
        """Optimize plan steps for efficiency"""
        try:
            # Analyze dependencies and parallelize where possible
            dependency_graph = {step.step_id: set(step.dependencies) for step in steps}
            optimized_steps = []
            processed = set()
            
            while len(processed) < len(steps):
                # Find steps that can be executed (all dependencies processed)
                available = []
                for step in steps:
                    if step.step_id not in processed and \
                       all(dep in processed for dep in step.dependencies):
                        available.append(step)
                
                if not available:
                    break  # Circular dependency or error
                
                # Sort available steps by estimated duration (longest first)
                available.sort(key=lambda x: x.estimated_duration, reverse=True)
                
                for step in available:
                    optimized_steps.append(step)
                    processed.add(step.step_id)
            
            return optimized_steps
            
        except Exception as e:
            logging.error(f"Error optimizing plan: {e}")
            return steps  # Return original steps if optimization fails

    async def _validate_plan(self, plan: Plan) -> bool:
        """Validate plan for completeness and correctness"""
        try:
            # Check for basic requirements
            if not plan.steps:
                return False
                
            # Verify all dependencies exist
            all_step_ids = {step.step_id for step in plan.steps}
            for step in plan.steps:
                if not all(dep in all_step_ids for dep in step.dependencies):
                    return False
                    
            # Check for circular dependencies
            visited = set()
            temp = set()
            
            def has_cycle(step_id: str) -> bool:
                if step_id in temp:
                    return True
                if step_id in visited:
                    return False
                    
                temp.add(step_id)
                step = next(s for s in plan.steps if s.step_id == step_id)
                
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True
                        
                temp.remove(step_id)
                visited.add(step_id)
                return False
            
            for step in plan.steps:
                if has_cycle(step.step_id):
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating plan: {e}")
            return False

    async def create_plan(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an execution plan based on the request"""
        try:
            # Analyze task
            analysis = await self._analyze_task(request)
            if "error" in analysis:
                raise ValueError(f"Task analysis failed: {analysis['error']}")
            
            # Generate plan steps
            steps = await self._generate_plan_steps(analysis, request)
            if not steps:
                raise ValueError("Failed to generate plan steps")
            
            # Optimize steps
            optimized_steps = await self._optimize_plan(steps, request.get("requirements", {}))
            
            # Create plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task=request.get("task", ""),
                context=request.get("context", {}),
                steps=optimized_steps,
                requirements=request.get("requirements", {}),
                metadata={
                    "analysis": analysis,
                    "optimization_applied": bool(optimized_steps != steps)
                },
                version="1.0",
                created_at=datetime.utcnow().isoformat()
            )
            
            # Validate plan
            if not await self._validate_plan(plan):
                raise ValueError("Plan validation failed")
            
            # Store plan in procedural memory
            workflow = Workflow(
                workflow_id=plan.plan_id,
                name=f"Plan_{plan.plan_id}",
                steps=[
                    WorkflowStep(
                        action=step.action,
                        parameters=step.parameters,
                        dependencies=step.dependencies,
                        metadata={"step_id": step.step_id}
                    )
                    for step in plan.steps
                ],
                metadata={
                    "task": plan.task,
                    "version": plan.version
                }
            )
            await asyncio.to_thread(self.procedural_memory.record_workflow, workflow)
            
            # Return serializable plan
            return {
                "plan_id": plan.plan_id,
                "task": plan.task,
                "context": plan.context,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "action": step.action,
                        "parameters": step.parameters,
                        "dependencies": step.dependencies,
                        "estimated_duration": step.estimated_duration,
                        "retry_policy": step.retry_policy
                    }
                    for step in plan.steps
                ],
                "requirements": plan.requirements,
                "metadata": plan.metadata,
                "version": plan.version,
                "created_at": plan.created_at
            }
            
        except Exception as e:
            logging.error(f"Error creating plan: {e}")
            return None

    async def update_plan(self, plan_id: str, 
                         updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing plan with new information"""
        try:
            # Retrieve existing plan from procedural memory
            workflow = await asyncio.to_thread(
                self.procedural_memory.get_workflow,
                plan_id
            )
            
            if not workflow:
                raise ValueError(f"Plan {plan_id} not found")
            
            # Apply updates and regenerate plan
            request = {
                "task": workflow.metadata.get("task", ""),
                "context": updates.get("context", {}),
                "requirements": updates.get("requirements", {}),
                "constraints": updates.get("constraints", {})
            }
            
            updated_plan = await self.create_plan(request)
            if not updated_plan:
                raise ValueError("Failed to update plan")
            
            return updated_plan
            
        except Exception as e:
            logging.error(f"Error updating plan: {e}")
            return None
