import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { apiRequest, apiConfig } from '../config/api';

const SearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [includeImages, setIncludeImages] = useState(true);

  const performSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const data = await apiRequest(apiConfig.endpoints.search, {
        method: 'POST',
        body: JSON.stringify({
          query,
          limit: 10,
          include_images: includeImages,
        }),
      });

      setResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  };

  const exampleQueries = [
    'payment issues',
    'refund policy',
    'billing questions',
    'account problems',
    'technical support',
  ];

  return (
    <div className="search-interface">
      <div className="search-header">
        <h3>Semantic Search</h3>
        <p>Search through conversation history and knowledge base using AI-powered semantic search</p>
      </div>

      <div className="search-input-section">
        <div className="search-input-container">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your search query..."
            className="search-input"
          />
          <button
            onClick={performSearch}
            disabled={isLoading || !query.trim()}
            className="search-button"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="search-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
            />
            Include image results
          </label>
        </div>

        <div className="example-queries">
          <span>Example queries:</span>
          {exampleQueries.map((exampleQuery) => (
            <button
              key={exampleQuery}
              onClick={() => setQuery(exampleQuery)}
              className="example-query"
            >
              {exampleQuery}
            </button>
          ))}
        </div>
      </div>

      <div className="search-results">
        {results.length > 0 && (
          <div className="results-header">
            <h4>Search Results ({results.length})</h4>
          </div>
        )}

        {results.map((result, index) => (
          <div key={index} className="search-result">
            <div className="result-header">
              <span className="result-score">
                Relevance: {(result.score * 100).toFixed(1)}%
              </span>
              <span className="result-type">
                {result.payload?.type || 'Unknown'}
              </span>
            </div>

            <div className="result-content">
              {result.payload?.message && (
                <div className="result-message">
                  <strong>Message:</strong> {result.payload.message}
                </div>
              )}
              
              {result.payload?.response && (
                <div className="result-response">
                  <strong>Response:</strong> {result.payload.response}
                </div>
              )}

              {result.payload?.user_id && (
                <div className="result-user">
                  <strong>User:</strong> {result.payload.user_id}
                </div>
              )}

              {result.payload?.timestamp && (
                <div className="result-timestamp">
                  <strong>Date:</strong> {new Date(result.payload.timestamp).toLocaleString()}
                </div>
              )}

              {result.payload?.sentiment && (
                <div className="result-sentiment">
                  <strong>Sentiment:</strong>
                  {Object.entries(result.payload.sentiment).map(([key, value]) => (
                    <span key={key} className={`sentiment-tag sentiment-${key}`}>
                      {key}: {(value as number).toFixed(2)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {query && results.length === 0 && !isLoading && (
          <div className="no-results">
            <p>No results found for "{query}"</p>
            <p>Try different keywords or check your spelling.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchInterface;
