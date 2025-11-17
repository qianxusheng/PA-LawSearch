# ES Configuration
ES_PASSWORD = "0=ej+ZeERilvX9QENqYQ"
ES_HOST = "https://localhost:9200"

# Multiple index names for different retrieval methods
ES_INDEX_BM25 = "pa_law_cases_bm25"      # BM25 baseline
ES_INDEX_DENSE = "pa_law_cases_dense"    # Dense vector index

# Legacy support (for backward compatibility)
ES_INDEX_NAME = ES_INDEX_BM25

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 5000
API_DEBUG = True

# Model Configuration
# Legal-BERT models for encoding
DUAL_ENCODER_MODEL = "nlpaueb/legal-bert-base-uncased"  # For dual-encoder (retrieval)
CROSS_ENCODER_MODEL = "BAAI/bge-reranker-large" 

# Retrieval Configuration
DENSE_VECTOR_DIM = 768     # BERT base dimension

# For dense_rerank method only:
# Stage 1: Dense retrieval gets top-K candidates
# Stage 2: Cross-encoder reranks these K candidates
# Recommended for 200k docs: 100-500 (balance between accuracy and speed)
# - 100: Fast (~1-2s), good for most queries
# - 200: Moderate (~2-4s), better recall
# - 500: Slow (~5-10s), best recall
TOP_K_RERANK = 200      # Candidates to rerank (only affects dense_rerank method)

# For direct dense search: no hard limit (ES will handle pagination)
# User can browse as many pages as needed