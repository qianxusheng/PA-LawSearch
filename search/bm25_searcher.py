"""
BM25 Searcher - Baseline retrieval method
"""
from config import ES_INDEX_BM25


class BM25Searcher:
    def __init__(self, es_client=None):
        """
        Args:
            es_client: Elasticsearch client instance (optional, for connection sharing)
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
        self.index_name = ES_INDEX_BM25

    def search(self, query, size=10, from_=0):
        """
        Search using BM25

        Args:
            query: Query string
            size: Number of results to return
            from_: Offset for pagination

        Returns:
            dict with 'total', 'results' keys
        """
        es_query = {
            "query": {
                "match": {"full_text": query}
            },
            "size": size,
            "from": from_,
            "_source": ["id", "name", "decision_date", "court_name",
                       "jurisdiction_name", "word_count"]
        }

        response = self.es.search(index=self.index_name, body=es_query)

        results = {
            "total": response["hits"]["total"]["value"],
            "results": []
        }

        for hit in response["hits"]["hits"]:
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


if __name__ == "__main__":
    searcher = BM25Searcher()

    query = "contract law"
    results = searcher.search(query, size=5)

    print(f"Found {results['total']} results")
    print("\nTop 5 results:")
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['name']} (score: {result['score']:.4f})")
