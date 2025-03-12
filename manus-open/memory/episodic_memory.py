class EpisodicMemory:
    def __init__(self):
        self.sessions = {}

    def store_session(self, request):
        session_id = len(self.sessions) + 1
        self.sessions[session_id] = request
        return session_id

    def retrieve_session(self, session_id):
        return self.sessions.get(session_id)
