from typing import Dict, List, Any, Optional, Union
from neo4j import GraphDatabase, Session, Transaction
import logging
from dataclasses import dataclass
from datetime import datetime
import uuid
import json

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]  # IDs of steps this step depends on
    metadata: Dict[str, Any]

@dataclass
class Workflow:
    """Represents a complete workflow sequence"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any]
    timestamp: str = None

class ProceduralMemory:
    """Neo4j-based procedural memory implementation for storing and analyzing workflows"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j",
                 password: str = "password"):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            # Verify connection
            with self.driver.session() as session:
                session.run("MATCH (n) RETURN n LIMIT 1")
            logging.info("Successfully connected to Neo4j for procedural memory")
            
            # Initialize schema constraints
            self._initialize_schema()
            
        except Exception as e:
            logging.error(f"Failed to initialize Neo4j connection: {e}")
            raise
        
    def _initialize_schema(self):
        """Initialize Neo4j schema constraints"""
        try:
            with self.driver.session() as session:
                # Create constraints for unique IDs
                session.run("""
                    CREATE CONSTRAINT workflow_id IF NOT EXISTS
                    FOR (w:Workflow) REQUIRE w.workflow_id IS UNIQUE
                """)
                session.run("""
                    CREATE CONSTRAINT step_id IF NOT EXISTS
                    FOR (s:Step) REQUIRE s.step_id IS UNIQUE
                """)
                logging.info("Successfully initialized Neo4j schema")
        except Exception as e:
            logging.error(f"Failed to initialize schema: {e}")
            raise

    def record_workflow(self, workflow: Workflow) -> bool:
        """Record a workflow and its steps in the graph database"""
        try:
            if not workflow.timestamp:
                workflow.timestamp = datetime.utcnow().isoformat()
                
            with self.driver.session() as session:
                return session.execute_write(self._create_workflow_tx, workflow)
                
        except Exception as e:
            logging.error(f"Failed to record workflow: {e}")
            return False
            
    def _create_workflow_tx(self, tx: Transaction, workflow: Workflow) -> bool:
        """Transaction function to create workflow and steps"""
        try:
            # Create workflow node
            tx.run("""
                CREATE (w:Workflow {
                    workflow_id: $workflow_id,
                    name: $name,
                    timestamp: $timestamp,
                    metadata: $metadata
                })
            """, {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "timestamp": workflow.timestamp,
                "metadata": json.dumps(workflow.metadata)
            })
            
            # Create step nodes and relationships
            for i, step in enumerate(workflow.steps):
                step_id = str(uuid.uuid4())
                
                # Create step node
                tx.run("""
                    MATCH (w:Workflow {workflow_id: $workflow_id})
                    CREATE (s:Step {
                        step_id: $step_id,
                        action: $action,
                        parameters: $parameters,
                        metadata: $metadata,
                        sequence: $sequence
                    })-[:PART_OF]->(w)
                """, {
                    "workflow_id": workflow.workflow_id,
                    "step_id": step_id,
                    "action": step.action,
                    "parameters": json.dumps(step.parameters),
                    "metadata": json.dumps(step.metadata),
                    "sequence": i
                })
                
                # Create dependency relationships
                for dep_id in step.dependencies:
                    tx.run("""
                        MATCH (s1:Step {step_id: $step_id})
                        MATCH (s2:Step {step_id: $dep_id})
                        CREATE (s1)-[:DEPENDS_ON]->(s2)
                    """, {
                        "step_id": step_id,
                        "dep_id": dep_id
                    })
                    
            return True
            
        except Exception as e:
            logging.error(f"Transaction failed: {e}")
            return False

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retrieve a complete workflow by ID"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (w:Workflow {workflow_id: $workflow_id})
                    OPTIONAL MATCH (s:Step)-[:PART_OF]->(w)
                    OPTIONAL MATCH (s)-[d:DEPENDS_ON]->(dep:Step)
                    RETURN w, collect(DISTINCT s) as steps, 
                           collect(DISTINCT {from: s.step_id, to: dep.step_id}) as dependencies
                    ORDER BY s.sequence
                """, {"workflow_id": workflow_id})
                
                record = result.single()
                if not record:
                    return None
                    
                workflow_data = record["w"]
                steps_data = record["steps"]
                dependencies = record["dependencies"]
                
                # Reconstruct workflow
                steps = []
                for step in steps_data:
                    step_deps = [d["to"] for d in dependencies if d["from"] == step["step_id"]]
                    steps.append(WorkflowStep(
                        action=step["action"],
                        parameters=json.loads(step["parameters"]),
                        dependencies=step_deps,
                        metadata=json.loads(step["metadata"])
                    ))
                
                return Workflow(
                    workflow_id=workflow_data["workflow_id"],
                    name=workflow_data["name"],
                    steps=steps,
                    metadata=json.loads(workflow_data["metadata"]),
                    timestamp=workflow_data["timestamp"]
                )
                
        except Exception as e:
            logging.error(f"Failed to retrieve workflow: {e}")
            return None

    def find_similar_workflows(self, pattern: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Find workflows with similar action patterns"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (w:Workflow)
                    MATCH (s:Step)-[:PART_OF]->(w)
                    WITH w, collect(s.action) as actions
                    WHERE ALL(action IN $pattern WHERE action IN actions)
                    RETURN w.workflow_id as id, w.name as name, 
                           w.timestamp as timestamp, w.metadata as metadata
                    LIMIT $limit
                """, {
                    "pattern": pattern,
                    "limit": limit
                })
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logging.error(f"Failed to find similar workflows: {e}")
            return []

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored workflows"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (w:Workflow)
                    OPTIONAL MATCH (s:Step)-[:PART_OF]->(w)
                    RETURN count(DISTINCT w) as workflow_count,
                           count(s) as total_steps,
                           avg(size(collect(s))) as avg_steps_per_workflow
                """)
                
                stats = result.single()
                return {
                    "total_workflows": stats["workflow_count"],
                    "total_steps": stats["total_steps"],
                    "average_steps_per_workflow": stats["avg_steps_per_workflow"]
                }
                
        except Exception as e:
            logging.error(f"Failed to get workflow statistics: {e}")
            return {}

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow and all its steps"""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (w:Workflow {workflow_id: $workflow_id})
                    OPTIONAL MATCH (s:Step)-[:PART_OF]->(w)
                    DETACH DELETE w, s
                """, {"workflow_id": workflow_id})
                
            logging.info(f"Successfully deleted workflow: {workflow_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete workflow: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all procedural memory data (use with caution)"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logging.info("Successfully cleared all procedural memory data")
            return True
        except Exception as e:
            logging.error(f"Failed to clear procedural memory: {e}")
            return False

    def close(self):
        """Close the Neo4j driver connection"""
        try:
            self.driver.close()
            logging.info("Successfully closed Neo4j connection")
        except Exception as e:
            logging.error(f"Error closing Neo4j connection: {e}")
