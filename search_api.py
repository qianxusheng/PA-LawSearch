from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app)

## TODO: the Elasticsearch server should be moved to CRC server maybe
## TODO: determined definition of API interface

# Connect to Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "0=ej+ZeERilvX9QENqYQ"),
    verify_certs=False
)

index_name = "legal_cases_test"


@app.route('/cases', methods=['GET'])
def get_cases():
    """
    Get ranking list of cases based on query

    Query params:
        query: search text (required)
        size: number of results (default 10)
        page: page number starting from 1 (default 1)

    Example: GET /cases?query=murder&size=10&page=1

    Response:
    {
        "total": 150,
        "page": 1,
        "size": 10,
        "results": [
            {
                "id": "12121253",
                "score": 8.5432,
                "name": "Pennsylvania v. Susanna M'Kee",
                "decision_date": "1791-09",
                "court_name": "Allegheny County Court",
                "jurisdiction_name": "Pa.",
                "word_count": 3462
            }
        ]
    }
    """
    try:
        query_text = request.args.get("query", "")
        size = int(request.args.get("size", 10)) 
        page = int(request.args.get("page", 1))
        from_ = (page - 1) * size

        if not query_text:
            return jsonify({"error": "query parameter is required"}), 400

        # Build ES query
        es_query = {
            "query": {
                "match": {"full_text": query_text}
            },
            "size": size,
            "from": from_,
            "_source": ["id", "name", "decision_date", "court_name", "jurisdiction_name", "word_count"]
        }

        # Execute search
        response = es.search(index=index_name, body=es_query)

        # Format results - only return ranking list, no full_text
        results = {
            "total": response["hits"]["total"]["value"],
            "page": page,
            "size": size,
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

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cases/<doc_id>', methods=['GET'])
def get_case_detail(doc_id):
    """
    Get full case details including HTML/full_text by ID

    Example: GET /cases/12121253

    Response:
    {
        "id": "12121253",
        "name": "Pennsylvania v. Susanna M'Kee",
        "decision_date": "1791-09",
        "court_name": "Allegheny County Court",
        "jurisdiction_name": "Pa.",
        "parties": "Pennsylvania, Susanna M'Kee",
        "judges": "Judge Smith",
        "word_count": 3462,
        "full_text": "..."
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
            return jsonify({"error": "Case not found"}), 404

        doc = response["hits"]["hits"][0]["_source"]
        return jsonify(doc), 200

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
    print("Starting PA Legal Case Search API...")
    print("Endpoints:")
    print("  GET  /cases?query=<text>&size=10&page=1 - Get ranking list")
    print("  GET  /cases/<doc_id> - Get case full details")
    print("  GET  /health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
