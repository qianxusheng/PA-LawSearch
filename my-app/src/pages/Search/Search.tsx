import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../../components/SearchBar/SearchBar';
import SearchResults from '../../components/SearchResults/SearchResults';
import CaseDetail from '../../components/CaseDetail/CaseDetail';
import './Search.css';

function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState(null);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCaseId, setSelectedCaseId] = useState(null);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      handleSearch(q, 1);
    }
  }, [searchParams]);

  const handleSearch = async (searchQuery, page = 1) => {
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
      setError(err.message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (query) {
      handleSearch(query, newPage);
    }
  };

  const handleCaseClick = (caseId) => {
    setSelectedCaseId(caseId);
  };

  const handleCloseDetail = () => {
    setSelectedCaseId(null);
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      </div>

      <div className="search-content">
        {error && (
          <div className="error-message">
            Error: {error}. Make sure the backend server is running on port 5000.
          </div>
        )}

        {(results || isLoading) && (
          <div className="results-container">
            <SearchResults
              results={results}
              isLoading={isLoading}
              total={total}
              onCaseClick={handleCaseClick}
            />

            {total > 0 && (
              <div className="pagination">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1 || isLoading}
                >
                  Previous
                </button>
                <span>
                  Page {currentPage} of {Math.ceil(total / 10)}
                  ({total} total results)
                </span>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(total / 10) || isLoading}
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
}

export default Search;
