from pydantic import BaseModel, Field
from schema.user import User_info, User_update


class AnswerRequest(BaseModel):
    user_id: str = Field(description="会话ID")
    text: str = Field(description="用户回答文本", default="")

class SendMessageRequest(AnswerRequest):
    pass

class UserloginRequest(User_info):
    user_id: str = Field(description="用户ID")

class UserUpdateRequest(User_update):
    user_id: str = Field(description="用户ID")