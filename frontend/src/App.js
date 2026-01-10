import React, { useState, useEffect } from 'react';
import { Container, Alert, Badge, OverlayTrigger, Tooltip } from 'react-bootstrap';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import ResultsList from './components/ResultsList';
import LoadingSpinner from './components/LoadingSpinner';
import { searchProjects, getStats } from './services/api';

function App() {
  const [results, setResults] = useState(null);
  const [queryTime, setQueryTime] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [isConnected, setIsConnected] = useState(null);

  // Check backend connection and load stats on mount
  useEffect(() => {
    async function checkConnection() {
      try {
        const statsData = await getStats();
        if (statsData.status === 'success') {
          setStats(statsData.data);
          setIsConnected(true);
        }
      } catch (err) {
        console.error('Backend connection error:', err);
        setIsConnected(false);
      }
    }
    checkConnection();
  }, []);

  const handleSearch = async (params) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setQueryTime(null);

    try {
      const response = await searchProjects(params);

      if (response.status === 'success') {
        setResults(response.results);
        setQueryTime(response.query_time_ms);
      } else {
        setError(response.message || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('Failed to connect to the server. Please ensure the backend is running.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <Container>
        {/* Connection Status */}
        {isConnected === false && (
          <Alert variant="warning" className="mb-4">
            <Alert.Heading>Backend Not Connected</Alert.Heading>
            <p className="mb-0">
              Unable to connect to the backend server. Please ensure the Flask server is running on port 5001.
            </p>
            <hr />
            <p className="mb-0">
              <code>python -m backend.app</code>
            </p>
          </Alert>
        )}

        {/* Stats Info */}
        {stats && stats.total_documents > 0 && (
          <div className="mb-2 text-end" style={{ fontSize: '0.8rem' }}>
            <OverlayTrigger
              placement="bottom"
              overlay={
                <Tooltip>
                  Total historical bid spreadsheets indexed from 2016-2024
                </Tooltip>
              }
            >
              <Badge bg="info" className="me-2" style={{ cursor: 'help' }}>
                {stats.total_documents.toLocaleString()} indexed
              </Badge>
            </OverlayTrigger>
            {stats.documents_with_training_labels > 0 && (
              <OverlayTrigger
                placement="bottom"
                overlay={
                  <Tooltip>
                    Projects where experts noted similar past bids in the spreadsheet.
                    Not all spreadsheets have this data filled in.
                  </Tooltip>
                }
              >
                <Badge bg="secondary" style={{ cursor: 'help' }}>
                  {stats.documents_with_training_labels.toLocaleString()} with training labels
                </Badge>
              </OverlayTrigger>
            )}
          </div>
        )}

        {/* No Data Warning */}
        {stats && stats.total_documents === 0 && (
          <Alert variant="info" className="mb-4">
            <Alert.Heading>No Data Indexed</Alert.Heading>
            <p>
              The vector store is empty. Please run the data ingestion script to index your bid spreadsheets:
            </p>
            <code>python scripts/ingest_data.py --clear</code>
          </Alert>
        )}

        {/* Search Form */}
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Loading State */}
        {isLoading && (
          <div className="mt-4">
            <LoadingSpinner message="Searching for similar projects..." />
          </div>
        )}

        {/* Results */}
        {!isLoading && (
          <ResultsList results={results} queryTime={queryTime} error={error} />
        )}
      </Container>

      {/* Footer */}
      <footer className="text-center py-4 mt-5 text-muted">
        <small>Axiom Intelligent Proposal Assistant v1.0</small>
      </footer>
    </div>
  );
}

export default App;
