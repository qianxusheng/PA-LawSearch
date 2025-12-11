"""
Index precomputed dense embeddings into Elasticsearch.

Usage (from project root):
    .\venv\Scripts\Activate.ps1
    python -m indexing.index_dense_from_file

Requires:
    - embeddings.jsonl in the project root (from the GPU run)
      Each line should be a JSON object with at least:
        {
          "id": ...,
          "name": ...,
          "decision_date": ...,
          "court_name": ...,
          "jurisdiction_name": ...,
          "parties": ...,
          "judges": ...,
          "word_count": ...,
          "full_text": ...,
          "dense_vector": [ ... floats ... ]
        }
    - Elasticsearch running locally
    - config.py with ES_HOST, ES_PASSWORD, ES_INDEX_DENSE, DENSE_VECTOR_DIM
"""

import json
from pathlib import Path

import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from tqdm import tqdm

from config import ES_HOST, ES_PASSWORD, ES_INDEX_DENSE, DENSE_VECTOR_DIM

# Silence insecure HTTPS warnings for local dev
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMBEDDINGS_PATH = Path("embeddings.jsonl")
BATCH_SIZE = 500


def create_dense_index() -> Elasticsearch:
    """
    Create (or recreate) the dense-vector index used for semantic search.

    This is intentionally duplicated here so we don't need to import
    indexing.dense_indexer (which pulls in torch / DualEncoder).
    """
    es = Elasticsearch(
        ES_HOST,
        basic_auth=("elastic", ES_PASSWORD),
        verify_certs=False,
        request_timeout=60,
    )

    # Drop existing index if present (fresh rebuild)
    if es.indices.exists(index=ES_INDEX_DENSE):
        print(f"Deleting existing index: {ES_INDEX_DENSE}")
        es.indices.delete(index=ES_INDEX_DENSE)

    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "legal_text_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                        ],
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_",
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english",
                    },
                },
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer",
                },
                "decision_date": {"type": "date"},
                "court_name": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer",
                },
                "jurisdiction_name": {"type": "keyword"},
                "parties": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer",
                },
                "judges": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer",
                },
                "word_count": {"type": "integer"},
                "full_text": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer",
                },
                "dense_vector": {
                    "type": "dense_vector",
                    "dims": DENSE_VECTOR_DIM,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        },
    }

    es.indices.create(index=ES_INDEX_DENSE, body=mapping)
    # Optimize for bulk indexing: no replicas and infrequent refreshes
    es.indices.put_settings(
        index=ES_INDEX_DENSE,
        body={
            "index": {
                "refresh_interval": "-1",
                "number_of_replicas": 0,
            }
        },
    )
    print(f"Created dense index '{ES_INDEX_DENSE}'.")
    return es


def index_batch(es: Elasticsearch, actions, failed_docs) -> int:
    """
    Index a single batch using streaming_bulk, but do NOT crash
    if some documents fail. Instead, record failures in failed_docs.
    Returns number of successfully indexed docs in this batch.
    """
    success_count = 0

    # streaming_bulk consumes the iterable, so we pass a list directly
    for ok, result in streaming_bulk(
        es,
        actions,
        request_timeout=300,
        raise_on_error=False,
        raise_on_exception=False,
    ):
        if ok:
            success_count += 1
        else:
            # result looks like {"index": {"_index": ..., "_id": ..., "status": ..., "error": {...}}}
            action, info = next(iter(result.items()))
            doc_id = info.get("_id")
            error = info.get("error")
            failed_docs.append({"id": doc_id, "error": error})

    return success_count


def main() -> None:
    # 1. Sanity check: make sure embeddings file exists
    if not EMBEDDINGS_PATH.is_file():
        raise FileNotFoundError(
            f"{EMBEDDINGS_PATH} not found. Make sure embeddings.jsonl "
            f"is in the project root."
        )

    # 2. (Re)create the dense index using our local helper
    print("Creating dense vector index via create_dense_index()...")
    es = create_dense_index()
    print(f"Index '{ES_INDEX_DENSE}' is ready.")

    # 3. Stream embeddings.jsonl and bulk index in batches
    print(f"Indexing documents from {EMBEDDINGS_PATH}...")
    actions = []
    total_indexed = 0
    failed_docs = []

    with EMBEDDINGS_PATH.open("r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Indexing dense embeddings"):
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            # Validate dense vector
            dv = record.get("dense_vector")
            if not isinstance(dv, list) or len(dv) != DENSE_VECTOR_DIM:
                # Skip malformed entries
                continue

            doc_id = record["id"]

            actions.append(
                {
                    "_index": ES_INDEX_DENSE,
                    "_id": doc_id,  # stable id in ES
                    "_source": {
                        "id": doc_id,
                        "name": record.get("name"),
                        "decision_date": record.get("decision_date"),
                        "court_name": record.get("court_name"),
                        "jurisdiction_name": record.get("jurisdiction_name"),
                        "parties": record.get("parties"),
                        "judges": record.get("judges"),
                        "word_count": record.get("word_count"),
                        "full_text": record.get("full_text"),
                        "dense_vector": dv,
                    },
                }
            )

            if len(actions) >= BATCH_SIZE:
                total_indexed += index_batch(es, actions, failed_docs)
                actions = []

        # Flush any remaining docs
        if actions:
            total_indexed += index_batch(es, actions, failed_docs)

    print(f"Successfully indexed {total_indexed} documents into '{ES_INDEX_DENSE}'.")

    if failed_docs:
        print(f"{len(failed_docs)} document(s) failed to index.")
        # Show a few examples to debug mapping issues
        for entry in failed_docs[:5]:
            print(f"- Failed id={entry['id']}, error={entry['error']}")

    # 4. Restore normal index settings after heavy indexing
    es.indices.put_settings(
        index=ES_INDEX_DENSE,
        body={
            "index": {
                "refresh_interval": "1s",
                # If you want replicas for robustness later, add:
                # "number_of_replicas": 1,
            }
        },
    )
    print("Dense index settings updated (refresh_interval=1s). Done.")


if __name__ == "__main__":
    main()
