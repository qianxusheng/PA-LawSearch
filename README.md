# IR Final Project - Legal Case Search

Multi-method legal case retrieval system with BM25 baseline and BERT-based semantic search.

## Overview

This project implements three retrieval methods for legal case search:

1. **BM25 (Baseline)**: Traditional keyword-based retrieval
2. **Dense Retrieval**: Legal-BERT dual-encoder for semantic search
3. **Dense + Reranking**: Two-stage retrieval with cross-encoder reranking

## Project Structure

```
IR/
├── config.py                    # Configuration (ES, models, etc.)
├── requirements.txt             # Python dependencies
├── batch_download.py           # Download data from case.law
│
├── api/                        # API package
│   ├── app.py                 # Flask app setup & entry point
│   └── routes.py              # API routes
│
├── indexing/                   # Indexing scripts
│   ├── bm25_indexer.py        # Create BM25 index
│   └── dense_indexer.py       # Create dense vector index
│
├── models/                     # BERT models
│   ├── dual_encoder.py        # Legal-BERT for embeddings
│   └── cross_encoder.py       # Cross-encoder for reranking
│
├── search/                     # Search implementations
│   ├── bm25_searcher.py       # BM25 search
│   ├── dense_searcher.py      # Dense vector search
│   └── reranker.py            # Two-stage retrieval
│
└── frontend/                   # React frontend
    └── ...
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Elasticsearch

Update config.py with your Elasticsearch credentials:
- `ES_HOST`: Your Elasticsearch host
- `ES_PASSWORD`: Your Elasticsearch password

### 3. Create Indices

#### BM25 Index (Baseline)
```bash
python -m indexing.bm25_indexer
```

#### Dense Vector Index (for semantic search)
```bash
python -m indexing.dense_indexer
```
Note: This will download Legal-BERT model (~400MB) on first run.

### 4. Start API Server

```bash
python -m api.app
```

API will be available at `http://localhost:5000`

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Search Cases
```
GET /cases?query=<text>&method=<method>&size=<n>&page=<p>
```

**Parameters:**
- `query` (required): Search query text
- `method` (optional): Retrieval method
  - `bm25`: Traditional BM25 (default)
  - `dense`: Dense vector retrieval (Legal-BERT)
  - `dense_rerank`: Two-stage (dense + cross-encoder)
- `size` (optional): Number of results (default: 10)
- `page` (optional): Page number (default: 1)

**Example:**
```bash
curl "http://localhost:5000/cases?query=contract%20law&method=dense_rerank&size=5"
```

### Get Case Details
```
GET /cases/<doc_id>?index=<bm25|dense>
```

**Example:**
```bash
curl "http://localhost:5000/cases/12121253?index=bm25"
```

### Health Check
```
GET /health
```

## Retrieval Methods

### 1. BM25 (Baseline)
- Traditional keyword-based retrieval
- Uses Elasticsearch's BM25 algorithm
- Fast and lightweight

### 2. Dense Retrieval
- Uses Legal-BERT dual-encoder
- Model: `nlpaueb/legal-bert-base-uncased`
- Semantic similarity via cosine distance
- Better at capturing semantic meaning

### 3. Dense + Reranking (Two-stage)
- **Stage 1 (Coarse)**: Dense retrieval gets top 100 candidates
- **Stage 2 (Fine)**: Cross-encoder reranks to top 10
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Best accuracy but slower

## Configuration

Edit config.py to customize:

```python
# Models
DUAL_ENCODER_MODEL = "nlpaueb/legal-bert-base-uncased"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Retrieval parameters
TOP_K_RETRIEVAL = 100  # for reranking
```

## Notes

- The Elasticsearch instance needs to be set up locally
- Dense indexing will take longer due to BERT encoding (3 hours for GPU, 12 hours for CPU)
- Sparse indexing will take around 3 hour
- Models are cached after first download
- GPU recommended for faster dense encoding (CPU works too)
