from chromadb import ChromaDB

class SemanticMemory:
    def __init__(self):
        self.chroma_db = ChromaDB()

    def store_knowledge(self, knowledge):
        self.chroma_db.store(knowledge)

    def retrieve_knowledge(self, query):
        return self.chroma_db.search(query)
