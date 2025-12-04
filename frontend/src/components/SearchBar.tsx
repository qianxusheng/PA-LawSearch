import React, { useState } from 'react';
import { SearchMethod } from '@/types';
import MethodRadio from './MethodRadio';

interface SearchBarProps {
  onSearch: (query: string, method: SearchMethod) => void;
  isLoading: boolean;
  initialQuery?: string;
  initialMethod?: SearchMethod;
}

const SEARCH_METHODS = [
  { value: 'bm25' as SearchMethod, label: 'BM25' },
  { value: 'dense' as SearchMethod, label: 'Dense' },
  { value: 'dense_rerank' as SearchMethod, label: 'Dense+Rerank' }
];

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading, initialQuery = '', initialMethod = 'bm25' }) => {
  const [query, setQuery] = useState(initialQuery);
  const [method, setMethod] = useState<SearchMethod>(initialMethod);

  // Update query and method when props change
  React.useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  React.useEffect(() => {
    setMethod(initialMethod);
  }, [initialMethod]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, method);
    }
  };

  return (
    <div className="w-full mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Search Method Selection */}
        <div className="flex gap-6 items-center justify-center">
          <span className="text-sm font-medium text-gray-600">Method:</span>
          {SEARCH_METHODS.map(({ value, label }) => (
            <MethodRadio
              key={value}
              value={value}
              label={label}
              checked={method === value}
              disabled={isLoading}
              onChange={setMethod}
            />
          ))}
        </div>

        {/* Search Input and Button */}
        <div className="flex gap-3 items-center">
          <input
            type="text"
            className="flex-1 px-6 py-4 text-lg border border-gray-300 rounded-3xl outline-none transition-all shadow-sm hover:shadow-md focus:border-indigo-600 focus:shadow-lg focus:shadow-indigo-100 disabled:bg-gray-100 disabled:cursor-not-allowed"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            placeholder="Search legal cases..."
          />
          <button
            type="submit"
            className="px-10 py-4 text-lg font-medium text-white bg-indigo-600 border-none rounded-3xl cursor-pointer transition-all whitespace-nowrap shadow-sm hover:bg-indigo-700 hover:shadow-md hover:-translate-y-0.5 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none disabled:transform-none"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchBar;
