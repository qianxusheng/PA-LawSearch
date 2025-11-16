import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SearchBar, SearchResults, CaseDetail } from '@/components';
import { useSearch } from '@/hooks';
import { SearchMethod } from '@/types';

const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [method, setMethod] = useState<SearchMethod>('bm25');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [jumpToPage, setJumpToPage] = useState('');

  const { results, total, isLoading, error, search } = useSearch();

  useEffect(() => {
    const q = searchParams.get('q');
    const m = searchParams.get('method') as SearchMethod;
    if (q) {
      setQuery(q);
      const searchMethod = m && ['bm25', 'dense', 'dense_rerank'].includes(m) ? m : 'bm25';
      setMethod(searchMethod);
      search(q, searchMethod, 1);
    }
  }, [searchParams]);

  const handleSearch = async (searchQuery: string, searchMethod: SearchMethod, page = 1) => {
    setQuery(searchQuery);
    setMethod(searchMethod);
    setCurrentPage(page);
    setSearchParams({ q: searchQuery, method: searchMethod });
    await search(searchQuery, searchMethod, page);
  };

  const handlePageChange = (newPage: number) => {
    if (query) {
      handleSearch(query, method, newPage);
    }
  };

  const handleCaseClick = (caseId: string) => {
    setSelectedCaseId(caseId);
  };

  const handleCloseDetail = () => {
    setSelectedCaseId(null);
  };

  const handleJumpToPage = () => {
    const pageNum = parseInt(jumpToPage);
    const maxPage = Math.ceil(total / 10);
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= maxPage) {
      handleSearch(query, method, pageNum);
      setJumpToPage('');
    }
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
              <div className="flex justify-center items-center gap-4 my-8">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1 || isLoading}
                  className="px-5 py-2.5 text-base bg-indigo-600 text-white border-none rounded-md cursor-pointer transition-colors hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Previous
                </button>

                <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-sm text-gray-600 font-medium">
                    Page {currentPage} of {Math.ceil(total / 10)}
                  </span>
                  <span className="text-gray-300">|</span>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={jumpToPage}
                    onChange={(e) => setJumpToPage(e.target.value.replace(/\D/g, ''))}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleJumpToPage();
                      }
                    }}
                    className="w-16 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />
                  <button
                    onClick={handleJumpToPage}
                    disabled={isLoading}
                    className="px-3 py-1 text-sm bg-indigo-600 text-white border-none rounded cursor-pointer transition-colors hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    Go
                  </button>
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(total / 10) || isLoading}
                  className="px-5 py-2.5 text-base bg-indigo-600 text-white border-none rounded-md cursor-pointer transition-colors hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Next
                </button>

                <span className="text-sm text-gray-500 ml-2">
                  ({total} total results)
                </span>
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
