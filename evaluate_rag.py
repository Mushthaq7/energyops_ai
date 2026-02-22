import time
from app.services.rag import rag_service
from app.services.evaluation import evaluation_service

def evaluate_questions():
    test_questions = [
        "How to check oil levels?",
        "What are the solar panel cleaning procedures?",
        "How to inspect wind turbine blades?",
        "What to do if solar output is low?"
    ]

    print(f"Starting evaluation of {len(test_questions)} questions...")
    
    for question in test_questions:
        print(f"\nEvaluating: {question}")
        start_time = time.time()
        
        # Call RAG service
        result = rag_service.ask(question)
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract metrics
        answer = result["answer"]
        citations = result["citations"]
        
        # Log to MLflow
        evaluation_service.log_metrics(
            question=question,
            answer=answer,
            latency=latency,
            citations_count=len(citations)
        )
            
    print("\nEvaluation complete. Results logged to MLflow.")

if __name__ == "__main__":
    evaluate_questions()
