"""
Hybrid Fusion: BM25 + Dense KNN Fusion
Combines lexical (BM25) and semantic (dense vector) search using Reciprocal Rank Fusion
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.bm25_searcher import BM25Searcher
from search.dense_searcher import DenseSearcher


class HybridFusion:
    def __init__(self, es_client=None, bm25_searcher=None, dense_searcher=None):
        """
        Initialize hybrid fusion searcher

        Args:
            es_client: Elasticsearch client instance (optional, for connection sharing)
            bm25_searcher: BM25Searcher instance
            dense_searcher: DenseSearcher instance
        """
        if bm25_searcher is None:
            self.bm25_searcher = BM25Searcher(es_client=es_client)
        else:
            self.bm25_searcher = bm25_searcher

        if dense_searcher is None:
            self.dense_searcher = DenseSearcher(es_client=es_client)
        else:
            self.dense_searcher = dense_searcher

    def reciprocal_rank_fusion(self, bm25_results, dense_results, k=60):
        """
        Reciprocal Rank Fusion (RRF) algorithm

        RRF score = sum(1 / (k + rank))

        Args:
            bm25_results: List of results from BM25
            dense_results: List of results from dense search
            k: Constant for RRF (default: 60, from original paper)

        Returns:
            List of fused results sorted by RRF score
        """
        # Build rank maps
        bm25_ranks = {doc['id']: rank + 1 for rank, doc in enumerate(bm25_results)}
        dense_ranks = {doc['id']: rank + 1 for rank, doc in enumerate(dense_results)}

        # Combine all unique document IDs
        all_doc_ids = set(bm25_ranks.keys()) | set(dense_ranks.keys())

        # Build document map for metadata
        doc_map = {}
        for doc in bm25_results:
            doc_map[doc['id']] = doc
        for doc in dense_results:
            if doc['id'] not in doc_map:
                doc_map[doc['id']] = doc

        # Calculate RRF scores
        rrf_scores = {}
        for doc_id in all_doc_ids:
            score = 0.0

            # Add BM25 contribution
            if doc_id in bm25_ranks:
                score += 1.0 / (k + bm25_ranks[doc_id])

            # Add Dense contribution
            if doc_id in dense_ranks:
                score += 1.0 / (k + dense_ranks[doc_id])

            rrf_scores[doc_id] = score

        # Sort by RRF score (descending)
        sorted_doc_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Build final results
        fused_results = []
        for doc_id, rrf_score in sorted_doc_ids:
            doc = doc_map[doc_id].copy()
            doc['rrf_score'] = rrf_score
            doc['bm25_rank'] = bm25_ranks.get(doc_id, None)
            doc['dense_rank'] = dense_ranks.get(doc_id, None)
            fused_results.append(doc)

        return fused_results

    def search(self, query, size=10, bm25_k=50, dense_k=50, rrf_k=60):
        """
        Hybrid search combining BM25 and Dense retrieval

        Args:
            query: Query string
            size: Number of final results to return
            bm25_k: Number of candidates from BM25 (default: 50)
            dense_k: Number of candidates from Dense (default: 50)
            rrf_k: RRF constant (default: 60)

        Returns:
            dict with 'total', 'results' keys
        """
        # Retrieve candidates from both methods
        bm25_response = self.bm25_searcher.search(query, size=bm25_k)
        dense_response = self.dense_searcher.search(query, size=dense_k)

        bm25_results = bm25_response.get('results', [])
        dense_results = dense_response.get('results', [])

        # Fuse results using RRF
        fused_results = self.reciprocal_rank_fusion(
            bm25_results,
            dense_results,
            k=rrf_k
        )

        # Return top-k results
        return {
            "total": len(fused_results),
            "results": fused_results[:size],
            "method": "hybrid_fusion"
        }


if __name__ == "__main__":
    print("Loading hybrid fusion searcher...")
    fusion = HybridFusion()

    query = "contract formation requirements"
    print(f"\nQuery: {query}")
    print(f"Running hybrid fusion (BM25 + Dense KNN)...")

    results = fusion.search(query, size=10)

    print(f"\nFound {results['total']} fused results")
    print(f"\nTop 10 hybrid results:")
    for i, result in enumerate(results['results'][:10], 1):
        print(f"{i}. {result['name']}")
        print(f"   RRF score: {result['rrf_score']:.4f}")
        print(f"   BM25 rank: {result['bm25_rank']}, Dense rank: {result['dense_rank']}")
