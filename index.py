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
            "name": {"type": "keyword"},
            "name_abbreviation": {"type": "keyword"},
            "decision_date": {"type": "keyword"},
            "docket_number": {"type": "keyword"},

            # Court info
            "court_name": {"type": "keyword"},
            "court_abbreviation": {"type": "keyword"},

            # Jurisdiction info
            "jurisdiction_name": {"type": "keyword"},
            "jurisdiction_name_long": {"type": "keyword"},

            # Citations
            "citations_cite": {"type": "keyword"},
            "citation_type": {"type": "keyword"},

            # People
            "parties": {"type": "keyword"},
            "judges": {"type": "keyword"},
            "attorneys": {"type": "keyword"},

            # Opinions
            "opinion_type": {"type": "keyword"},
            "opinion_author": {"type": "keyword"},

            # Provenance
            "provenance_source": {"type": "keyword"},
            "provenance_batch": {"type": "keyword"},

            # Metadata
            "last_updated": {"type": "keyword"},

            # Numeric fields for range queries
            "word_count": {"type": "integer"},
            "char_count": {"type": "integer"},
            "pagerank_percentile": {"type": "float"},
            "first_page": {"type": "integer"},
            "last_page": {"type": "integer"},

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

    # Extract parties, judges, attorneys (keep as arrays for multi-value matching)
    parties = casebody.get("parties", [])
    judges = casebody.get("judges", [])
    attorneys = casebody.get("attorneys", [])

    # Extract opinion information
    opinion_types = [op.get("type", "") for op in opinions if op.get("type")]
    opinion_authors = [op.get("author", "") for op in opinions if op.get("author")]

    # Extract citations information
    citations = case_data.get("citations", [])
    citations_cite = [c.get("cite", "") for c in citations if "cite" in c]
    citation_types = [c.get("type", "") for c in citations if "type" in c]

    # Extract analysis information
    analysis = case_data.get("analysis", {})
    word_count = analysis.get("word_count", 0)
    char_count = analysis.get("char_count", 0)
    pagerank_percentile = analysis.get("pagerank", {}).get("percentile", 0.0)

    # Extract provenance information
    provenance = case_data.get("provenance", {})
    provenance_source = provenance.get("source", "")
    provenance_batch = provenance.get("batch", "")

    # Extract court and jurisdiction information
    court = case_data.get("court", {})
    jurisdiction = case_data.get("jurisdiction", {})

    # Build document
    doc = {
        "id": case_data.get("id"),
        "name": case_data.get("name"),
        "name_abbreviation": case_data.get("name_abbreviation"),
        "decision_date": case_data.get("decision_date"),
        "docket_number": case_data.get("docket_number"),
        "court_name": court.get("name"),
        "court_abbreviation": court.get("name_abbreviation"),
        "jurisdiction_name": jurisdiction.get("name"),
        "jurisdiction_name_long": jurisdiction.get("name_long"),
        "citations_cite": citations_cite,
        "citation_type": citation_types,
        "last_updated": case_data.get("last_updated"),
        "parties": parties,
        "judges": judges,
        "attorneys": attorneys,
        "opinion_type": opinion_types,
        "opinion_author": opinion_authors,
        "provenance_source": provenance_source,
        "provenance_batch": provenance_batch,
        "word_count": word_count,
        "char_count": char_count,
        "pagerank_percentile": pagerank_percentile,
        "first_page": case_data.get("first_page"),
        "last_page": case_data.get("last_page"),
        "full_text": full_text
    }
    es.index(index=index_name, document=doc)

