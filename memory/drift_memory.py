import os
import sqlitedict
import threading

class DriftMemory:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.db = sqlitedict.SqliteDict(self.db_path, autocommit=True)

    def get_last_commit(self, repo):
        with self.lock:
            return self.db.get(f"last_commit:{repo}")

    def set_last_commit(self, repo, commit):
        with self.lock:
            self.db[f"last_commit:{repo}"] = commit

    def get_api_doc_map(self, repo):
        with self.lock:
            return self.db.get(f"api_doc_map:{repo}", {})

    def set_api_doc_map(self, repo, mapping):
        with self.lock:
            self.db[f"api_doc_map:{repo}"] = mapping

    def add_execution_history(self, repo, entry):
        with self.lock:
            history = self.db.get(f"history:{repo}", [])
            history.append(entry)
            self.db[f"history:{repo}"] = history

    def get_execution_history(self, repo):
        with self.lock:
            return self.db.get(f"history:{repo}", [])
