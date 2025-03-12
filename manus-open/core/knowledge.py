class KnowledgeAgent:
    def __init__(self, semantic_memory):
        self.semantic_memory = semantic_memory

    def query_knowledge(self, task):
        # Query semantic memory for relevant information
        knowledge = self.semantic_memory.query(task)

        # Return the queried knowledge
        return knowledge
