from typing import Dict, Any, List, Optional, Union
from memory.episodic_memory import EpisodicMemory
from memory.semantic_memory import SemanticMemory
from memory.procedural_memory import ProceduralMemory
from router.model_router import ModelRouter, ModelConfig, TaskConfig
import logging
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
import json

class KnowledgeAgent:
    """Agent responsible for knowledge retrieval and synthesis across memory systems"""
    
    def __init__(self, cache_size: int = 1000, cache_ttl: int = 3600):
        """Initialize knowledge agent with memory systems"""
        # Initialize memory systems
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Initialize model router
        self.model_router = ModelRouter()
        self._setup_model_routing()
        
        # Configure caching
        self.cache_ttl = cache_ttl
        self.knowledge_cache = lru_cache(maxsize=cache_size)(self._retrieve_knowledge_uncached)
        self.cache_timestamps: Dict[str, datetime] = {}
        
        logging.info("Knowledge agent initialized successfully")

    def _setup_model_routing(self):
        """Configure model routing for knowledge tasks"""
        # Add model configurations
        knowledge_model = ModelConfig(
            model_name="gpt-4",
            provider="openai",
            api_key="your-api-key",
            temperature=0.3,  # Lower temperature for more focused knowledge retrieval
            parameters={"top_p": 0.1}
        )
        self.model_router.add_model(knowledge_model)
        
        # Add task configurations
        knowledge_task = TaskConfig(
            task_type="knowledge_synthesis",
            required_capabilities=["knowledge_base", "reasoning"],
            priority_models=["gpt-4"],
            fallback_models=["gpt-3.5-turbo"]
        )
        self.model_router.add_task_config(knowledge_task)

    def _get_cache_key(self, plan: Dict[str, Any]) -> str:
        """Generate a cache key for a knowledge request"""
        relevant_data = {
            "task": plan.get("task"),
            "context": plan.get("context"),
            "requirements": plan.get("requirements")
        }
        return json.dumps(relevant_data, sort_keys=True)

    async def _retrieve_from_episodic(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant episodes from episodic memory"""
        try:
            # Get time range from plan
            time_window = plan.get("time_window", "24h")
            end_time = datetime.utcnow()
            
            if time_window == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_window == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=24)  # Default to 24h
                
            # Get sessions within timeframe
            sessions = await asyncio.to_thread(
                self.episodic_memory.get_sessions_by_timerange,
                start_time.isoformat(),
                end_time.isoformat()
            )
            
            return [
                {
                    "session_id": session.session_id,
                    "context": session.context,
                    "actions": session.actions,
                    "outcome": session.outcome
                }
                for session in sessions
            ]
            
        except Exception as e:
            logging.error(f"Error retrieving from episodic memory: {e}")
            return []

    async def _retrieve_from_semantic(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from semantic memory"""
        try:
            # Extract search queries from plan
            queries = []
            if task := plan.get("task"):
                queries.append(task)
            if context := plan.get("context"):
                queries.extend(context.values())
            
            results = []
            for query in queries:
                # Search semantic memory
                matches = await asyncio.to_thread(
                    self.semantic_memory.query_knowledge,
                    query,
                    n_results=5
                )
                results.extend(matches)
            
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving from semantic memory: {e}")
            return []

    async def _retrieve_from_procedural(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant workflows from procedural memory"""
        try:
            # Extract action patterns from plan
            patterns = []
            if steps := plan.get("steps"):
                patterns = [step.get("action") for step in steps if step.get("action")]
            
            if not patterns:
                return []
            
            # Find similar workflows
            workflows = await asyncio.to_thread(
                self.procedural_memory.find_similar_workflows,
                patterns,
                limit=3
            )
            
            return workflows
            
        except Exception as e:
            logging.error(f"Error retrieving from procedural memory: {e}")
            return []

    async def _synthesize_knowledge(self, 
                                  episodic_data: List[Dict[str, Any]],
                                  semantic_data: List[Dict[str, Any]],
                                  procedural_data: List[Dict[str, Any]],
                                  plan: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize knowledge from different memory systems"""
        try:
            # Prepare context for model
            context = {
                "task": plan.get("task", ""),
                "episodic_knowledge": episodic_data,
                "semantic_knowledge": semantic_data,
                "procedural_knowledge": procedural_data,
                "requirements": plan.get("requirements", {})
            }
            
            # Use model router to synthesize knowledge
            prompt = json.dumps(context, indent=2)
            response = await self.model_router.route_task(
                "knowledge_synthesis",
                prompt,
                parameters={"max_tokens": 1000}
            )
            
            if not response:
                raise ValueError("Failed to synthesize knowledge")
                
            # Parse and structure the response
            try:
                knowledge = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                knowledge = {
                    "content": response.choices[0].message.content,
                    "source": "model_synthesis"
                }
            
            return knowledge
            
        except Exception as e:
            logging.error(f"Error synthesizing knowledge: {e}")
            return {
                "error": str(e),
                "partial_data": {
                    "episodic": bool(episodic_data),
                    "semantic": bool(semantic_data),
                    "procedural": bool(procedural_data)
                }
            }

    async def _retrieve_knowledge_uncached(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and synthesize knowledge without caching"""
        try:
            # Parallel retrieval from all memory systems
            episodic_data, semantic_data, procedural_data = await asyncio.gather(
                self._retrieve_from_episodic(plan),
                self._retrieve_from_semantic(plan),
                self._retrieve_from_procedural(plan)
            )
            
            # Synthesize knowledge
            knowledge = await self._synthesize_knowledge(
                episodic_data,
                semantic_data,
                procedural_data,
                plan
            )
            
            return knowledge
            
        except Exception as e:
            logging.error(f"Error retrieving knowledge: {e}")
            return {"error": str(e)}

    async def retrieve_knowledge(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to retrieve knowledge based on a plan"""
        try:
            cache_key = self._get_cache_key(plan)
            
            # Check cache timestamp
            if cache_key in self.cache_timestamps:
                age = datetime.utcnow() - self.cache_timestamps[cache_key]
                if age.total_seconds() > self.cache_ttl:
                    self.knowledge_cache.cache_clear()
            
            # Get knowledge (either from cache or fresh)
            knowledge = await self.knowledge_cache(json.dumps(plan))
            
            # Update cache timestamp
            self.cache_timestamps[cache_key] = datetime.utcnow()
            
            return knowledge
            
        except Exception as e:
            logging.error(f"Error in knowledge retrieval: {e}")
            # Attempt uncached retrieval as fallback
            return await self._retrieve_knowledge_uncached(plan)

    def clear_cache(self):
        """Clear the knowledge cache"""
        try:
            self.knowledge_cache.cache_clear()
            self.cache_timestamps.clear()
            logging.info("Successfully cleared knowledge cache")
        except Exception as e:
            logging.error(f"Error clearing cache: {e}")

    async def update_knowledge(self, knowledge: Dict[str, Any]) -> bool:
        """Update knowledge across memory systems"""
        try:
            # Store in semantic memory
            if content := knowledge.get("content"):
                entry = {
                    "content": content,
                    "metadata": {"updated_at": datetime.utcnow().isoformat()}
                }
                await asyncio.to_thread(
                    self.semantic_memory.store_knowledge,
                    entry
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating knowledge: {e}")
            return False
