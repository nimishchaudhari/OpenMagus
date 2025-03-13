from typing import Dict, Any, List, Optional, Set, Tuple
import asyncio
from aiohttp import ClientSession, ClientError
import logging
from dataclasses import dataclass
from datetime import datetime
import json
from memory.episodic_memory import EpisodicMemory, Session
from memory.semantic_memory import SemanticMemory, KnowledgeEntry
from memory.procedural_memory import ProceduralMemory
import traceback
import backoff
from enum import Enum
import uuid

class TaskStatus(Enum):
    """Possible states for a task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskExecution:
    """Represents a task execution instance"""
    task_id: str
    plan: Dict[str, Any]
    knowledge: Dict[str, Any]
    status: TaskStatus
    created_at: str
    updated_at: str
    current_step: Optional[str] = None
    completed_steps: Set[str] = None
    failed_steps: Dict[str, Any] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = set()
        if self.failed_steps is None:
            self.failed_steps = {}

class ExecutorAgent:
    """Agent responsible for executing plans and managing task execution"""
    
    def __init__(self):
        """Initialize executor with required components"""
        self.task_queue = asyncio.Queue()
        self.session = None
        
        # Initialize memory systems
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Task management
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.task_lock = asyncio.Lock()
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.worker_count = 0
        
        logging.info("Executor agent initialized successfully")

    async def _store_execution_record(self, task: TaskExecution):
        """Store task execution record in memory systems"""
        try:
            # Store in episodic memory
            session = Session(
                session_id=task.task_id,
                timestamp=datetime.utcnow().isoformat(),
                context={"task_type": task.plan.get("task", "unknown")},
                actions=[{
                    "step": step,
                    "status": "completed" if step in task.completed_steps else "failed",
                    "error": task.failed_steps.get(step)
                } for step in task.plan.get("steps", [])],
                outcome=task.result or {},
                metadata={
                    "status": task.status.value,
                    "error": task.error
                }
            )
            await asyncio.to_thread(self.episodic_memory.store_session, session)
            
            # Store execution knowledge in semantic memory
            if task.status == TaskStatus.COMPLETED and task.result:
                entry = KnowledgeEntry(
                    content=json.dumps({
                        "task": task.plan.get("task"),
                        "execution_pattern": list(task.completed_steps),
                        "result": task.result
                    }),
                    metadata={"task_id": task.task_id}
                )
                await asyncio.to_thread(self.semantic_memory.store_knowledge, entry)
                
        except Exception as e:
            logging.error(f"Error storing execution record: {e}")

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _execute_step(self, step: Dict[str, Any], 
                          task: TaskExecution) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Execute a single step with retry logic"""
        try:
            # Simulate step execution (replace with actual implementation)
            await asyncio.sleep(step.get("estimated_duration", 1))
            
            # Update task state
            task.current_step = step["step_id"]
            task.updated_at = datetime.utcnow().isoformat()
            
            # Execute step action based on type
            action = step["action"]
            if action.startswith("api_"):
                # Handle API calls
                url = step["parameters"].get("url")
                method = step["parameters"].get("method", "GET")
                async with self.session.request(method, url) as response:
                    response.raise_for_status()
                    result = await response.json()
            elif action.startswith("process_"):
                # Handle data processing
                data = step["parameters"].get("data")
                result = {"processed": data}  # Replace with actual processing
            else:
                # Default action handling
                result = {
                    "action": action,
                    "parameters": step["parameters"],
                    "status": "completed"
                }
            
            return True, result
            
        except ClientError as e:
            logging.error(f"API error in step {step['step_id']}: {e}")
            return False, {"error": str(e)}
        except Exception as e:
            logging.error(f"Error executing step {step['step_id']}: {e}")
            return False, {"error": str(e)}

    async def _check_dependencies(self, step: Dict[str, Any], 
                                task: TaskExecution) -> bool:
        """Check if all dependencies for a step are satisfied"""
        return all(dep in task.completed_steps for dep in step.get("dependencies", []))

    async def execute_plan(self, plan: Dict[str, Any], 
                          knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plan and manage its execution state"""
        task_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        task = TaskExecution(
            task_id=task_id,
            plan=plan,
            knowledge=knowledge,
            status=TaskStatus.PENDING,
            created_at=current_time,
            updated_at=current_time
        )
        
        try:
            # Store task in active tasks
            async with self.task_lock:
                self.active_tasks[task_id] = task
            
            # Update status to running
            task.status = TaskStatus.RUNNING
            task.updated_at = datetime.utcnow().isoformat()
            
            # Get steps from plan
            steps = plan.get("steps", [])
            total_steps = len(steps)
            step_results = {}
            
            while len(task.completed_steps) + len(task.failed_steps) < total_steps:
                # Find available steps
                available_steps = [
                    step for step in steps
                    if step["step_id"] not in task.completed_steps
                    and step["step_id"] not in task.failed_steps
                    and await self._check_dependencies(step, task)
                ]
                
                if not available_steps:
                    if len(task.completed_steps) + len(task.failed_steps) < total_steps:
                        raise ValueError("Deadlock detected in plan execution")
                    break
                
                # Execute available steps in parallel
                execution_tasks = [
                    self._execute_step(step, task)
                    for step in available_steps
                ]
                
                step_statuses = await asyncio.gather(*execution_tasks)
                
                # Process results
                for step, (success, result) in zip(available_steps, step_statuses):
                    step_id = step["step_id"]
                    if success:
                        task.completed_steps.add(step_id)
                        step_results[step_id] = result
                    else:
                        task.failed_steps[step_id] = result.get("error", "Unknown error")
                        
                        # Check retry policy
                        retry_policy = step.get("retry_policy", {})
                        max_attempts = retry_policy.get("max_attempts", 3)
                        if len(task.failed_steps) >= max_attempts:
                            raise ValueError(f"Step {step_id} failed after {max_attempts} attempts")
                
                task.updated_at = datetime.utcnow().isoformat()
            
            # Check final status
            if task.failed_steps:
                task.status = TaskStatus.FAILED
                task.error = "Some steps failed during execution"
                task.result = {
                    "completed_steps": list(task.completed_steps),
                    "failed_steps": task.failed_steps,
                    "step_results": step_results
                }
            else:
                task.status = TaskStatus.COMPLETED
                task.result = {
                    "step_results": step_results,
                    "final_state": "success"
                }
            
            # Store execution record
            await self._store_execution_record(task)
            
            return {
                "task_id": task_id,
                "status": task.status.value,
                "result": task.result,
                "error": task.error
            }
            
        except Exception as e:
            logging.error(f"Plan execution failed: {traceback.format_exc()}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            await self._store_execution_record(task)
            
            return {
                "task_id": task_id,
                "status": TaskStatus.FAILED.value,
                "error": str(e)
            }

    async def worker(self):
        """Worker process for executing tasks from the queue"""
        while True:
            try:
                plan, knowledge = await self.task_queue.get()
                result = await self.execute_plan(plan, knowledge)
                self.task_queue.task_done()
                logging.info(f"Task completed: {result}")
            except Exception as e:
                logging.error(f"Worker error: {e}")
                self.task_queue.task_done()

    async def start(self, num_workers: int):
        """Start the executor with specified number of workers"""
        self.worker_count = num_workers
        self.session = ClientSession()
        self.workers = [
            asyncio.create_task(self.worker())
            for _ in range(num_workers)
        ]
        logging.info(f"Started {num_workers} executor workers")

    async def add_task(self, plan: Dict[str, Any], knowledge: Dict[str, Any]):
        """Add a task to the execution queue"""
        await self.task_queue.put((plan, knowledge))
        logging.info(f"Task added to queue: {plan.get('task', 'unknown')}")

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status.value,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "current_step": task.current_step,
                "completed_steps": list(task.completed_steps),
                "failed_steps": task.failed_steps,
                "result": task.result,
                "error": task.error
            }
        return None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow().isoformat()
            await self._store_execution_record(task)
            return True
        return False

    async def close(self):
        """Shutdown the executor and cleanup resources"""
        try:
            # Cancel all workers
            for worker in self.workers:
                worker.cancel()
            
            # Close HTTP session
            await self.session.close()
            
            # Clear task queue
            while not self.task_queue.empty():
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            
            logging.info("Executor shutdown complete")
            
        except Exception as e:
            logging.error(f"Error during executor shutdown: {e}")
