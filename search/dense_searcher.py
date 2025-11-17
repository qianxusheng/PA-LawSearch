"""
Dense Vector Searcher using Legal-BERT
Coarse-grained retrieval using semantic search
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ES_INDEX_DENSE, TOP_K_RERANK
from models.dual_encoder import DualEncoder


class DenseSearcher:
    def __init__(self, es_client=None, encoder=None):
        """
        Initialize dense searcher

        Args:
            es_client: Elasticsearch client instance (optional, for connection sharing)
            encoder: DualEncoder instance, creates new one if None
        """
        if es_client is None:
            from elasticsearch import Elasticsearch
            from config import ES_PASSWORD, ES_HOST
            self.es = Elasticsearch(
                ES_HOST,
                basic_auth=("elastic", ES_PASSWORD),
                verify_certs=False
            )
        else:
            self.es = es_client
        self.index_name = ES_INDEX_DENSE
        self.encoder = encoder or DualEncoder()

    def search(self, query, size=10, from_=0):
        """
        Search using dense vectors (KNN with application-layer pagination)
        Limited to top 1000 results for performance

        Args:
            query: Query string
            size: Number of results to return per page
            from_: Offset for pagination

        Returns:
            dict with 'total', 'results' keys
        """
        query_vector = self.encoder.encode_query(query).tolist()

        # Use KNN to retrieve top 1000 results, then paginate in application layer
        es_query = {
            "size": 1000,  # Must set size to actually return k results
            "knn": {
                "field": "dense_vector",
                "query_vector": query_vector,
                "k": 1000,  # Find top 1000 nearest neighbors
                "num_candidates": 5000,  # Explore 5000 candidates for better accuracy
                "filter": {
                    "range": {
                        "word_count": {
                            "gte": 100  # Filter out short documents (ORDERs, docket entries)
                        }
                    }
                }
            },
            "_source": ["id", "name", "decision_date", "court_name",
                       "jurisdiction_name", "word_count"]
        }

        response = self.es.search(index=self.index_name, body=es_query)

        # Get all hits returned by KNN (up to k=1000)
        all_hits = response["hits"]["hits"]
        total_available = len(all_hits)

        results = {
            "total": total_available,  # Total available (max 1000)
            "results": []
        }

        # Paginate: slice from from_ to from_ + size
        paginated_hits = all_hits[from_:from_ + size]

        for hit in paginated_hits:
            doc = hit["_source"]
            results["results"].append({
                "id": doc.get("id"),
                "score": hit["_score"],
                "name": doc.get("name"),
                "decision_date": doc.get("decision_date"),
                "court_name": doc.get("court_name"),
                "jurisdiction_name": doc.get("jurisdiction_name"),
                "word_count": doc.get("word_count")
            })

        return results

    def get_document_by_id(self, doc_id):
        """
        Get full document by ID

        Args:
            doc_id: Document ID

        Returns:
            dict with document data or None if not found
        """
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {"term": {"id": doc_id}},
                "size": 1
            }
        )

        if response["hits"]["total"]["value"] == 0:
            return None

        return response["hits"]["hits"][0]["_source"]

    def search_with_full_text(self, query, size=TOP_K_RERANK):
        """
        Search and return results with full_text for reranking

        Args:
            query: Query string
            size: Number of candidates to retrieve (default: TOP_K_RERANK)

        Returns:
            list of dicts with full document data
        """
        query_vector = self.encoder.encode_query(query).tolist()

        es_query = {
            "size": size,
            "knn": {
                "field": "dense_vector",
                "query_vector": query_vector,
                "k": size,
                "num_candidates": size * 5,
                "filter": {
                    "range": {
                        "word_count": {
                            "gte": 100  # Filter out short documents (ORDERs, docket entries)
                        }
                    }
                }
            },
            "_source": ["id", "name", "decision_date", "court_name",
                       "jurisdiction_name", "word_count", "full_text"]
        }

        response = self.es.search(index=self.index_name, body=es_query)

        results = []
        for hit in response["hits"]["hits"]:
            doc = hit["_source"]
            doc["_score"] = hit["_score"]
            results.append(doc)

        return results


if __name__ == "__main__":
    print("Loading dense searcher...")
    searcher = DenseSearcher()

    query = "contract formation requirements"
    results = searcher.search(query, size=5)

    print(f"\nFound {results['total']} results")
    print("\nTop 5 results:")
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['name']} (score: {result['score']:.4f})")
