import os
import pytest
import asyncio
from datetime import datetime
from agents.coordinator import CoordinatorAgent
from agents.knowledge import KnowledgeAgent
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent, TaskStatus

@pytest.mark.asyncio
class TestAgentIntegration:
    async def test_full_system_flow(self):
        """Test full integration between all agents"""
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        try:
            # Test request
            request = {
                "task": "process_data",
                "parameters": {
                    "input": "Sample text for processing",
                    "operations": ["analyze", "summarize"]
                },
                "requirements": {
                    "max_time": 60,
                    "output_format": "json"
                }
            }
            
            # Process through coordinator
            response = await coordinator.handle_request(request)
            assert response is not None
            assert "task_id" in response
            assert response["status"] == "success"
            
            # Verify task completion
            status = await coordinator.get_task_status(response["task_id"])
            assert status is not None
            assert status["status"] in ["completed", "failed"]
            
            if status["status"] == "completed":
                assert "result" in status
                
        finally:
            await coordinator.close()

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling across agent interactions"""
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        try:
            # Test with invalid request
            invalid_request = {
                "task": "invalid_task",
                "parameters": {}
            }
            
            response = await coordinator.handle_request(invalid_request)
            assert response is not None
            assert response["status"] == "error"
            assert "error" in response
            
        finally:
            await coordinator.close()

    @pytest.mark.asyncio
    async def test_task_cancellation(self):
        """Test task cancellation"""
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        try:
            # Start a long-running task
            request = {
                "task": "long_process",
                "parameters": {
                    "duration": 10
                }
            }
            
            # Submit task
            response = await coordinator.handle_request(request)
            assert response is not None
            assert "task_id" in response
            
            # Cancel task through executor
            result = await coordinator.executor.cancel_task(response["task_id"])
            assert result is True
            
            # Verify cancelled status
            status = await coordinator.get_task_status(response["task_id"])
            assert status is not None
            assert "cancelled" in status["status"].lower()
            
        finally:
            await coordinator.close()
