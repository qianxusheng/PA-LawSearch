import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { SearchBar } from '@/components';
import { SearchMethod } from '@/types';
import { ROUTES } from '@/constants';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const handleSearch = (query: string, method: SearchMethod) => {
    navigate(`${ROUTES.SEARCH}?q=${encodeURIComponent(query)}&method=${method}`);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center pt-[25vh]">
      <header className="text-center text-gray-800 p-4 mb-6">
        <h1 className="text-4xl m-0 mb-2 font-normal text-gray-900">
          Pennsylvania Legal Case Search
        </h1>
        <p className="text-2xl m-0 text-gray-600">
          Reference:{' '}
          <a
            href="https://case.law/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 no-underline transition-colors hover:text-indigo-700 hover:underline"
          >
            case.law
          </a>
        </p>
      </header>

      <div className="w-full max-w-4xl px-4">
        <SearchBar onSearch={handleSearch} isLoading={false} />

        <div className="mt-6 text-center">
          <Link
            to="/ask"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Try Legal Q&A (RAG)
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
