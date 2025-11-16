"""
Reranker using Cross-Encoder
Fine-grained reranking stage after coarse retrieval
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cross_encoder import CrossEncoder
from search.dense_searcher import DenseSearcher
from config import TOP_K_RERANK


class Reranker:
    def __init__(self, es_client=None, dense_searcher=None, cross_encoder=None):
        """
        Initialize reranker

        Args:
            es_client: Elasticsearch client instance (optional, for connection sharing)
            dense_searcher: DenseSearcher instance for coarse retrieval
            cross_encoder: CrossEncoder instance for reranking
        """
        if dense_searcher is None:
            self.dense_searcher = DenseSearcher(es_client=es_client)
        else:
            self.dense_searcher = dense_searcher
        self.cross_encoder = cross_encoder or CrossEncoder()

    def search_and_rerank(self, query, top_k_retrieval=TOP_K_RERANK,
                          top_k_rerank=None):
        """
        Two-stage retrieval: coarse retrieval + fine-grained reranking

        Args:
            query: Query string
            top_k_retrieval: Number of candidates from dense retrieval
            top_k_rerank: Number of final results to return (None = return all ranked)

        Returns:
            dict with 'total', 'results' keys
        """
        candidates = self.dense_searcher.search_with_full_text(
            query, size=top_k_retrieval
        )

        if not candidates:
            return {"total": 0, "results": []}

        documents = [doc.get("full_text", "")[:2000] for doc in candidates]
        ranked_indices_scores = self.cross_encoder.rerank(query, documents)

        results = {
            "total": len(candidates),
            "results": []
        }

        limit = top_k_rerank if top_k_rerank is not None else len(ranked_indices_scores)
        for idx, score in ranked_indices_scores[:limit]:
            doc = candidates[idx]
            results["results"].append({
                "id": doc.get("id"),
                "score": float(score),
                "dense_score": doc.get("_score"),
                "name": doc.get("name"),
                "decision_date": doc.get("decision_date"),
                "court_name": doc.get("court_name"),
                "jurisdiction_name": doc.get("jurisdiction_name"),
                "word_count": doc.get("word_count")
            })

        return results


if __name__ == "__main__":
    print("Loading reranker...")
    reranker = Reranker()

    query = "contract formation requirements"
    print(f"\nQuery: {query}")
    print(f"Retrieving top {TOP_K_RERANK} candidates...")

    results = reranker.search_and_rerank(query, top_k_rerank=5)

    print(f"\nFound {results['total']} candidates")
    print(f"\nTop 5 after reranking:")
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['name']}")
        print(f"   Rerank score: {result['score']:.4f}, Dense score: {result['dense_score']:.4f}")
