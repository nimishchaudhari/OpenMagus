import redis

class EpisodicMemory:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def store_session(self, session_id, data):
        self.redis_client.hmset(session_id, data)

    def retrieve_session(self, session_id):
        return self.redis_client.hgetall(session_id)

    def clear_session(self, session_id):
        self.redis_client.delete(session_id)
