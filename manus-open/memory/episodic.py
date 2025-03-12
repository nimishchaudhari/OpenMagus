class EpisodicMemory:
    def store_session(self, request):
        # Simple session storage logic: return the request as the session
        return request

    def update_session(self, session, result):
        # Simple session update logic: return the result
        return result
