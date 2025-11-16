flowchart TD
    %% ---- Data & Offline Indexing Pipeline ----
    subgraph "Offline Pipeline: Data to Indexes"
        A[Raw Legal Data] --> B[Indexing Process]
        B -- "Lexical" --> C[BM25 Index]
        B -- "Semantic" --> D[Dual-Encoder Model]
        D -- "Encodes Documents" --> E[Vector Index (e.g., FAISS)]
    end

    %% ---- Online Search Pipeline ----
    subgraph "Online Pipeline: Search & Ranking"
        F[User Query] --> G[API Layer]
        G --> H[Search Layer]

        subgraph "1. Retrieval Stage (Two Paths)"
            H -- "BM25 Search" --> C
            H -- "Dense Search" --> I[Dual-Encoder Model]
            I -- "Encodes Query" --> E
        end

        subgraph "2. Re-ranking Stage (Optional)"
            J[Initial Results from BM25/Dense] --> K[Cross-Encoder Model]
            K -- "Scores (Query, Doc) pairs for relevance" --> L[Final Ranked List]
        end
    end

    %% ---- Final Output ----
    L --> G
    J --> G