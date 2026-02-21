from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.rag import rag_service

router = APIRouter()

class RagQueryRequest(BaseModel):
    query: str
    k: int = 3

class RagQueryResponse(BaseModel):
    query: str
    results: List[dict]
    
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    citations: List[dict]

@router.post("/query", response_model=RagQueryResponse)
def query_documents(request: RagQueryRequest):
    """
    Query the maintenance documents using RAG (Retrieval only).
    """
    try:
        results = rag_service.query(request.query, k=request.k)
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    Ask a question and get a generated answer with citations.
    """
    try:
        result = rag_service.ask(request.question)
        return {
            "question": request.question,
            "answer": result["answer"],
            "citations": result["citations"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index")
def index_documents():
    """
    Trigger re-indexing of documents.
    """
    try:
        rag_service.index_documents()
        return {"status": "indexing completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
