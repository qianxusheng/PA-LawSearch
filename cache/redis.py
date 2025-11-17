import hashlib
import redis
from config import REDIS_HOST, REDIS_PORT
import json

class SearchCache:
    def __init__(self):
        self.redis = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, decode_responses = True)
    
    def get(self, query, method):
        key = hashlib.md5(f"{query}:{method}".encode()).hexdigest()
        data = self.redis.get(f"search:{method}:{key}")
        
        return json.loads(data) if data else None
    
    def set(self, query, method, results, ttl = 900):
        key = hashlib.md5(f"{query}:{method}".encode()).hexdigest()
        self.redis.setex(f"search:{method}:{key}", ttl, json.dumps(results))
        