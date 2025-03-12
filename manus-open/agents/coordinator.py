class CoordinatorAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.episodic_memory = EpisodicMemory()
        self.model_router = ModelRouter()

    def handle_request(self, request):
        session = self.episodic_memory.store_session(request)
        plan = self.planner.create_plan(request)
        result = self.model_router.route(plan)
        self.episodic_memory.update_session(session, result)
        return result
