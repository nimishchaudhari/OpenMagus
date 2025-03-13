from typing import Dict, Any, Optional, List
import json
import redis
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

@dataclass
class Session:
    """Represents a session in episodic memory"""
    session_id: str
    timestamp: str
    context: Dict[str, Any]
    actions: List[Dict[str, Any]]
    outcome: Dict[str, Any]
    metadata: Dict[str, Any]

class EpisodicMemory:
    """Redis-based episodic memory implementation for storing agent interaction sessions"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize Redis connection for episodic memory"""
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_timeout=5
            )
            self.redis.ping()  # Test connection
            logging.info("Successfully connected to Redis for episodic memory")
        except redis.ConnectionError as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise

    def _serialize_session(self, session: Session) -> str:
        """Serialize session data to JSON string"""
        try:
            return json.dumps(asdict(session))
        except Exception as e:
            logging.error(f"Failed to serialize session: {e}")
            raise

    def _deserialize_session(self, data: str) -> Optional[Session]:
        """Deserialize JSON string to Session object"""
        try:
            if not data:
                return None
            session_dict = json.loads(data)
            return Session(**session_dict)
        except Exception as e:
            logging.error(f"Failed to deserialize session: {e}")
            return None

    def store_session(self, session: Session) -> bool:
        """Store a session in Redis with timestamp indexing"""
        try:
            # Store the main session data
            key = f"session:{session.session_id}"
            session_data = self._serialize_session(session)
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Store session data
            pipe.set(key, session_data)
            
            # Store timestamp index
            timestamp_key = f"timestamp:{session.timestamp}"
            pipe.set(timestamp_key, session.session_id)
            
            # Add to session list
            pipe.zadd("sessions", {session.session_id: float(datetime.fromisoformat(session.timestamp).timestamp())})
            
            pipe.execute()
            logging.info(f"Successfully stored session {session.session_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to store session: {e}")
            return False

    def retrieve_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a specific session by ID"""
        try:
            key = f"session:{session_id}"
            data = self.redis.get(key)
            return self._deserialize_session(data) if data else None
            
        except Exception as e:
            logging.error(f"Failed to retrieve session {session_id}: {e}")
            return None

    def get_sessions_by_timerange(self, start_time: str, end_time: str) -> List[Session]:
        """Retrieve sessions within a specific time range"""
        try:
            start_ts = float(datetime.fromisoformat(start_time).timestamp())
            end_ts = float(datetime.fromisoformat(end_time).timestamp())
            
            # Get session IDs within time range
            session_ids = self.redis.zrangebyscore("sessions", start_ts, end_ts)
            
            # Retrieve each session
            sessions = []
            for sid in session_ids:
                if session := self.retrieve_session(sid):
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logging.error(f"Failed to retrieve sessions by timerange: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated indices"""
        try:
            key = f"session:{session_id}"
            
            # Get session data first to remove timestamp index
            if session_data := self.redis.get(key):
                session = self._deserialize_session(session_data)
                if session:
                    pipe = self.redis.pipeline()
                    
                    # Remove main session data
                    pipe.delete(key)
                    
                    # Remove timestamp index
                    pipe.delete(f"timestamp:{session.timestamp}")
                    
                    # Remove from session list
                    pipe.zrem("sessions", session_id)
                    
                    pipe.execute()
                    logging.info(f"Successfully deleted session {session_id}")
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to delete session {session_id}: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all episodic memory data (use with caution)"""
        try:
            self.redis.flushdb()
            logging.info("Successfully cleared all episodic memory data")
            return True
        except Exception as e:
            logging.error(f"Failed to clear episodic memory: {e}")
            return False

    def get_total_sessions(self) -> int:
        """Get total number of stored sessions"""
        try:
            return self.redis.zcard("sessions")
        except Exception as e:
            logging.error(f"Failed to get total sessions count: {e}")
            return 0
