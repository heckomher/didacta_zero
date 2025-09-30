# Sistema de logs en MongoDB de didacta_zero
import pymongo
from datetime import datetime
import uuid
from django.conf import settings

class MongoDBLogger:
    """MongoDB logging for Didacta Calendar MVP"""
    def __init__(self):
        # Get MongoDB settings from Django settings
        mongo_settings = settings.DATABASES['mongodb']['CLIENT']
        db_name = settings.DATABASES['mongodb']['NAME']
        
        # Construct connection string with authentication
        connection_string = (
            f"mongodb://{mongo_settings['username']}:{mongo_settings['password']}"
            f"@{mongo_settings['host']}:{mongo_settings['port']}/"
            f"?authSource={mongo_settings['authSource']}"
        )
        
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db_name]
        
        # Collections
        self.system_logs = self.db.system_logs
        # Create indexes
        self._create_indexes()
    def _create_indexes(self):
        """Create indexes for better query performance"""
        self.system_logs.create_index([("timestamp", -1)])
        self.system_logs.create_index([("log_level", 1), ("timestamp", -1)])
        self.system_logs.create_index([("user_id", 1), ("timestamp", -1)])

    def log_system_event(self, level, component, operation, message,
                        user_id=None, session_id=None, metadata=None,
                        execution_time=None):
        """Log system events to MongoDB"""
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow(),
            "log_level": level.upper(),
            "component": component,
            "operation": operation,
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "execution_time": execution_time,
            "metadata": metadata or {},
            "environment": "development"  # Change based on settings
        }
        
        try:
            self.system_logs.insert_one(log_entry)
        except Exception as e:
            # Fallback to console logging
            print(f"MongoDB logging failed: {str(e)}")

# Singleton instance
_mongo_logger_instance = None

def get_mongo_logger():
    """Get or create MongoDB logger singleton"""
    global _mongo_logger_instance
    if _mongo_logger_instance is None:
        _mongo_logger_instance = MongoDBLogger()
    return _mongo_logger_instance