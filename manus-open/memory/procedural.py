from neo4j import GraphDatabase

class ProceduralMemory:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def store_workflow(self, workflow):
        with self.driver.session() as session:
            session.write_transaction(self._create_workflow, workflow)

    def _create_workflow(self, tx, workflow):
        query = (
            "CREATE (w:Workflow {name: $name, steps: $steps})"
        )
        tx.run(query, name=workflow['name'], steps=workflow['steps'])

    def retrieve_workflow(self, name):
        with self.driver.session() as session:
            return session.read_transaction(self._get_workflow, name)

    def _get_workflow(self, tx, name):
        query = (
            "MATCH (w:Workflow {name: $name})"
            "RETURN w"
        )
        result = tx.run(query, name=name)
        return [record["w"] for record in result]
