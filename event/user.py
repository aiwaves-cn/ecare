# from typing import Annotated

# from fastapi import Depends
import redis
import redis.lock
import json
from schema.session import UserloginRequest


class User:
    
    def __init__(self) -> None:
        self.redis = redis.StrictRedis(host='localhost', port=6378, password='KY4KLoqGq6er8kTXhsuAcA==',decode_responses=True)
    
    @staticmethod
    def get_redis_key(user_id: str):
        return f"the_user_info_of_{user_id}"
        
    @staticmethod
    def get_redis_lock(user_id: int):
        return f"the_lock_user_info_of_{user_id}"
    
    async def set_user_info(self, user_info: UserloginRequest):
        key = self.get_redis_key(user_info.user_id)
        # lock = self.get_redis_lock(user_info.user_id)
        client = redis.StrictRedis(host='172.17.0.1', port=6378, password='KY4KLoqGq6er8kTXhsuAcA==',decode_responses=True)
        response = await self.get_user_info(key)
        if response:
            for key in user_info:
                if user_info[key]:
                    response[key] = user_info[key]
        else:
            response = user_info.model_dump()
            response.pop('user_id')
        
        client.set(key, json.dumps(response))
    
    async def get_user_info(self, user_id: int)->dict:
        key = self.get_redis_key(user_id)
        client = redis.StrictRedis(host='172.17.0.1', port=6378, password='KY4KLoqGq6er8kTXhsuAcA==',decode_responses=True)
        data = client.get(key)
        if data:
            return json.loads(data)
        else:
            return data
        

def get_user():
    
    return User()