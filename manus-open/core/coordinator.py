class CoordinatorAgent:
    def __init__(self, planner_agent, knowledge_agent, executor_agent, episodic_memory, semantic_memory, procedural_memory, model_router):
        self.planner_agent = planner_agent
        self.knowledge_agent = knowledge_agent
        self.executor_agent = executor_agent
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.procedural_memory = procedural_memory
        self.model_router = model_router

    def handle_request(self, request):
        # Store session in episodic memory
        session_id = self.episodic_memory.store_session(request)

        # Route task to planner agent
        self.planner_agent.handle_task(request, session_id)

        # Return response to user
        return {"status": "task routed", "session_id": session_id}
