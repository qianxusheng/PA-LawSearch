"""
Dual-Encoder using Legal-BERT for generating dense vectors
Used for coarse-grained retrieval stage
"""
import torch
from transformers import AutoTokenizer, AutoModel
from config import DUAL_ENCODER_MODEL
import numpy as np


class DualEncoder:
    def __init__(self, model_name=DUAL_ENCODER_MODEL, device=None):
        """
        Initialize dual-encoder model

        Args:
            model_name: HuggingFace model name
            device: 'cuda' or 'cpu', auto-detect if None
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading dual-encoder model: {model_name}")
        print(f"Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def encode(self, texts, batch_size=16, max_length=512, show_progress=False):
        """
        Encode texts into dense vectors using mean pooling

        Args:
            texts: List of text strings or single string
            batch_size: Batch size for encoding
            max_length: Max token length
            show_progress: Show progress bar

        Returns:
            numpy array of shape (n, 768) for BERT-base
        """
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors='pt'
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**encoded)
                embeddings = self._mean_pooling(outputs, encoded['attention_mask'])

            all_embeddings.append(embeddings.cpu().numpy())

        all_embeddings = np.vstack(all_embeddings)
        return all_embeddings

    def _mean_pooling(self, model_output, attention_mask):
        """
        Mean pooling - take attention mask into account for correct averaging
        """
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def encode_query(self, query):
        """
        Encode a single query

        Args:
            query: Query string

        Returns:
            numpy array of shape (768,)
        """
        return self.encode(query)[0]

    def encode_document(self, document):
        """
        Encode a single document

        Args:
            document: Document string

        Returns:
            numpy array of shape (768,)
        """
        return self.encode(document)[0]

    def compute_similarity(self, query_embedding, doc_embeddings):
        """
        Compute cosine similarity between query and documents

        Args:
            query_embedding: numpy array (768,)
            doc_embeddings: numpy array (n, 768)

        Returns:
            numpy array of similarity scores (n,)
        """
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        doc_norms = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-9)
        similarities = np.dot(doc_norms, query_norm)
        return similarities


if __name__ == "__main__":
    encoder = DualEncoder()

    query = "What are the legal requirements for contract formation?"
    documents = [
        "A contract requires offer, acceptance, and consideration.",
        "The court ruled that the defendant violated copyright law.",
        "Contract law governs agreements between parties."
    ]

    query_emb = encoder.encode_query(query)
    doc_embs = encoder.encode(documents)

    print(f"Query embedding shape: {query_emb.shape}")
    print(f"Document embeddings shape: {doc_embs.shape}")

    similarities = encoder.compute_similarity(query_emb, doc_embs)
    print(f"\nSimilarities: {similarities}")

    ranked_indices = np.argsort(similarities)[::-1]
    print("\nRanked documents:")
    for i, idx in enumerate(ranked_indices):
        print(f"{i+1}. (score={similarities[idx]:.4f}) {documents[idx][:80]}...")
