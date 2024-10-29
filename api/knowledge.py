import os, json
import logging
from typing import Annotated
from schema.openai import MessageData
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
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

logger = logging.getLogger(__name__)
RAW = Path(__file__).parent.parent.joinpath('knowledge/raw')
PROCESSED = Path(__file__).parent.parent.joinpath('knowledge/processed')
DB = Path(__file__).parent.parent.joinpath('knowledge/db')
# print(CHAT_HISTORY)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post(
    "/upload",
    summary="上传知识文件",
    response_model=ApiResponse,
)
async def upload_file(file: UploadFile):  
    file_path = os.path.join(RAW, os.path.basename(file.filename))
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    
    return ApiResponse(data={"message": f"{file.filename} uploaded successfully"})

@router.post(
    "/file_parse",
    summary="解析文件",
)
async def upload_file(file: str):
    source = os.path.join(RAW,os.path.basename(file))
    if not os.path.exists(source):
        raise HTTPException(status_code=404, detail="File not found")
    target = os.path.join(PROCESSED, os.path.basename(file))
    File_Parse.file_parse(source, target)
    return ApiResponse(data={"message": f"{file.filename} pa successfully"})

@router.post(
    "/db_update",
    summary="更新数据库",
)
async def updata_db():
    try:
        update_knowledge(PROCESSED, DB)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"An error occurred: {str(e)}")
    return ApiResponse(data={"message": f"knowledge updated successfully"})

@router.post(
    "/query",
    summary="数据库查询",
)
async def query_db(query:str,k:int=3):
    try:
        docs=query_and_rerank(DB, query,k)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"An error occurred: {str(e)}")
    return ApiResponse(data={"message": '\n'.join([i.page_content for i in docs])})

@router.delete("/delete/{filename}",summary="删除指定文件")
async def delete_file(filename: str):
    file_path = os.path.join(RAW, os.path.basename(filename))
    processed_file_path = os.path.join(PROCESSED, os.path.basename(filename))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(processed_file_path)
    except:
        pass

    try:
        # 删除文件
        os.remove(file_path)
        return {"filename": filename, "status": "File deleted successfully"}
    except Exception as e:
        # 如果删除过程中出现异常，返回500错误
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")

