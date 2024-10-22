from schema.user import User_info_id, User_info, User_update
from schema.session import UserloginRequest, UserUpdateRequest
from event.user import User
from fastapi import APIRouter
router = APIRouter(prefix="/user", tags=["user"])

@router.post(
    "/create",
    summary="创建新用户",
)
async def init_session(
    body: User_info_id,
):  
    response = await User.add_user(body)
    if response['code'] == 0:
        return {"code":200, "status": "success", "message": f"user {body.user_id} created sucessfully"}
    else:
        return {"code":500, "status": "fail","message": response['message']}


@router.put(
    "/update/{user_id}",
    summary="更新用户信息",
)
async def init_session(
    user_id: str,
    body: User_update,
):  
    response = await User.update_user(user_id, body)
    if response['code'] == 0:
        if User.get_user_info(user_id):
            User.set_user_info(UserUpdateRequest(**response['message']))
        return {"code":200, "status": "success", "message": f"user {user_id} updated sucessfully"}
    else:
        return {"code":500, "status": "fail","message": response['message']}
