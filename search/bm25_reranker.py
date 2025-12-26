"""
BM25 + Cross-Encoder Reranker
Two-stage retrieval: BM25 coarse retrieval + Cross-encoder reranking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cross_encoder import CrossEncoder
from search.bm25_searcher import BM25Searcher
from config import TOP_K_RERANK, ES_INDEX_BM25


class BM25Reranker:
    def __init__(self, es_client=None, bm25_searcher=None, cross_encoder=None):
        """
        Initialize BM25 + Cross-encoder reranker

        Args:
            es_client: Elasticsearch client instance (optional, for connection sharing)
            bm25_searcher: BM25Searcher instance for coarse retrieval
            cross_encoder: CrossEncoder instance for reranking
        """
        if bm25_searcher is None:
            self.bm25_searcher = BM25Searcher(es_client=es_client)
        else:
            self.bm25_searcher = bm25_searcher
        self.cross_encoder = cross_encoder or CrossEncoder()
        self.es = es_client or self.bm25_searcher.es
        self.index_name = ES_INDEX_BM25

    def search_with_full_text(self, query, size=100):
        """
        Get BM25 candidates with full_text for reranking

        Args:
            query: Query string
            size: Number of candidates to retrieve

        Returns:
            list of documents with full_text
        """
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "type": "best_fields",
                    "fields": [
                        "name^4",
                        "parties^3",
                        "head_matter^3",
                        "full_text^1"
                    ]
                }
            },
            "size": size,
            "_source": [
                "id", "name", "decision_date", "court_name",
                "jurisdiction_name", "word_count", "full_text"
            ]
        }

        response = self.es.search(index=self.index_name, body=es_query, request_timeout=60)

        candidates = []
        for hit in response["hits"]["hits"]:
            doc = hit["_source"]
            doc["_score"] = hit["_score"]  # Keep BM25 score
            candidates.append(doc)

        return candidates

    def search_and_rerank(self, query, top_k=TOP_K_RERANK):
        """
        Two-stage retrieval: BM25 coarse retrieval + Cross-encoder reranking

        Args:
            query: Query string
            top_k: Number of candidates to retrieve and rerank (default: TOP_K_RERANK)

        Returns:
            dict with 'total', 'results' keys
        """
        # Stage 1: Retrieve top_k candidates using BM25
        candidates = self.search_with_full_text(query, size=top_k)

        if not candidates:
            return {"total": 0, "results": []}

        # Stage 2: Rerank all candidates with Cross-encoder
        documents = [doc.get("full_text", "")[:2000] for doc in candidates]
        ranked_indices_scores = self.cross_encoder.rerank(query, documents)

        results = {
            "total": len(candidates),
            "results": []
        }

        # Return all reranked results
        for idx, score in ranked_indices_scores:
            doc = candidates[idx]
            results["results"].append({
                "id": doc.get("id"),
                "score": float(score),  # Cross-encoder score
                "bm25_score": doc.get("_score"),  # Original BM25 score
                "name": doc.get("name"),
                "decision_date": doc.get("decision_date"),
                "court_name": doc.get("court_name"),
                "jurisdiction_name": doc.get("jurisdiction_name"),
                "word_count": doc.get("word_count")
            })

        return results


if __name__ == "__main__":
    print("Loading BM25 + Cross-encoder reranker...")
    reranker = BM25Reranker()

    query = "contract formation requirements"
    print(f"\nQuery: {query}")
    print(f"Retrieving and reranking top {TOP_K_RERANK} BM25 candidates...")

    results = reranker.search_and_rerank(query, top_k=TOP_K_RERANK)

    print(f"\nFound {results['total']} candidates")
    print(f"\nTop 5 after reranking:")
    for i, result in enumerate(results['results'][:5], 1):
        print(f"{i}. {result['name']}")
        print(f"   Rerank score: {result['score']:.4f}, BM25 score: {result['bm25_score']:.4f}")
