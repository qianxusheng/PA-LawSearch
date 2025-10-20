import React from 'react';
import { CaseResult } from '../../types';
import ResultCard from './ResultCard';
import './SearchResults.css';

interface SearchResultsProps {
  results: CaseResult[] | null;
  isLoading: boolean;
  total: number;
  onCaseClick: (caseId: string) => void;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  isLoading,
  total,
  onCaseClick
}) => {
  if (isLoading) {
    return <div className="loading">Searching...</div>;
  }

  if (!results) {
    return (
      <div className="no-results">
        <p>Enter a search query to find Pennsylvania legal cases</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="no-results">
        <p>No results found. Try adjusting your search.</p>
      </div>
    );
  }

  return (
    <div className="search-results">
      <div className="results-header">
        <h2>Search Results</h2>
        <span className="results-count">Found {total} cases</span>
      </div>

      <div className="results-list">
        {results.map((result, index) => (
          <ResultCard
            key={result.id || index}
            result={result}
            onCaseClick={onCaseClick}
          />
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
