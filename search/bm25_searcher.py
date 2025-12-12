"""
BM25 Searcher - Baseline retrieval method
"""
import re
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

    def search(
        self,
        query,
        size=10,
        from_=0,
        court_name=None,
        start_date=None,
        end_date=None,
    ):
        """
        Search using BM25 (multi-field with boosts + phrase handling + filters + highlight)

        Args:
            query: Query string
            size: Number of results to return
            from_: Offset for pagination
            court_name: Optional exact court name filter (keyword)
            start_date: Optional lower bound for decision_date (YYYY-MM-DD or YYYY-MM)
            end_date: Optional upper bound for decision_date

        Returns:
            dict with 'total', 'results' keys
        """
        # Extract quoted phrases: "strict liability", etc.
        phrase_terms = re.findall(r'"([^"]+)"', query)
        # Strip quote chars for the main multi_match query
        clean_query = re.sub(r'"([^"]+)"', r"\1", query).strip() or query

        # Base multi-field BM25 with boosts
        multi_match_clause = {
            "multi_match": {
                "query": clean_query,
                "type": "best_fields",
                "fields": [
                    "name^4",        # case name / style of cause
                    "parties^3",     # parties field
                    "head_matter^3", # head matter / syllabus etc.
                    "full_text^1"    # full body
                ]
            }
        }

        must_clauses = [multi_match_clause]

        # If we have explicit phrases, require at least one phrase match
        if phrase_terms:
            phrase_should = []
            for phrase in phrase_terms:
                phrase_should.append({
                    "match_phrase": {
                        "full_text": {
                            "query": phrase,
                            "slop": 1
                        }
                    }
                })
                phrase_should.append({
                    "match_phrase": {
                        "head_matter": {
                            "query": phrase,
                            "slop": 1
                        }
                    }
                })

            must_clauses.append({
                "bool": {
                    "should": phrase_should,
                    "minimum_should_match": 1
                }
            })

        # Filters (court + date range)
        filters = []

        if court_name:
            # exact match on the keyword field
            filters.append({"term": {"court_name": court_name}})

        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            filters.append({"range": {"decision_date": date_range}})

        bool_query = {"bool": {"must": must_clauses}}
        if filters:
            bool_query["bool"]["filter"] = filters

        es_query = {
            "query": bool_query,
            "size": size,
            "from": from_,
            "_source": [
                "id",
                "name",
                "decision_date",
                "court_name",
                "jurisdiction_name",
                "word_count"
            ],
            "highlight": {
                "fields": {
                    "full_text": {
                        "fragment_size": 200,
                        "number_of_fragments": 1
                    },
                    "head_matter": {
                        "fragment_size": 200,
                        "number_of_fragments": 1
                    }
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        }

        response = self.es.search(index=self.index_name, body=es_query, request_timeout=60)

        results = {
            "total": response["hits"]["total"]["value"] if "hits" in response else 0,
            "results": []
        }

        for hit in response["hits"]["hits"]:
            doc = hit["_source"]
            highlight = hit.get("highlight", {})
            snippet = None

            if "full_text" in highlight:
                snippet = highlight["full_text"][0]
            elif "head_matter" in highlight:
                snippet = highlight["head_matter"][0]

            results["results"].append({
                "id": doc.get("id"),
                "score": hit["_score"],
                "name": doc.get("name"),
                "decision_date": doc.get("decision_date"),
                "court_name": doc.get("court_name"),
                "jurisdiction_name": doc.get("jurisdiction_name"),
                "word_count": doc.get("word_count"),
                "snippet": snippet,
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
