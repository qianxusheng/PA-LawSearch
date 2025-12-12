import React, { useState } from 'react';
import { SearchMethod, SearchFilters } from '@/types';
import MethodRadio from './MethodRadio';

interface SearchBarProps {
  onSearch: (query: string, method: SearchMethod, filters: SearchFilters) => void;
  isLoading: boolean;
  initialQuery?: string;
  initialMethod?: SearchMethod;
}

const SEARCH_METHODS = [
  { value: 'bm25' as SearchMethod, label: 'BM25' },
  { value: 'dense' as SearchMethod, label: 'Dense' },
  { value: 'dense_rerank' as SearchMethod, label: 'Dense+Rerank' },
];

const COURT_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Any court' },
  { value: 'Pennsylvania Department of Justice', label: 'Pennsylvania Department of Justice' },
  { value: 'Superior Court of Pennsylvania', label: 'Superior Court of Pennsylvania' },
  { value: 'Supreme Court of Pennsylvania', label: 'Supreme Court of Pennsylvania' },
];

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  isLoading,
  initialQuery = '',
  initialMethod = 'bm25',
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [method, setMethod] = useState<SearchMethod>(initialMethod);
  const [showFilters, setShowFilters] = useState(false);
  const [court, setCourt] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // keep internal state in sync when props change
  React.useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  React.useEffect(() => {
    setMethod(initialMethod);
  }, [initialMethod]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const filters: SearchFilters = {
      court: court || undefined,
      startDate: startDate || undefined,
      endDate: endDate || undefined,
    };

    onSearch(query, method, filters);
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

        {/* Search Input, Filters, and Button */}
        <div className="flex flex-col gap-3">
          <div className="flex gap-3 items-center">
            <input
              type="text"
              className="flex-1 px-6 py-4 text-lg border border-gr...[your existing tailwind classes]..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isLoading}
              placeholder="Search legal cases..."
            />

            <button
              type="submit"
              className="px-10 py-4 text-lg font-medium text-white...[your existing tailwind classes]..."
              disabled={isLoading || !query.trim()}
            >
              {isLoading ? 'Searching…' : 'Search'}
            </button>
          </div>

          {/* Filters toggle */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setShowFilters((prev) => !prev)}
              className="text-sm text-indigo-700 font-medium hover:text-indigo-900"
            >
              {showFilters ? 'Hide filters' : 'Show filters'}
            </button>
          </div>

          {showFilters && (
            <div className="mt-2 p-4 bg-gray-50 border border-gray-200 rounded-lg space-y-4">
              {/* Court selection */}
              <div>
                <span className="block text-xs font-semibold text-gray-500 mb-2">
                  Court
                </span>
                <div className="flex flex-wrap gap-2">
                  {COURT_OPTIONS.map((option) => (
                    <button
                      key={option.value || 'any'}
                      type="button"
                      onClick={() => setCourt(option.value)}
                      className={`px-3 py-1.5 text-xs rounded-full border ${
                        court === option.value
                          ? 'bg-indigo-600 text-white border-indigo-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-indigo-400'
                      }`}
                      disabled={isLoading}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Date range */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">
                    Start date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    disabled={isLoading}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">
                    End date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    disabled={isLoading}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar;
