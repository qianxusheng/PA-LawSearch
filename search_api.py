from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)

## TODO: the Elasticsearch server should be moved to CRC server maybe
## TODO: determined definition of API interface

# Connect to Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "0=ej+ZeERilvX9QENqYQ"),
    verify_certs=False
)

index_name = "legal_cases_test"


@app.route('/search', methods=['POST'])
def search():
    """
    Search API with Query + Filters

    Request Body:
    {
        "query": "murder evidence",
        "filters": {
            "court_name": "Pennsylvania High Court",
            "jurisdiction_name": "Pa.",
            "decision_date_from": "1790",
            "decision_date_to": "1800",
            "word_count_min": 1000,
            "word_count_max": 5000
        },
        "size": 100,
        "from": 0
    }

    Response:
    {
        "total": 150,
        "hits": [
            {
                "doc_id": "12121253",
                "score": 8.5432,
                "name": "Pennsylvania v. Susanna M'Kee",
                "decision_date": "1791-09",
                "court_name": "Allegheny County Court",
                "jurisdiction_name": "Pa.",
                "word_count": 3462,
                "full_text": "..."
            }
        ]
    }
    """
    try:
        data = request.json
        query_text = data.get("query", "")
        filters = data.get("filters", {})
        size = data.get("size", 100)
        from_ = data.get("from", 0)

        # Build ES query
        es_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "size": size,
            "from": from_
        }

        # Query part
        if query_text:
            es_query["query"]["bool"]["must"].append({
                "match": {"full_text": query_text}
            })
        else:
            es_query["query"]["bool"]["must"].append({"match_all": {}})

        # Filter part - keyword fields
        keyword_filters = [
            "court_name", "court_abbreviation",
            "jurisdiction_name", "jurisdiction_name_long",
            "opinion_type", "opinion_author",
            "provenance_source", "provenance_batch",
            "citation_type", "docket_number"
        ]

        for field in keyword_filters:
            if field in filters and filters[field]:
                es_query["query"]["bool"]["filter"].append({
                    "term": {field: filters[field]}
                })

        # Date range filter
        if "decision_date_from" in filters or "decision_date_to" in filters:
            date_range = {}
            if "decision_date_from" in filters:
                date_range["gte"] = filters["decision_date_from"]
            if "decision_date_to" in filters:
                date_range["lte"] = filters["decision_date_to"]
            es_query["query"]["bool"]["filter"].append({
                "range": {"decision_date": date_range}
            })

        # Numeric range filters
        numeric_ranges = {
            "word_count": ("word_count_min", "word_count_max"),
            "char_count": ("char_count_min", "char_count_max"),
            "pagerank_percentile": ("pagerank_min", "pagerank_max")
        }

        for field, (min_key, max_key) in numeric_ranges.items():
            if min_key in filters or max_key in filters:
                range_filter = {}
                if min_key in filters:
                    range_filter["gte"] = filters[min_key]
                if max_key in filters:
                    range_filter["lte"] = filters[max_key]
                es_query["query"]["bool"]["filter"].append({
                    "range": {field: range_filter}
                })

        # Execute search
        response = es.search(index=index_name, body=es_query)

        # Format results
        results = {
            "total": response["hits"]["total"]["value"],
            "took": response["took"],
            "hits": []
        }

        for hit in response["hits"]["hits"]:
            doc = hit["_source"]
            results["hits"].append({
                "doc_id": doc.get("id"),
                "score": hit["_score"],
                "name": doc.get("name"),
                "decision_date": doc.get("decision_date"),
                "court_name": doc.get("court_name"),
                "jurisdiction_name": doc.get("jurisdiction_name"),
                "word_count": doc.get("word_count"),
                "parties": doc.get("parties"),
                "judges": doc.get("judges"),
                "full_text": doc.get("full_text")
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/retrieve', methods=['POST'])
def retrieve():
    """
    Simple retrieve API - returns top K documents for a query

    Request Body:
    {
        "query": "murder evidence",
        "top_k": 100
    }

    Response:
    {
        "query": "murder evidence",
        "total": 150,
        "retrieved": 100,
        "results": [
            {
                "doc_id": "12121253",
                "score": 8.5432
            }
        ]
    }
    """
    try:
        data = request.json
        query_text = data.get("query", "")
        top_k = data.get("top_k", 100)

        if not query_text:
            return jsonify({"error": "query is required"}), 400

        # Simple match query
        response = es.search(
            index=index_name,
            body={
                "query": {"match": {"full_text": query_text}},
                "size": top_k,
                "_source": ["id"]
            }
        )

        results = {
            "query": query_text,
            "total": response["hits"]["total"]["value"],
            "retrieved": len(response["hits"]["hits"]),
            "results": [
                {
                    "doc_id": hit["_source"]["id"],
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        }

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_doc/<doc_id>', methods=['GET'])
def get_doc(doc_id):
    """
    Get a specific document by ID

    Response:
    {
        "doc_id": "12121253",
        "name": "Pennsylvania v. Susanna M'Kee",
        "decision_date": "1791-09",
        "full_text": "...",
        ...
    }
    """
    try:
        response = es.search(
            index=index_name,
            body={
                "query": {"term": {"id": doc_id}},
                "size": 1
            }
        )

        if response["hits"]["total"]["value"] == 0:
            return jsonify({"error": "Document not found"}), 404

        doc = response["hits"]["hits"][0]["_source"]
        return jsonify(doc), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/filters/values', methods=['GET'])
def get_filter_values():
    """
    Get all possible values for a filter field

    Query: ?field=court_name

    Response:
    {
        "field": "court_name",
        "values": ["Pennsylvania High Court", "Allegheny County Court", ...],
        "count": 25
    }
    """
    try:
        field = request.args.get("field")
        if not field:
            return jsonify({"error": "field parameter is required"}), 400

        response = es.search(
            index=index_name,
            body={
                "size": 0,
                "aggs": {
                    "unique_values": {
                        "terms": {"field": field, "size": 1000}
                    }
                }
            }
        )

        buckets = response["aggregations"]["unique_values"]["buckets"]
        values = [bucket["key"] for bucket in buckets]

        return jsonify({
            "field": field,
            "values": values,
            "count": len(values)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    try:
        es.ping()
        stats = es.count(index=index_name)
        return jsonify({
            "status": "healthy",
            "elasticsearch": "connected",
            "total_documents": stats["count"]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("Starting Search API...")
    print("Endpoints:")
    print("  POST /search - Query + Filters search")
    print("  POST /retrieve - Simple retrieval (for ranking)")
    print("  GET  /get_doc/<doc_id> - Get document by ID")
    print("  GET  /filters/values?field=<field_name> - Get filter values")
    print("  GET  /health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
