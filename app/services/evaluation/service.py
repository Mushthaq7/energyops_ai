import time
import mlflow
from typing import Dict, Any

class EvaluationService:
    def __init__(self, experiment_name: str = "RAG_Evaluation"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(self.experiment_name)

    def count_tokens(self, text: str) -> int:
        """
        Simple whitespace-based token counting approximation.
        In production, use tiktoken or sentencepiece.
        """
        if not text:
            return 0
        return len(text.split())

    def log_metrics(self, question: str, answer: str, latency: float, citations_count: int):
        """
        Logs metrics and parameters to MLflow.
        """
        with mlflow.start_run():
            # Log inputs/outputs
            mlflow.log_param("question", question)
            mlflow.log_text(answer, "answer.txt")
            
            # Calculate metrics
            prompt_tokens = self.count_tokens(question)
            completion_tokens = self.count_tokens(answer)
            total_tokens = prompt_tokens + completion_tokens
            
            # Log metrics
            mlflow.log_metric("latency_seconds", latency)
            mlflow.log_metric("prompt_tokens", prompt_tokens)
            mlflow.log_metric("completion_tokens", completion_tokens)
            mlflow.log_metric("total_tokens", total_tokens)
            mlflow.log_metric("citations_count", citations_count)
            
            print(f"Logged to MLflow: Latency={latency:.4f}s, Tokens={total_tokens}")

evaluation_service = EvaluationService()
