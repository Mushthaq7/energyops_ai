from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import time

from app.services.rag import rag_service
from app.services.evaluation import evaluation_service

router = APIRouter()

class EvaluationRequest(BaseModel):
    questions: List[str]

class EvaluationResponse(BaseModel):
    status: str
    results_logged: int

@router.post("/evaluate", response_model=EvaluationResponse)
def run_evaluation(request: EvaluationRequest):
    """
    Run evaluation on a list of questions and log metrics to MLflow.
    """
    try:
        count = 0
        for question in request.questions:
            start_time = time.time()
            result = rag_service.ask(question)
            end_time = time.time()
            latency = end_time - start_time
            
            evaluation_service.log_metrics(
                question=question,
                answer=result["answer"],
                latency=latency,
                citations_count=len(result["citations"])
            )
            count += 1
            
        return {"status": "success", "results_logged": count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
