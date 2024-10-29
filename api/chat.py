# 使用总的知识库来问答
import os, json
import logging
from typing import Annotated
from schema.openai import MessageData
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from utilswaves.authentication import get_current_user
from utilswaves.schema import ApiResponse
from pathlib import Path
from core.chat import ChatService
# from api.utils import CHAT_HISTORY
from typing import Optional, List
from schema.session import SendMessageRequest, AnswerRequest, UserloginRequest
from event.user import User, get_user
from schema.user import User_info, User_info_id
from core.jina import JinaEmbeddings

logger = logging.getLogger(__name__)
CACHED = Path(__file__).parent.parent.joinpath('cached')
print(CACHED)
# print(CHAT_HISTORY)
router = APIRouter(prefix="/chat", tags=["chat"])

CHAT_HISTORY = {}
@router.post(
    "/user_log_in",
    summary="用户登陆",
    response_model=ApiResponse[AnswerRequest],
)
async def init_session(
    body: UserloginRequest,
    user_manager: Annotated[User, Depends(get_user)]
):  
    user_id = body.user_id
    print(type(user_manager))
    if not os.path.exists(os.path.join(CACHED,str(user_id)+'.json')):
        empty_list = []
        with open(os.path.join(CACHED,str(user_id)+'.json'),'w') as f:
            json.dump(empty_list, f)
    await user_manager.set_user_info(body)
    # else:
    #     with open(os.path.join(CACHED,str(user_id)+'.json'),'r') as f:
    #         content = json.load(f)
    #         CHAT_HISTORY[user_id] = content
    # session = await history_manager.create_chat_session(current_user.user_id)
    return ApiResponse(data=AnswerRequest(user_id=user_id))


@router.post(
    "/send_msg",
    summary="发送问题，获取答案",
    response_model=ApiResponse[AnswerRequest],
)
async def send_msg(
    body: SendMessageRequest,
    user_manager: Annotated[User, Depends(get_user)]
):  
    user_id = body.user_id
    if not os.path.exists(os.path.join(CACHED,str(user_id)+'.json')):
        history = []
    else:
        with open(os.path.join(CACHED,str(user_id)+'.json'),'r') as f:
            data = f.read().strip()
            if data:
                history = json.loads(data)
            else:
                history = []
    service = ChatService()
    user_info = await user_manager.get_user_info(user_id)
    user_info = User_info_id(user_id = user_id,**user_info)
    print(user_info)
    print(type(user_info))
    ans = await service.chat(user_info=user_info, chat_history=history, text=body.text)
    history.append(f"用户：{body.text}")
    history.append(f"小XI：{ans}")
    # print(history)
    with open(os.path.join(CACHED,str(user_id)+'.json'),'w') as f:
        json.dump(history,f,ensure_ascii=False,indent=4)
    return  ApiResponse(data = AnswerRequest(user_id=body.user_id,text=ans))

@router.post(
    "/user_log_out",
    summary="用户退出",
    response_model=ApiResponse[AnswerRequest],
)
async def init_session(
    body: SendMessageRequest 
):
    user_id = body.user_id
    if len(CHAT_HISTORY[user_id]):
        with open(os.path.join(CACHED,str(user_id)+'.json'),'w') as f:
            json.dump(CHAT_HISTORY[user_id], f, ensure_ascii=False, indent=4)
    CHAT_HISTORY.pop(user_id)
    # session = await history_manager.create_chat_session(current_user.user_id)
    return ApiResponse(data=AnswerRequest(user_id=user_id))

if __name__ == '__main__':
    with open('/home/ron/xiatao/AI_character/cached/1.json','w') as f:
        pass