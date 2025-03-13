import os
import pytest
import asyncio
from datetime import datetime
from router.model_router import ModelRouter, ModelConfig, TaskConfig

@pytest.mark.asyncio
class TestModelRouter:
    async def test_model_routing_and_caching(self):
        router = ModelRouter(cache_size=100)
        
        # Configure model using environment variables
        # LiteLLM handles model config based on model string
        planning_model = ModelConfig(
            model_name=os.getenv("LLM_MODEL"),  # e.g. "azure/gpt-4", "claude-2", etc.
            api_key=os.getenv("LLM_API_KEY"),
        )
        assert router.add_model(planning_model)
        
        # Configure task routing
        task_config = TaskConfig(
            task_type="planning",
            required_capabilities=["reasoning"],
            priority_models=[os.getenv("LLM_MODEL")],
            fallback_models=["openrouter/deepseek/deepseek-r1:free"]
        )
        assert router.add_task_config(task_config)
        
        # Test actual model call
        # Using litellm.completion() format
        response = await router.route_task(
            "planning",
            [{"role": "user", "content": "Create a plan to analyze a dataset with the following steps: 1. Load data 2. Clean data 3. Analyze"}],
            {"max_tokens": 500}
        )
        assert response is not None
        assert hasattr(response, "choices")
        assert len(response.choices) > 0
        assert "data" in response.choices[0].message.content.lower()
        
        # Test caching
        cached_response = await router.route_task(
            "planning",
            [{"role": "user", "content": "Create a plan to analyze a dataset with the following steps: 1. Load data 2. Clean data 3. Analyze"}],
            {"max_tokens": 500}
        )
        assert cached_response == response
        
    async def test_model_error_handling(self):
        router = ModelRouter(cache_size=100)
        
        # Test with unsupported model
        invalid_model = ModelConfig(
            model_name="unsupported-model",
            api_key=os.getenv("LLM_API_KEY")
        )
        router.add_model(invalid_model)
        
        task_config = TaskConfig(
            task_type="test",
            required_capabilities=["test"],
            priority_models=["invalid-model"],
            fallback_models=[]
        )
        router.add_task_config(task_config)
        
        # Should handle error gracefully
        response = await router.route_task(
            "test",
            [{"role": "user", "content": "This should fail"}],
            {}
        )
        assert response is None
        
    async def test_model_parameter_override(self):
        router = ModelRouter(cache_size=100)
        
        model = ModelConfig(
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
            api_key=os.getenv("LLM_API_KEY")
        )
        router.add_model(model)
        
        task_config = TaskConfig(
            task_type="override_test",
            required_capabilities=["test"],
            priority_models=[os.getenv("LLM_MODEL")],
            fallback_models=[]
        )
        router.add_model_config(task_config)
        
        # Test parameter override
        response = await router.route_task(
            "override_test",
            [{"role": "user", "content": "Test prompt"}],
            {"temperature": 0.1}  # Override default temperature
        )
        assert response is not None
        
    async def test_concurrent_requests(self):
        router = ModelRouter(cache_size=100)
        
        model = ModelConfig(
            model_name=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY")
        )
        router.add_model(model)
        
        task_config = TaskConfig(
            task_type="concurrent_test",
            required_capabilities=["test"],
            priority_models=[os.getenv("LLM_MODEL")],
            fallback_models=[]
        )
        router.add_task_config(task_config)
        
        # Test multiple concurrent requests
        tasks = [
            router.route_task(
                "concurrent_test",
                [{"role": "user", "content": f"Test prompt {i}"}],
                {}
            )
            for i in range(3)
        ]
        
        responses = await asyncio.gather(*tasks)
        assert all(response is not None for response in responses)
        assert len(set(r.choices[0].message.content for r in responses)) == 3  # Should be unique responses
