from fastapi import APIRouter

from . import chat, knowledge

__all__ = ["router"]

router = APIRouter()

modules = [chat, knowledge]

for module in modules:
    router.include_router(module.router)
