from threading import Lock


class SessionManager:
    _instance = None
    _lock = Lock()
    _user_sessions = {}

    # 
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    # Start new session (delete previous session if applicable)
    def start_session(self, user_id, session_id):
        # Remove any existing session for the user
        if user_id in self._user_sessions:
            self.end_session(user_id)
        else:
            self._user_sessions[user_id] = session_id
    
    # End curent session
    def end_session(self, user_id):
        if user_id in self._user_sessions:
            del self._user_sessions[user_id]
    
    # Access primary key for user session
    def get_active_session(self, user_id):
        return self._user_sessions.get(user_id)