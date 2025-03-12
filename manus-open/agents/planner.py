class PlannerAgent:
    def __init__(self):
        self.knowledge_agent = KnowledgeAgent()

    def create_plan(self, request):
        knowledge = self.knowledge_agent.query_knowledge(request)
        plan = self.generate_plan(knowledge)
        return plan

    def generate_plan(self, knowledge):
        # Simple planning logic: return the knowledge as the plan
        return knowledge
