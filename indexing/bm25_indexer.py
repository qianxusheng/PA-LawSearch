"""
BM25 Indexer - Baseline retrieval method
"""
from elasticsearch import Elasticsearch
import json
import os
import zipfile
from tqdm import tqdm
from config import ES_PASSWORD, ES_HOST, ES_INDEX_BM25


def create_bm25_index():
    """
    Create BM25 index with custom analyzer
    """
    es = Elasticsearch(
        ES_HOST,
        basic_auth=("elastic", ES_PASSWORD),
        verify_certs=False
    )

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
                            "english_stemmer"
                        ]
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "name": {"type": "text"},
                "decision_date": {"type": "keyword"},
                "court_name": {"type": "text"},
                "jurisdiction_name": {"type": "text"},
                "parties": {"type": "text"},
                "judges": {"type": "text"},
                "word_count": {"type": "integer"},
                "full_text": {
                    "type": "text",
                    "analyzer": "legal_text_analyzer"
                }
            }
        }
    }

    if es.indices.exists(index=ES_INDEX_BM25):
        print(f"Index {ES_INDEX_BM25} already exists. Deleting...")
        es.indices.delete(index=ES_INDEX_BM25)

    es.indices.create(index=ES_INDEX_BM25, body=mapping)
    print(f"Created index: {ES_INDEX_BM25}")

    return es


def index_documents(es, data_dir="data"):
    """
    Index all documents from data directory
    """
    json_files_info = []
    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        if os.path.isdir(folder_path):
            for zip_name in os.listdir(folder_path):
                if zip_name.endswith(".zip"):
                    zip_path = os.path.join(folder_path, zip_name)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for file_info in zip_ref.namelist():
                            if file_info.endswith(".json") and "json/" in file_info:
                                json_files_info.append((zip_path, file_info))

    print(f"Found {len(json_files_info)} documents to index")

    for zip_path, json_filename in tqdm(json_files_info, desc="Indexing BM25 cases"):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            with zip_ref.open(json_filename) as f:
                case_data = json.load(f)

        casebody = case_data.get("casebody", {})
        opinions = casebody.get("opinions", [])
        opinions_text = "\n".join([op.get("text", "") for op in opinions if "text" in op])
        head_matter = casebody.get("head_matter", "")

        if head_matter:
            full_text = head_matter + "\n" + opinions_text
        else:
            full_text = opinions_text

        parties = casebody.get("parties", [])
        judges = casebody.get("judges", [])
        analysis = case_data.get("analysis", {})
        word_count = analysis.get("word_count", 0)
        court = case_data.get("court", {})
        jurisdiction = case_data.get("jurisdiction", {})

        doc = {
            "id": case_data.get("id"),
            "name": case_data.get("name"),
            "decision_date": case_data.get("decision_date"),
            "court_name": court.get("name"),
            "jurisdiction_name": jurisdiction.get("name"),
            "parties": ", ".join(parties) if parties else "",
            "judges": ", ".join(judges) if judges else "",
            "word_count": word_count,
            "full_text": full_text
        }

        es.index(index=ES_INDEX_BM25, document=doc)

    print(f"Indexed {len(json_files_info)} documents to {ES_INDEX_BM25}")


if __name__ == "__main__":
    print("Creating BM25 index...")
    es = create_bm25_index()

    print("Indexing documents...")
    index_documents(es)

    print("Done!")
