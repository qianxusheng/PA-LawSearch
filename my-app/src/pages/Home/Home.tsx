import { useNavigate } from 'react-router-dom';
import SearchBar from '../../components/SearchBar/SearchBar';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  const handleSearch = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="home">
      <header className="home-header">
        <h1>Pennsylvania Legal Case Search</h1>
        <p className="subtitle">
          Reference: <a href="https://case.law/" target="_blank" rel="noopener noreferrer">case.law</a>
        </p>
      </header>

      <div className="home-search">
        <SearchBar onSearch={handleSearch} isLoading={false} />
      </div>
    </div>
  );
}

export default Home;
