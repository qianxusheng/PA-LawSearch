"""
Dense Vector Indexer using Legal-BERT
Creates index with dense_vector field for semantic search
"""
from elasticsearch import Elasticsearch
import json
import os
import zipfile
from tqdm import tqdm
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ES_PASSWORD, ES_HOST, ES_INDEX_DENSE, DENSE_VECTOR_DIM
from models.dual_encoder import DualEncoder


def create_dense_index():
    """
    Create dense vector index with dense_vector field
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
                },
                "dense_vector": {
                    "type": "dense_vector",
                    "dims": DENSE_VECTOR_DIM,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }

    if es.indices.exists(index=ES_INDEX_DENSE):
        print(f"Index {ES_INDEX_DENSE} already exists. Deleting...")
        es.indices.delete(index=ES_INDEX_DENSE)

    es.indices.create(index=ES_INDEX_DENSE, body=mapping)
    print(f"Created index: {ES_INDEX_DENSE}")

    return es


def index_documents(es, encoder, data_dir="data", batch_size=8):
    """
    Index all documents with dense vectors
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

    batch_docs = []
    batch_texts = []

    for zip_path, json_filename in tqdm(json_files_info, desc="Indexing Dense Vector cases"):
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

        batch_docs.append(doc)
        batch_texts.append(full_text[:2000])  # Truncate for encoding

        if len(batch_docs) >= batch_size:
            embeddings = encoder.encode(batch_texts, batch_size=batch_size)

            for doc, embedding in zip(batch_docs, embeddings):
                doc["dense_vector"] = embedding.tolist()
                es.index(index=ES_INDEX_DENSE, document=doc)

            batch_docs = []
            batch_texts = []

    if batch_docs:
        embeddings = encoder.encode(batch_texts, batch_size=batch_size)
        for doc, embedding in zip(batch_docs, embeddings):
            doc["dense_vector"] = embedding.tolist()
            es.index(index=ES_INDEX_DENSE, document=doc)

    print(f"Indexed {len(json_files_info)} documents to {ES_INDEX_DENSE}")


if __name__ == "__main__":
    print("Loading dual encoder model...")
    encoder = DualEncoder()

    print("Creating dense vector index...")
    es = create_dense_index()

    print("Indexing documents with dense vectors...")
    index_documents(es, encoder)

    print("Done!")
