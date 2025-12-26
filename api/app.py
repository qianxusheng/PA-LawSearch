"""
Flask Application Setup
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from elasticsearch import Elasticsearch

from config import ES_PASSWORD, ES_HOST, API_HOST, API_PORT, API_DEBUG
from search.bm25_searcher import BM25Searcher
from search.dense_searcher import DenseSearcher
from search.dense_reranker import Reranker
from search.bm25_reranker import BM25Reranker
from rag.rag_service import RAGService
from api.routes import register_routes


def create_app():
    """
    Create and configure Flask application
    """
    app = Flask(__name__)
    CORS(app)

    # Single ES connection shared across all searchers
    es = Elasticsearch(
        ES_HOST,
        basic_auth=("elastic", ES_PASSWORD),
        verify_certs=False
    )

    # Lazy-loaded searchers (initialized on first use)
    searchers = {
        'bm25': None,
        'dense': None,
        'reranker': None,
        'bm25_reranker': None,
        'rag': None
    }

    def get_bm25_searcher():
        if searchers['bm25'] is None:
            searchers['bm25'] = BM25Searcher(es_client=es)
        return searchers['bm25']

    def get_dense_searcher():
        if searchers['dense'] is None:
            print("Loading dense searcher (first time)...")
            searchers['dense'] = DenseSearcher(es_client=es)
        return searchers['dense']

    def get_reranker():
        if searchers['reranker'] is None:
            print("Loading reranker (first time)...")
            searchers['reranker'] = Reranker(es_client=es)
        return searchers['reranker']

    def get_bm25_reranker():
        if searchers['bm25_reranker'] is None:
            print("Loading BM25 reranker (first time)...")
            searchers['bm25_reranker'] = BM25Reranker(es_client=es)
        return searchers['bm25_reranker']

    def get_rag_service():
        if searchers['rag'] is None:
            print("Loading RAG service (first time)...")
            searchers['rag'] = RAGService(es_client=es)
        return searchers['rag']

    # Register routes
    register_routes(app, es, get_bm25_searcher, get_dense_searcher, get_reranker, get_bm25_reranker, get_rag_service)

    return app


def run_app():
    """
    Run the Flask application
    """
    print("Starting PA Legal Case Search API...")
    print("\nEndpoints:")
    print("  GET  /cases?query=<text>&method=<bm25|dense|dense_rerank|bm25_rerank>&size=10&page=1")
    print("       - Get ranking list with specified method")
    print("  GET  /cases/<doc_id>?index=<bm25|dense>")
    print("       - Get case full details")
    print("  POST /ask")
    print("       - RAG Q&A endpoint (requires Ollama)")
    print("  GET  /health")
    print("       - Health check")
    print("\nRetrieval Methods:")
    print("  - bm25: Traditional BM25 baseline")
    print("  - dense: Dense vector retrieval (Legal-BERT dual-encoder)")
    print("  - dense_rerank: Two-stage retrieval (dense + cross-encoder reranking)")
    print("  - bm25_rerank: Two-stage retrieval (BM25 + cross-encoder reranking)")
    print("\nRAG:")
    print("  - /ask: Hybrid fusion (BM25 + Dense) retrieval + Ollama LLM generation")

    app = create_app()
    app.run(debug=API_DEBUG, host=API_HOST, port=API_PORT)


if __name__ == '__main__':
    run_app()
