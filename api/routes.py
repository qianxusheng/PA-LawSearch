"""
API Routes for Legal Case Search
"""
from flask import request, jsonify
from config import ES_INDEX_BM25, ES_INDEX_DENSE, TOP_K_RERANK
from cache.redis import SearchCache 

def register_routes(app, es, get_bm25_searcher, get_dense_searcher, get_reranker, get_bm25_reranker):
    """
    Register all API routes

    Args:
        app: Flask application instance
        es: Elasticsearch client
        get_bm25_searcher: Function to get BM25 searcher
        get_dense_searcher: Function to get dense searcher
        get_reranker: Function to get reranker
    """
    cache = SearchCache()
    @app.route('/cases', methods=['GET'])
    def get_cases():
        """
        Get ranking list of cases based on query

        Query params:
            query: search text (required)
            method: retrieval method - 'bm25', 'dense', or 'dense_rerank' (default: 'bm25')
            size: number of results (default 10)
            page: page number starting from 1 (default 1)

        Examples:
            GET /cases?query=murder&method=bm25&size=10&page=1
            GET /cases?query=contract&method=dense&size=10
            GET /cases?query=contract&method=dense_rerank&size=10

        Response:
        {
            "total": 150,
            "page": 1,
            "size": 10,
            "method": "bm25",
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
            method = request.args.get("method", "bm25").lower()
            size = int(request.args.get("size", 10))
            page = int(request.args.get("page", 1))

            court_name = request.args.get("court", "").strip() or None
            start_date = request.args.get("start_date") or None
            end_date = request.args.get("end_date") or None


            if not query_text:
                return jsonify({"error": "query parameter is required"}), 400

            if method not in ["bm25", "dense", "dense_rerank", "bm25_rerank"]:
                return jsonify({"error": "method must be 'bm25', 'dense', 'dense_rerank', or 'bm25_rerank'"}), 400

            if method == "bm25":
                searcher = get_bm25_searcher()
                from_ = (page - 1) * size
                results = searcher.search(
                    query_text,
                    size=size,
                    from_=from_,
                    court_name=court_name,
                    start_date=start_date,
                    end_date=end_date,
                )
                results["page"] = page
                results["size"] = size
                results["method"] = "bm25"

            elif method == "dense":
                searcher = get_dense_searcher()
                from_ = (page - 1) * size
                results = searcher.search(query_text, size=size, from_=from_)
                results["page"] = page
                results["size"] = size
                results["method"] = "dense"

            elif method == "dense_rerank":
                cached = cache.get(query_text, method)
                if cached:
                    all_results = cached
                else:
                    ranker = get_reranker()
                    all_results = ranker.search_and_rerank(query_text, top_k=TOP_K_RERANK)
                    cache.set(query_text, method, all_results)

                start = (page - 1) * size
                end = start + size

                results = {
                    "total": all_results["total"],
                    "results": all_results["results"][start:end],
                    "page": page,
                    "size": size,
                    "method": "dense_rerank"
                }

            elif method == "bm25_rerank":
                cached = cache.get(query_text, method)
                if cached:
                    all_results = cached
                else:
                    ranker = get_bm25_reranker()
                    all_results = ranker.search_and_rerank(query_text, top_k=TOP_K_RERANK)
                    cache.set(query_text, method, all_results)

                start = (page - 1) * size
                end = start + size

                results = {
                    "total": all_results["total"],
                    "results": all_results["results"][start:end],
                    "page": page,
                    "size": size,
                    "method": "bm25_rerank"
                }

            return jsonify(results), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/cases/<doc_id>', methods=['GET'])
    def get_case_detail(doc_id):
        """
        Get full case details including full_text by ID

        Query params:
            index: which index to search - 'bm25' or 'dense' (default: 'bm25')

        Example: GET /cases/12121253?index=bm25

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
            index_type = request.args.get("index", "bm25").lower()
            index_name = ES_INDEX_BM25 if index_type == "bm25" else ES_INDEX_DENSE

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
            if "dense_vector" in doc:
                del doc["dense_vector"]

            return jsonify(doc), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/health', methods=['GET'])
    def health():
        """Health check"""
        try:
            es.ping()

            bm25_stats = None
            dense_stats = None

            if es.indices.exists(index=ES_INDEX_BM25):
                bm25_stats = es.count(index=ES_INDEX_BM25)["count"]

            if es.indices.exists(index=ES_INDEX_DENSE):
                dense_stats = es.count(index=ES_INDEX_DENSE)["count"]

            return jsonify({
                "status": "healthy",
                "elasticsearch": "connected",
                "indices": {
                    "bm25": {
                        "name": ES_INDEX_BM25,
                        "documents": bm25_stats
                    },
                    "dense": {
                        "name": ES_INDEX_DENSE,
                        "documents": dense_stats
                    }
                }
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 500
