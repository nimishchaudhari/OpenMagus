from typing import Dict, Any, Optional, List, Union
import litellm
from litellm import completion, ModelResponse
import logging
from dataclasses import dataclass
import json
from datetime import datetime
import hashlib
import asyncio
from functools import lru_cache
import backoff
import os

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    model_name: str
    provider: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000
    parameters: Dict[str, Any] = None
    retry_count: int = 3
    timeout: int = 30

@dataclass
class TaskConfig:
    """Configuration for task-specific routing"""
    task_type: str
    required_capabilities: List[str]
    priority_models: List[str]
    fallback_models: List[str]
    parameters: Dict[str, Any] = None

class ModelRouter:
    """LiteLLM-based model router for managing model selection and interaction"""
    
    @staticmethod
    def create_model_config_from_env() -> Optional[ModelConfig]:
        """Create a ModelConfig from environment variables LLM_MODEL and LLM_API_KEY"""
        model_env = os.getenv("LLM_MODEL")
        api_key = os.getenv("LLM_API_KEY")

        if not model_env or not api_key:
            logging.warning("LLM_MODEL or LLM_API_KEY environment variables not set")
            return None

        # Split the model string to extract provider and model name
        parts = model_env.split('/', 1)

        if len(parts) < 2:
            # If no provider specified, use the model as is
            provider = ""
            model_name = model_env
        else:
            provider = parts[0]
            # For model_name, use the full string for litellm
            model_name = model_env

        return ModelConfig(
            model_name=model_name,
            provider=provider,
            api_key=api_key
        )

    def __init__(self, cache_size: int = 1000):
        """Initialize the model router with configurations"""
        self.models: Dict[str, ModelConfig] = {}
        self.task_configs: Dict[str, TaskConfig] = {}
        self.response_cache = lru_cache(maxsize=cache_size)(self._generate_completion)
        
        # Initialize LiteLLM with default settings
        litellm.set_verbose = True
        logging.info("Initialized ModelRouter with LiteLLM integration")

        # Auto-configure from environment if available
        env_model_config = self.create_model_config_from_env()
        if env_model_config:
            self.add_model(env_model_config)
            logging.info(f"Auto-configured model from environment: {env_model_config.model_name}")

    def add_model(self, model_config: ModelConfig) -> bool:
        """Add or update a model configuration"""
        try:
            self.models[model_config.model_name] = model_config
            logging.info(f"Added model configuration: {model_config.model_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to add model configuration: {e}")
            return False

    def add_task_config(self, task_config: TaskConfig) -> bool:
        """Add or update a task configuration"""
        try:
            self.task_configs[task_config.task_type] = task_config
            logging.info(f"Added task configuration: {task_config.task_type}")
            return True
        except Exception as e:
            logging.error(f"Failed to add task configuration: {e}")
            return False

    def _get_cache_key(self, prompt: str, model_name: str, parameters: Dict[str, Any]) -> str:
        """Generate a cache key for a specific request"""
        # Convert parameters to a string representation for hashing
        params_str = json.dumps(parameters, sort_keys=True) if parameters else "{}"
        key_content = f"{prompt}:{model_name}:{params_str}"
        return hashlib.sha256(key_content.encode()).hexdigest()

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _generate_completion(self, prompt_str: str, model_name: str,
                                 parameters: Dict[str, Any]) -> ModelResponse:
        """Generate completion with retry logic

        Args:
            prompt_str: String representation of the prompt (used for caching)
            model_name: Name of the model to use
            parameters: Additional parameters for the model
        """
        try:
            model_config = self.models[model_name]
            
            # Merge model config parameters with request parameters
            merged_params = {}
            if model_config.parameters:
                merged_params.update(model_config.parameters)
            if parameters:
                merged_params.update(parameters)
                
            # Add default parameters if not specified
            merged_params["temperature"] = parameters.get("temperature", model_config.temperature)
            merged_params["max_tokens"] = parameters.get("max_tokens", model_config.max_tokens)
            
            # Convert string representation back to list of messages if it looks like one
            if prompt_str.startswith("[") and "role" in prompt_str and "content" in prompt_str:
                try:
                    # Try to safely evaluate the string as a list of dicts
                    # This is just for the test cases, in production we'd use a more robust approach
                    import ast
                    messages = ast.literal_eval(prompt_str)
                except:
                    # If that fails, default to treating it as a simple string
                    messages = [{"role": "user", "content": prompt_str}]
            else:
                messages = [{"role": "user", "content": prompt_str}]

            response = await completion(
                model=model_config.model_name,
                messages=messages,
                api_key=model_config.api_key,
                timeout=model_config.timeout,
                **merged_params
            )
            
            return response
            
        except Exception as e:
            logging.error(f"Model completion failed for {model_name}: {e}")
            raise

    async def route_task(self, task_type: str, prompt: Union[str, List[Dict[str, str]]],
                        parameters: Optional[Dict[str, Any]] = None) -> Optional[ModelResponse]:
        """Route a task to appropriate model and get response

        Args:
            task_type: The type of task to route
            prompt: Either a string prompt or a list of message dictionaries in the format
                   [{"role": "user", "content": "..."}]
            parameters: Additional parameters for the model
        """
        try:
            if task_type not in self.task_configs:
                raise ValueError(f"Unknown task type: {task_type}")
                
            task_config = self.task_configs[task_type]
            parameters = parameters or {}
            
            # Convert string prompt to message format if needed
            if isinstance(prompt, str):
                formatted_prompt = [{"role": "user", "content": prompt}]
            else:
                formatted_prompt = prompt

            # Try priority models first
            for model_name in task_config.priority_models:
                if model_name not in self.models:
                    continue
                    
                try:
                    # Create a hashable representation of the prompt for caching
                    if isinstance(prompt, str):
                        prompt_str = prompt
                    else:
                        # Convert list of dicts to a stable string representation
                        prompt_str = json.dumps(formatted_prompt, sort_keys=True)

                    cache_key = self._get_cache_key(prompt_str, model_name, parameters)
                    response = await self.response_cache(prompt_str, model_name, parameters)
                    logging.info(f"Successfully routed task to model: {model_name}")
                    return response
                except Exception as e:
                    logging.warning(f"Priority model {model_name} failed: {e}")
                    continue
            
            # Try fallback models
            for model_name in task_config.fallback_models:
                if model_name not in self.models:
                    continue
                    
                try:
                    # Create a hashable representation of the prompt for caching
                    if isinstance(prompt, str):
                        prompt_str = prompt
                    else:
                        # Convert list of dicts to a stable string representation
                        prompt_str = json.dumps(formatted_prompt, sort_keys=True)

                    cache_key = self._get_cache_key(prompt_str, model_name, parameters)
                    response = await self.response_cache(prompt_str, model_name, parameters)
                    logging.info(f"Successfully routed task to fallback model: {model_name}")
                    return response
                except Exception as e:
                    logging.warning(f"Fallback model {model_name} failed: {e}")
                    continue
            
            raise Exception("All models failed for the task")
            
        except Exception as e:
            logging.error(f"Task routing failed: {e}")
            return None

    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get current status and metadata for a specific model"""
        try:
            model_config = self.models[model_name]
            return {
                "name": model_config.model_name,
                "provider": model_config.provider,
                "available": True,  # Add actual availability check if possible
                "parameters": model_config.parameters,
                "last_checked": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to get model status: {e}")
            return {}

    def get_task_routing_info(self, task_type: str) -> Dict[str, Any]:
        """Get routing information for a specific task type"""
        try:
            task_config = self.task_configs[task_type]
            return {
                "task_type": task_config.task_type,
                "capabilities": task_config.required_capabilities,
                "priority_models": [
                    {"name": m, "available": m in self.models}
                    for m in task_config.priority_models
                ],
                "fallback_models": [
                    {"name": m, "available": m in self.models}
                    for m in task_config.fallback_models
                ]
            }
        except Exception as e:
            logging.error(f"Failed to get task routing info: {e}")
            return {}

    def clear_cache(self):
        """Clear the response cache"""
        try:
            self.response_cache.cache_clear()
            logging.info("Successfully cleared model response cache")
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")

    async def shutdown(self):
        """Clean shutdown of the model router"""
        try:
            self.clear_cache()
            # Add any additional cleanup needed
            logging.info("Successfully shut down model router")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
