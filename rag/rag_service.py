"""
RAG Service: Retrieval-Augmented Generation for Legal Q&A
Combines hybrid retrieval (BM25 + Dense KNN) with Ollama LLM
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from search.bm25_dense_for_rag import HybridFusion


class RAGService:
    def __init__(self, es_client=None, hybrid_fusion=None, ollama_url="http://localhost:11434"):
        """
        Initialize RAG service

        Args:
            es_client: Elasticsearch client instance (optional)
            hybrid_fusion: HybridFusion instance (optional)
            ollama_url: Ollama API URL (default: http://localhost:11434)
        """
        if hybrid_fusion is None:
            self.retriever = HybridFusion(es_client=es_client)
        else:
            self.retriever = hybrid_fusion

        self.ollama_url = ollama_url
        self.model = "qwen3:8b"  # Ollama model name

    def retrieve_context(self, query, k=5, max_chars_per_doc=5000):
        """
        Retrieve relevant legal cases using hybrid fusion

        Args:
            query: User question
            k: Number of documents to retrieve
            max_chars_per_doc: Max characters per document (to fit in context)

        Returns:
            List of context strings with citations
        """
        # Use hybrid fusion to get top-k documents with full_text
        # For now, we'll use the regular search method and fetch full_text separately
        results = self.retriever.search(query, size=k)

        contexts = []
        for i, doc in enumerate(results['results'], 1):
            # Fetch full document by ID
            from search.dense_searcher import DenseSearcher
            searcher = DenseSearcher(es_client=self.retriever.dense_searcher.es)
            full_doc = searcher.get_document_by_id(doc['id'])

            if full_doc and 'full_text' in full_doc:
                # Truncate to max_chars_per_doc
                full_text = full_doc.get('full_text', '')[:max_chars_per_doc]

                # Format with citation
                context = f"""[Case {i}] {full_doc.get('name', 'Unknown')}
Court: {full_doc.get('court_name', 'N/A')}
Date: {full_doc.get('decision_date', 'N/A')}

{full_text}
"""
                contexts.append({
                    'text': context,
                    'citation': {
                        'id': doc['id'],
                        'name': full_doc.get('name'),
                        'court': full_doc.get('court_name'),
                        'date': full_doc.get('decision_date')
                    }
                })

        return contexts

    def build_prompt(self, query, contexts):
        """
        Build prompt for LLM with retrieved context

        Args:
            query: User question
            contexts: List of context dicts with 'text' and 'citation' keys

        Returns:
            Prompt string
        """
        context_text = "\n\n---\n\n".join([ctx['text'] for ctx in contexts])

        prompt = f"""You are a legal research assistant specializing in Pennsylvania case law. Answer the user's question based ONLY on the provided case excerpts. If the answer cannot be found in the cases, say so clearly.

RETRIEVED CASES:
{context_text}

---

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question based on the case excerpts above
2. Cite specific cases using the format [Case N] where N is the case number
3. Be concise but accurate
4. If the cases don't contain enough information to answer, acknowledge this
5. Focus on Pennsylvania law and the specific cases provided

ANSWER:"""

        return prompt

    def generate_answer(self, prompt, temperature=0.3, max_tokens=800):
        """
        Generate answer using Ollama LLM with streaming

        Args:
            prompt: Full prompt with context and question
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of generated text
        """
        import json
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                stream=True,
                timeout=120
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk and chunk['response']:
                                yield chunk['response']
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"Error: Ollama API returned status {response.status_code}"

        except requests.exceptions.ConnectionError:
            yield "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
        except Exception as e:
            yield f"Error generating answer: {str(e)}"

    def ask(self, query, k=5, max_chars_per_doc=5000):
        """
        Complete RAG pipeline: retrieve + generate (streaming)

        Args:
            query: User question
            k: Number of documents to retrieve
            max_chars_per_doc: Max characters per document

        Yields:
            dict chunks with 'type' and data
        """
        # Step 1: Retrieve relevant cases
        contexts = self.retrieve_context(query, k=k, max_chars_per_doc=max_chars_per_doc)

        if not contexts:
            yield {
                "type": "error",
                "message": "No relevant cases found for your question."
            }
            return

        # Step 2: Send citations first
        yield {
            "type": "citations",
            "citations": [ctx['citation'] for ctx in contexts]
        }

        # Step 3: Build prompt
        prompt = self.build_prompt(query, contexts)

        # Step 4: Stream answer chunks
        for chunk in self.generate_answer(prompt):
            yield {
                "type": "answer",
                "chunk": chunk
            }


if __name__ == "__main__":
    print("Initializing RAG service...")
    rag = RAGService()

    # Test query
    query = "What are the requirements for contract formation in Pennsylvania?"
    print(f"\nQuestion: {query}\n")

    result = rag.ask(query, k=3)

    print("Answer:")
    print(result['answer'])
    print("\n" + "="*80)
    print("\nCitations:")
    for i, citation in enumerate(result['citations'], 1):
        print(f"{i}. {citation['name']} ({citation['court']}, {citation['date']})")
