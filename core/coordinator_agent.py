class CoordinatorAgent:
    def __init__(self):
        self.redis_client = None

    def handle_request(self, request):
        # Simulate handling a request
        self.redis_client.set(request["task"], request["data"])
        return {"status": "task routed"}
