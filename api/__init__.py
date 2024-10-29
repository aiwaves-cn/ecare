from fastapi import APIRouter

from . import chat

__all__ = ["router"]

router = APIRouter()

modules = [chat]

for module in modules:
    router.include_router(module.router)
