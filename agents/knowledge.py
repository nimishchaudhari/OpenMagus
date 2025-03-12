class KnowledgeAgent:
    def retrieve_knowledge(self, plan):
        # Implement the logic to retrieve knowledge based on the plan
        knowledge = {
            "info": plan.get("task", "example_knowledge"),
            "details": ["detail1", "detail2", "detail3"]
        }
        return knowledge
