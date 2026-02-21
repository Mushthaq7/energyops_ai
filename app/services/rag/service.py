import os
import glob
import time
from typing import List, Dict, Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.llms import FakeListLLM

from app.core.metrics import MODEL_RESPONSE_TIME, MODEL_REQUESTS, DOCUMENTS_INDEXED


class RagService:
    def __init__(self, docs_dir: str = "data/documents"):
        self.docs_dir = docs_dir
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        # Placeholder for LLM. In production, use ChatOpenAI or CTransformers
        # self.llm = CTransformers(model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_type="mistral")
        self.llm = FakeListLLM(responses=["This is a simulated AI response based on the retrieved documents."])

    def load_documents(self) -> List[Document]:
        documents = []
        for file_path in glob.glob(os.path.join(self.docs_dir, "*.txt")):
            loader = TextLoader(file_path)
            doc_list = loader.load()
            for doc in doc_list:
                doc.metadata["source"] = os.path.basename(file_path)
            documents.extend(doc_list)
        return documents

    def index_documents(self):
        """Loads documents, chunks them, and creates a FAISS index."""
        docs = self.load_documents()
        if not docs:
            print("No documents found to index.")
            return

        chunks = self.text_splitter.split_documents(docs)
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        DOCUMENTS_INDEXED.inc(len(docs))
        print(f"Indexed {len(chunks)} chunks from {len(docs)} documents.")

    def query(self, query_text: str, k: int = 3) -> List[Dict]:
        """Performs similarity search and returns relevant chunks."""
        if not self.vector_store:
            self.index_documents()

        if not self.vector_store:
            return []

        start = time.perf_counter()
        results = self.vector_store.similarity_search_with_score(query_text, k=k)
        elapsed = time.perf_counter() - start
        MODEL_RESPONSE_TIME.labels(operation="retrieval").observe(elapsed)

        output = []
        for doc, score in results:
            output.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": float(score)
            })
        return output

    def ask(self, query_text: str, k: int = 3) -> Dict:
        """Retrieves context and generates an answer using LLM."""
        start_total = time.perf_counter()

        try:
            results = self.query(query_text, k)

            if not results:
                MODEL_REQUESTS.labels(operation="ask", status="success").inc()
                return {
                    "answer": "I could not find any relevant information to answer your question.",
                    "citations": []
                }

            context_str = "\n\n".join(
                [f"Source: {r['source']}\nContent: {r['content']}" for r in results]
            )

            prompt = f"""You are an expert energy operations assistant. Answer the user's question based strictly on the context provided below.

Context:
{context_str}

Question: {query_text}

Answer:"""

            # Track LLM generation time separately
            gen_start = time.perf_counter()
            answer = self.llm.invoke(prompt)
            gen_elapsed = time.perf_counter() - gen_start
            MODEL_RESPONSE_TIME.labels(operation="generation").observe(gen_elapsed)

            # Track total ask time
            total_elapsed = time.perf_counter() - start_total
            MODEL_RESPONSE_TIME.labels(operation="ask").observe(total_elapsed)
            MODEL_REQUESTS.labels(operation="ask", status="success").inc()

            return {
                "answer": answer,
                "citations": results
            }

        except Exception as e:
            MODEL_REQUESTS.labels(operation="ask", status="error").inc()
            raise

# Global instance
rag_service = RagService()
