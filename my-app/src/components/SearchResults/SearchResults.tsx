import React from 'react';
import { CaseResult } from '../../types';
import ResultCard from './ResultCard';

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
    return <div className="text-center p-8 text-xl text-gray-600">Searching...</div>;
  }

  if (!results) {
    return (
      <div className="text-center p-12 bg-gray-50 rounded-lg text-gray-600">
        <p>Enter a search query to find Pennsylvania legal cases</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center p-12 bg-gray-50 rounded-lg text-gray-600">
        <p>No results found. Try adjusting your search.</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="hidden">
        <h2>Search Results</h2>
        <span className="results-count">Found {total} cases</span>
      </div>

      <div className="flex flex-col gap-6">
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
