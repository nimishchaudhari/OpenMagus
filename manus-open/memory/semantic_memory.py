class SemanticMemory:
    def __init__(self):
        self.knowledge_base = {}

    def store_knowledge(self, key, value):
        self.knowledge_base[key] = value

    def query(self, key):
        return self.knowledge_base.get(key)
