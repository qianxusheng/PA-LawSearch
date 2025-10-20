import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CaseResult } from '../../types';
import SearchBar from '../../components/SearchBar/SearchBar';
import SearchResults from '../../components/SearchResults/SearchResults';
import CaseDetail from '../../components/CaseDetail/CaseDetail';

const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState<CaseResult[] | null>(null);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      handleSearch(q, 1);
    }
  }, [searchParams]);

  const handleSearch = async (searchQuery: string, page = 1) => {
    setQuery(searchQuery);
    setCurrentPage(page);
    setIsLoading(true);
    setError(null);
    setSearchParams({ q: searchQuery });

    const pageSize = 10;
    try {
      const response = await fetch(`http://localhost:5000/cases?query=${encodeURIComponent(searchQuery)}&size=${pageSize}&page=${page}`);

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data.results);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (query) {
      handleSearch(query, newPage);
    }
  };

  const handleCaseClick = (caseId: string) => {
    setSelectedCaseId(caseId);
  };

  const handleCloseDetail = () => {
    setSelectedCaseId(null);
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="p-6 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-8">
        {error && (
          <div className="max-w-4xl mx-auto mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-center">
            Error: {error}. Make sure the backend server is running on port 5000.
          </div>
        )}

        {(results || isLoading) && (
          <div className="max-w-4xl mx-auto">
            <SearchResults
              results={results}
              isLoading={isLoading}
              total={total}
              onCaseClick={handleCaseClick}
            />

            {total > 0 && (
              <div className="flex justify-center items-center gap-6 my-8">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1 || isLoading}
                  className="px-5 py-2.5 text-base bg-indigo-600 text-white border-none rounded-md cursor-pointer transition-colors hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600 font-medium">
                  Page {currentPage} of {Math.ceil(total / 10)}
                  ({total} total results)
                </span>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(total / 10) || isLoading}
                  className="px-5 py-2.5 text-base bg-indigo-600 text-white border-none rounded-md cursor-pointer transition-colors hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}

        {selectedCaseId && (
          <CaseDetail caseId={selectedCaseId} onClose={handleCloseDetail} />
        )}
      </div>
    </div>
  );
};

export default Search;
