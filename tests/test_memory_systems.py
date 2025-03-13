import os
import pytest
import uuid
from datetime import datetime, timedelta
from memory.episodic_memory import EpisodicMemory, Session
from memory.semantic_memory import SemanticMemory, KnowledgeEntry
from memory.procedural_memory import ProceduralMemory, Workflow, WorkflowStep

@pytest.mark.asyncio
class TestEpisodicMemory:
    async def test_full_session_lifecycle(self):
        memory = EpisodicMemory(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379))
        )
        
        # Create test session
        session = Session(
            session_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            context={"task_type": "file_processing"},
            actions=[{
                "action": "read_file",
                "parameters": {"path": "test.txt"},
                "timestamp": datetime.utcnow().isoformat()
            }],
            outcome={"status": "success", "content": "test data"},
            metadata={"system": "CI"}
        )
        
        # Test storage
        stored = memory.store_session(session)
        assert stored is True
        
        # Test retrieval
        retrieved = memory.retrieve_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        
        # Test time range query
        sessions = memory.get_sessions_by_timerange(
            start_time=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
            end_time=datetime.utcnow().isoformat()
        )
        assert len(sessions) > 0
        assert any(s.session_id == session.session_id for s in sessions)

@pytest.mark.asyncio
class TestSemanticMemory:
    async def test_knowledge_storage_and_retrieval(self):
        memory = SemanticMemory(
            persist_directory="/tmp/semantic_memory_test"
        )
        
        # Create test entries
        entries = [
            KnowledgeEntry(
                content="Python is a high-level programming language",
                metadata={"category": "programming", "confidence": 0.95}
            ),
            KnowledgeEntry(
                content="Redis is an in-memory data structure store",
                metadata={"category": "databases", "confidence": 0.98}
            )
        ]
        
        # Test batch storage
        success = memory.batch_store_knowledge(entries)
        assert success is True
        
        # Test semantic search
        results = memory.query_knowledge(
            query="What is Python?",
            n_results=1
        )
        assert len(results) == 1
        assert "Python" in results[0]["content"]
        
        # Test metadata filtering
        results = memory.query_knowledge(
            query="databases",
            metadata_filter={"category": "databases"}
        )
        assert len(results) > 0
        assert "Redis" in results[0]["content"]

@pytest.mark.asyncio
class TestProceduralMemory:
    async def test_workflow_management(self):
        memory = ProceduralMemory(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password")
        )
        
        # Create test workflow
        workflow = Workflow(
            workflow_id=str(uuid.uuid4()),
            name="File Processing Workflow",
            steps=[
                WorkflowStep(
                    action="read_file",
                    parameters={"path": "input.txt"},
                    dependencies=[],
                    metadata={"type": "io"}
                ),
                WorkflowStep(
                    action="process_content",
                    parameters={"format": "json"},
                    dependencies=["read_file"],
                    metadata={"type": "processing"}
                )
            ],
            metadata={"version": "1.0"}
        )
        
        # Test workflow recording
        recorded = memory.record_workflow(workflow)
        assert recorded is True
        
        # Test workflow retrieval
        retrieved = memory.get_workflow(workflow.workflow_id)
        assert retrieved is not None
        assert retrieved.workflow_id == workflow.workflow_id
        
        # Test pattern matching
        similar = memory.find_similar_workflows(
            pattern=["read_file", "process_content"]
        )
        assert len(similar) > 0
