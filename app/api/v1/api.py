from fastapi import APIRouter
from app.api.v1.endpoints import energy, rag, evaluation

api_router = APIRouter()
api_router.include_router(energy.router, prefix="/energy", tags=["energy"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
