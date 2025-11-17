"""
Cross-Encoder for reranking
Used for fine-grained reranking stage
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import CROSS_ENCODER_MODEL
import numpy as np


class CrossEncoder:
    def __init__(self, model_name=CROSS_ENCODER_MODEL, device=None):
        """
        Initialize cross-encoder model for reranking

        Args:
            model_name: HuggingFace model name
            device: 'cuda' or 'cpu', auto-detect if None
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading cross-encoder model: {model_name}")
        print(f"Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def predict(self, query_doc_pairs, batch_size=16, max_length=512):
        """
        Compute relevance scores for query-document pairs

        Args:
            query_doc_pairs: List of (query, document) tuples
            batch_size: Batch size for prediction
            max_length: Max token length

        Returns:
            numpy array of relevance scores
        """
        all_scores = []

        for i in range(0, len(query_doc_pairs), batch_size):
            batch_pairs = query_doc_pairs[i:i + batch_size]

            queries = [pair[0] for pair in batch_pairs]
            documents = [pair[1] for pair in batch_pairs]

            encoded = self.tokenizer(
                queries,
                documents,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors='pt'
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**encoded)
                scores = outputs.logits.squeeze(-1)

            all_scores.append(scores.cpu().numpy())

        all_scores = np.concatenate(all_scores)
        return all_scores

    def rerank(self, query, documents, batch_size=16):
        """
        Rerank documents for a given query

        Args:
            query: Query string
            documents: List of document strings
            batch_size: Batch size for prediction

        Returns:
            List of (index, score) tuples sorted by score (descending)
        """
        query_doc_pairs = [(query, doc) for doc in documents]
        scores = self.predict(query_doc_pairs, batch_size=batch_size)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked


if __name__ == "__main__":
    reranker = CrossEncoder()

    query = "What are the legal requirements for contract formation?"
    documents = [
        "A contract requires offer, acceptance, and consideration.",
        "The court ruled that the defendant violated copyright law.",
        "Contract law governs agreements between parties.",
        "Formation of a valid contract needs mutual assent and legal purpose."
    ]

    ranked = reranker.rerank(query, documents)

    print("Reranked documents:")
    for idx, score in ranked:
        print(f"Score: {score:.4f} | {documents[idx][:80]}...")
