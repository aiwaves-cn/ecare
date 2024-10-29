import os, json
import logging
from typing import Annotated
from schema.openai import MessageData
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from starlette.responses import StreamingResponse
from utilswaves.authentication import get_current_user
from utilswaves.schema import ApiResponse
from pathlib import Path
from core.chat import ChatService
# from api.utils import CHAT_HISTORY
from typing import Optional, List
from schema.session import SendMessageRequest, AnswerRequest, UserloginRequest
from event.user import User, get_user
from schema.user import User_info
from core.jina import JinaEmbeddings
from core.knowledge import File_Parse, update_knowledge, query_and_rerank
from pydantic import BaseModel
logger = logging.getLogger(__name__)
RAW = Path(__file__).parent.parent.joinpath('file/knowledge/raw')
PROCESSED = Path(__file__).parent.parent.joinpath('file/knowledge/processed')
DB = Path(__file__).parent.parent.joinpath('file/knowledge/db')
# print(CHAT_HISTORY)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])
class SearchRequest(BaseModel):
    query: str
    k: int = 3

@router.post(
    "/upload",
    summary="上传知识文件",
)
async def upload_file(file: UploadFile = File(...), id:str = Form(...)):  
    _, file_extension = os.path.splitext(file.filename)
    file_path = RAW.joinpath(os.path.basename(id + file_extension))
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    target = PROCESSED.joinpath(os.path.basename(id+'.txt'))
    File_Parse.file_parse(file_path, target)
    return {"code": 200, "status": "success","message": f"{file.filename} uploaded and parsed successfully"}

# @router.post(
#     "/file_parse",
#     summary="解析文件",
# )
# async def file_parse(file: str):
#     source = RAW.joinpath(os.path.basename(file))
#     if not os.path.exists(source):
#         raise HTTPException(status_code=404, detail="File not found")
#     target = PROCESSED.joinpath(os.path.basename(file.split('.')[0]+'.txt'))
#     File_Parse.file_parse(source, target)
#     return ApiResponse(data={"message": f"{file} parsed successfully"})

@router.post(
    "/db_update",
    summary="更新数据库",
)
async def updata_db():
    try:
        update_knowledge(PROCESSED, DB)
    except Exception as e:
        return {"code": 500, "status": "fail","message": f"An error occurred: {str(e)}"} 
    return {"code": 200, "status": "success","message": f"knowledge updated successfully"} 

@router.post(
    "/search",
    summary="数据库查询",
)
async def query_db(request: SearchRequest):
    query = request.query
    k = request.k
    try:
        docs=query_and_rerank(DB, query, k)
    except Exception as e:
        return {"code": 500, "status": "fail","message": f"An error occurred: {str(e)}"} 
    return {"code": 200, "status": "success","message": '\n'.join([i.page_content for i in docs])} 

@router.delete("/{id}",summary="删除指定文件")
async def delete_file(id: str):
    file_path = os.path.join(RAW, os.path.basename(id))
    processed_file_path = os.path.join(PROCESSED, os.path.basename(id)+'.txt')
    print("文件名:", id)
    print("文件路径:", file_path)
    if not os.path.exists(processed_file_path):
        return {"code": 404, "status": "fail","message": "File not found"} 
    try:
        os.remove(file_path+'.txt')
    except:
        pass
    try:
        os.remove(file_path+'.docx')
    except:
        pass

    try:
        # 删除文件
        os.remove(processed_file_path)
        return {"code": 200, "status": "success","message": f"File {id} deleted successfully"} 
    except Exception as e:
        # 如果删除过程中出现异常，返回500错误
        return {"code": 500, "status": "fail","message": f"File deletion failed: {str(e)}"} 