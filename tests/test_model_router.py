import os
import pytest
import asyncio
from datetime import datetime
from router.model_router import ModelRouter, ModelConfig, TaskConfig
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
class TestModelRouter:
    async def test_env_variable_parsing(self):
        # Test different LLM_MODEL formats
        test_cases = [
            {
                "model_env": "openrouter/deepseek/deepseek-v3",
                "expected_provider": "openrouter",
                "expected_model": "openrouter/deepseek/deepseek-v3"
            },
            {
                "model_env": "anthropic/claude-3-opus",
                "expected_provider": "anthropic",
                "expected_model": "anthropic/claude-3-opus"
            },
            {
                "model_env": "gpt-4",  # No provider specified
                "expected_provider": "",
                "expected_model": "gpt-4"
            }
        ]
        
        for case in test_cases:
            os.environ["LLM_MODEL"] = case["model_env"]
            os.environ["LLM_API_KEY"] = "test-api-key"

            model_config = ModelRouter.create_model_config_from_env()

            assert model_config is not None
            assert model_config.provider == case["expected_provider"]
            assert model_config.model_name == case["expected_model"]
            assert model_config.api_key == "test-api-key"

    async def test_model_config_from_env(self):
        # Set environment variables for testing
        os.environ["LLM_MODEL"] = "openrouter/deepseek/deepseek-v3"
        os.environ["LLM_API_KEY"] = "test-api-key"
        
        router = ModelRouter(cache_size=100)
        
        # The model should be auto-configured from environment variables
        # Verify the model was added correctly
        assert os.getenv("LLM_MODEL") in router.models
        
        # Verify the provider and model name were parsed correctly
        model_config = router.models[os.getenv("LLM_MODEL")]
        assert model_config.provider == "openrouter"
        assert model_config.model_name == "openrouter/deepseek/deepseek-v3"
        assert model_config.api_key == "test-api-key"
        
    async def test_direct_completion_call(self):
        # Test the _generate_completion method directly
        os.environ["LLM_MODEL"] = "openrouter/deepseek/deepseek-v3"
        os.environ["LLM_API_KEY"] = "test-api-key"
        
        router = ModelRouter(cache_size=100)
        
        # Mock the completion function
        with patch('router.model_router.completion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"

            # Set up the async mock
            future = asyncio.Future()
            future.set_result(mock_response)
            mock_completion.return_value = future

            # Call the method directly
            response = await router._generate_completion(
                "Test prompt",
                os.getenv("LLM_MODEL"),
                {"temperature": 0.7}
            )

            # Verify the call was made correctly
            mock_completion.assert_called_once()
            args, kwargs = mock_completion.call_args

            # Check that the model name and API key were passed correctly
            assert kwargs['model'] == "openrouter/deepseek/deepseek-v3"
            assert kwargs['api_key'] == "test-api-key"
            assert kwargs['messages'] == [{"role": "user", "content": "Test prompt"}]

            # Check that the response was returned correctly
            assert response == mock_response
