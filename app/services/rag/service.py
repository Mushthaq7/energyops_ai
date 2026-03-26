import os
import glob
import time
import logging
from typing import List, Dict, Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.llms import FakeListLLM

from app.core.metrics import MODEL_RESPONSE_TIME, MODEL_REQUESTS, DOCUMENTS_INDEXED
from app.core.config import settings

logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = "data/faiss_index"


class _LocalLLM:
    """Runs google/flan-t5-base locally via transformers pipeline.
    Model is ~250 MB, downloaded once and cached. No API key required.
    """
    def __init__(self):
        self._pipe = None  # lazy-loaded on first call

    def _load(self):
        if self._pipe is None:
            from transformers import pipeline
            logger.info("Loading flan-t5-base locally (first call may take a moment)...")
            self._pipe = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_new_tokens=256,
            )
            logger.info("flan-t5-base loaded.")

    def invoke(self, prompt: str) -> str:
        self._load()
        result = self._pipe(prompt, max_new_tokens=256)
        return result[0]["generated_text"]


def _build_llm():
    """Always use the local flan-t5-base model. HF_TOKEN is only needed for embeddings auth."""
    logger.info("LLM: google/flan-t5-base (local, CPU)")
    return _LocalLLM()


class RagService:
    def __init__(self, docs_dir: str = "data/documents"):
        self.docs_dir = docs_dir
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.llm = _build_llm()
        # Load persisted index if available
        if os.path.exists(FAISS_INDEX_PATH):
            try:
                self.vector_store = FAISS.load_local(
                    FAISS_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True
                )
                logger.info("Loaded FAISS index from %s", FAISS_INDEX_PATH)
            except Exception as e:
                logger.warning("Could not load FAISS index: %s", e)

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
            logger.warning("No documents found to index.")
            return

        chunks = self.text_splitter.split_documents(docs)
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        DOCUMENTS_INDEXED.inc(len(docs))
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        self.vector_store.save_local(FAISS_INDEX_PATH)
        logger.info("Indexed %d chunks from %d documents. Saved to %s", len(chunks), len(docs), FAISS_INDEX_PATH)

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
