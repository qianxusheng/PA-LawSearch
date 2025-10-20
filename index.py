from elasticsearch import Elasticsearch
import json
import os
from tqdm import tqdm

## TODO: indexing all docs
## TODO: how to collect, where to store?

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "0=ej+ZeERilvX9QENqYQ"),
    verify_certs=False
)

index_name = "legal_cases_test"

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

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
es.indices.create(index=index_name, body=mapping)

DATA_DIR = "data/add"
json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
for filename in tqdm(json_files, desc="Indexing cases"):
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "r", encoding="utf-8") as f:
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

