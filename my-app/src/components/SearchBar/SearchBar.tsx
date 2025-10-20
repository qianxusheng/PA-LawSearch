import React, { useState } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <div className="w-full mx-auto">
      <form onSubmit={handleSubmit} className="flex gap-3 items-center">
        <input
          type="text"
          className="flex-1 px-6 py-4 text-lg border border-gray-300 rounded-3xl outline-none transition-all shadow-sm hover:shadow-md focus:border-indigo-600 focus:shadow-lg focus:shadow-indigo-100 disabled:bg-gray-100 disabled:cursor-not-allowed"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="px-10 py-4 text-lg font-medium text-white bg-indigo-600 border-none rounded-3xl cursor-pointer transition-all whitespace-nowrap shadow-sm hover:bg-indigo-700 hover:shadow-md hover:-translate-y-0.5 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none disabled:transform-none"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );
};

export default SearchBar;
