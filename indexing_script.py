from elasticsearch import Elasticsearch
import json
import os
import zipfile
from tqdm import tqdm

PASSWORD = "0=ej+ZeERilvX9QENqYQ"
ES_HOST = "https://localhost:9200"
es = Elasticsearch(
    ES_HOST,
    basic_auth=("elastic", PASSWORD),
    verify_certs=False
)

index_name = "pa_law_cases"

## keyword and text mapping with custom analyzer
mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                ## preprocessing
                ## stem, remove stopwords and normalization
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
            # Basic info
            "id": {"type": "keyword"},
            "name": {"type": "text"},
            "decision_date": {"type": "keyword"},
            "court_name": {"type": "text"},
            "jurisdiction_name": {"type": "text"},

            # People
            "parties": {"type": "text"},
            "judges": {"type": "text"},

            # Metadata
            "word_count": {"type": "integer"},

            # Full text for query with custom analyzer
            "full_text": {
                "type": "text",
                "analyzer": "legal_text_analyzer"
            }
        }
    }
}

es.indices.create(index=index_name, body=mapping)

DATA_DIR = "data"

# collecting all the json path
json_files_info = []
for folder_name in os.listdir(DATA_DIR):
    folder_path = os.path.join(DATA_DIR, folder_name)
    if os.path.isdir(folder_path):
        for zip_name in os.listdir(folder_path):
            if zip_name.endswith(".zip"):
                zip_path = os.path.join(folder_path, zip_name)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for file_info in zip_ref.namelist():
                        if file_info.endswith(".json") and "json/" in file_info:
                            json_files_info.append((zip_path, file_info))

# batch processing
for zip_path, json_filename in tqdm(json_files_info, desc="Indexing cases"):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open(json_filename) as f:
            case_data = json.load(f)

    # Preprocessing: merge full text (opinions.text + head_matter)
    full_text = ""
    casebody = case_data.get("casebody", {})
    opinions = casebody.get("opinions", [])
    opinions_text = "\n".join([op.get("text", "") for op in opinions if "text" in op])
    head_matter = casebody.get("head_matter", "")
    if head_matter:
        full_text = head_matter + "\n" + opinions_text
    else:
        full_text = opinions_text

    # Extract basic info
    parties = casebody.get("parties", [])
    judges = casebody.get("judges", [])

    analysis = case_data.get("analysis", {})
    word_count = analysis.get("word_count", 0)

    court = case_data.get("court", {})
    jurisdiction = case_data.get("jurisdiction", {})

    # Build simplified document
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
    es.index(index=index_name, document=doc)

