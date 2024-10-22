# from typing import Annotated

# from fastapi import Depends
import redis
import redis.lock
import json
from schema.session import UserloginRequest
from schema.database import Users, Messages
from schema.user import User_info_id, User_info, User_update
from .redis import Session, pool
from sqlalchemy.future import select


class User:
    
    def __init__(self) -> None:
        self.redis = redis.StrictRedis(host='localhost', port=6378, password='KY4KLoqGq6er8kTXhsuAcA==',decode_responses=True, db=1)
    
    @staticmethod
    def get_redis_key(user_id: str):
        return f"the_user_info_of_{user_id}"
        
    @staticmethod
    def get_redis_chat_history_key(user_id: str):
        return f"the_user_chat_history_of_{user_id}"

    @staticmethod
    def get_redis_lock(user_id: str):
        return f"the_lock_user_info_of_{user_id}"

    @staticmethod
    async  def add_user(user_info: User_info_id):
        async with Session() as session:
            new = Users(**user_info.dict())
            try:
                session.add(new)
                await session.commit()
                return {"code": 0}
            except Exception as e:
                await session.rollback()
                return {"code": 1, "message": str(e)}

    @staticmethod
    async  def update_user(user_id: str, user_info: User_info):
        
        async with Session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().first()
            if user is None:
                return {"code": 1, "message": f"User {user_info.user_id} not exsists"}
            update_data = user_info.dict(exclude_unset=True)
            if update_data.get('age', -1) == -1:
                update_data.pop('age')
            print(user)
            print(type(user))
            for key, value in update_data.items():
                if value:
                    setattr(user, key, value)
            try:
                user_dict = {key: value for key, value in vars(user).items() if key != "_sa_instance_state"}
                await session.commit()
                return {"code": 0, "message": user_dict}
            except Exception as e:
                await session.rollback()
                return {"code": 1, "message": str(e)}

    @staticmethod
    async def add_message(user_id: str, message: str):
        async with Session as session:
            new = Messages(user_id = user_id,
                            message = message,
                            create_time = func.now())
            try:
                session.add(new)
                await session.commit()
                return {"code": 0}
            except Exception as e:
                await session.rollback()
                return {"code": 1, "message": str(e)}
    
    @staticmethod
    async def get_message(user_id: str):
        async with Session as session:
            try:
                result = await session.execute(select(Messages).where(Messages.user_id == user_id).order_by(desc(Messages.creat_time)))
                messages = result.scalars().all()
                message = []
                for mes in messages:
                    message.append(mes.message)
                return {"code": 0, "message": message}
            except Exception as e:
                return {"code": 1, "message": str(e)}

    @staticmethod
    async def get_user_from_sql(user_id: str):
        async with Session() as session:
            result = await session.execute(select(Users).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return {"code": 1, "message": f"user {user_id} not found"}
            user_dict = {key: value for key, value in vars(user).items() if key != "_sa_instance_state"}
            return {"code": 0, "message": user_dict}
    
    @staticmethod
    async def get_user_chat_history(user_id: str, chat_history: list[str]):
        key = User.get_redis_chat_history_key(user_id)
        client = redis.Redis(connection_pool=pool)
        if not redis_client.exists(redis_key):
            return []  
        messages = redis_client.lrange(redis_key, 0, -1)
        decoded_messages = [message.decode('utf-8') for message in messages]
        return decoded_messages

    @staticmethod
    async def set_user_info(user_info: UserloginRequest):
        key = User.get_redis_key(user_info.user_id)
        # lock = self.get_redis_lock(user_info.user_id)
        client = redis.Redis(connection_pool=pool)
        response = await User.get_user_info(key)
        if response:
            for key in user_info:
                if user_info[key]:
                    response[key] = user_info[key]
        else:
            response = user_info.model_dump()
            response.pop('user_id')
        
        client.set(key, json.dumps(response))
    
    @staticmethod
    async def get_user_info(user_id: str)->dict:
        key = User.get_redis_key(user_id)
        client = redis.Redis(connection_pool=pool)
        data = client.get(key)
        if data:
            return json.loads(data)
        else:
            return data
        

def get_user():
    return User()