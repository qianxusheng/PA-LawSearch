import React from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../../components/SearchBar/SearchBar';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
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
      </div>
    </div>
  );
};

export default Home;
