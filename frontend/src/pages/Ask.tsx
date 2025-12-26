import React, { useState } from 'react';
import { Link } from 'react-router-dom';

interface Citation {
  id: string;
  name: string;
  court: string;
  date: string;
}

const Ask: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async () => {
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);
    setAnswer('');
    setCitations([]);

    try {
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question.trim(),
          k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            console.log('Received chunk:', data);

            if (data.type === 'citations') {
              setCitations(data.citations);
              setIsLoading(false);
            } else if (data.type === 'answer') {
              setAnswer(prev => prev + data.chunk);
            } else if (data.type === 'error') {
              setError(data.message);
              setIsLoading(false);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="p-6 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <header className="mb-6">
            <Link to="/" className="inline-flex flex-col">
              <span className="text-xl font-semibold text-gray-900">
                Pennsylvania Legal Case Q&A
              </span>
              <span className="text-sm text-gray-500">
                Powered by Hybrid Retrieval + Ollama LLM
              </span>
            </Link>
          </header>

          <div className="space-y-4">
            <div>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a legal question about Pennsylvania case law..."
                className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows={4}
                disabled={isLoading}
              />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">
                Press Enter to submit, Shift+Enter for new line
              </span>
              <button
                onClick={handleAsk}
                disabled={isLoading || !question.trim()}
                className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Thinking...' : 'Ask Question'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-8">
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
            Error: {error}. Make sure the backend server and Ollama are running.
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
            <p className="text-gray-600">Retrieving relevant cases and generating answer...</p>
          </div>
        )}

        {answer && !isLoading && (
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Answer</h2>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{answer}</p>
              </div>
            </div>

            {citations.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Citations ({citations.length} cases)
                </h2>
                <div className="space-y-3">
                  {citations.map((citation, index) => (
                    <div
                      key={citation.id}
                      className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="flex items-start">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-sm font-medium mr-3 shrink-0">
                          {index + 1}
                        </span>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{citation.name}</h3>
                          <div className="mt-1 text-sm text-gray-600">
                            <p>{citation.court}</p>
                            <p>{citation.date}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-center">
              <button
                onClick={() => {
                  setQuestion('');
                  setAnswer('');
                  setCitations([]);
                  setError(null);
                }}
                className="px-4 py-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Ask Another Question
              </button>
            </div>
          </div>
        )}

        {!answer && !isLoading && !error && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No answer yet</h3>
            <p className="mt-1 text-sm text-gray-500">Ask a question to get started</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Ask;
