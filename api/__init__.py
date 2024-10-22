from fastapi import APIRouter

from . import chat, knowledge, user

__all__ = ["router"]

router = APIRouter()

modules = [chat, knowledge, user]

for module in modules:
    router.include_router(module.router)
