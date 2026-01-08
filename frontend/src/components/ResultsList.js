import React from 'react';
import { ListGroup, Badge, Alert } from 'react-bootstrap';

function getSimilarityClass(score) {
  if (score >= 0.7) return 'similarity-high';
  if (score >= 0.4) return 'similarity-medium';
  return 'similarity-low';
}

function formatScore(score) {
  return `${(score * 100).toFixed(1)}%`;
}

function ResultsList({ results, queryTime, error }) {
  if (error) {
    return (
      <div className="results-container p-4 mt-4">
        <Alert variant="danger">
          <Alert.Heading>Search Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  if (results.length === 0) {
    return (
      <div className="results-container p-4 mt-4">
        <Alert variant="info">
          No similar projects found. Try adjusting your search parameters.
        </Alert>
      </div>
    );
  }

  return (
    <div className="results-container p-4 mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">Similar Historical Bids</h5>
        <div>
          <Badge bg="secondary" className="stats-badge me-2">
            {results.length} result{results.length !== 1 ? 's' : ''}
          </Badge>
          {queryTime && (
            <Badge bg="light" text="dark" className="stats-badge">
              {queryTime}ms
            </Badge>
          )}
        </div>
      </div>

      <ListGroup>
        {results.map((result, index) => (
          <ListGroup.Item
            key={result.project_id}
            className="result-item d-flex justify-content-between align-items-center"
          >
            <div className="d-flex align-items-center">
              <span className="text-muted me-3" style={{ minWidth: '24px' }}>
                {index + 1}.
              </span>
              <div>
                <div className="fw-medium">{result.filename}</div>
                <small className="text-muted">
                  Project ID: {result.project_id} | Year: {result.year}
                </small>
              </div>
            </div>
            <Badge
              className={`similarity-badge ${getSimilarityClass(result.similarity_score)}`}
            >
              {formatScore(result.similarity_score)}
            </Badge>
          </ListGroup.Item>
        ))}
      </ListGroup>

      <div className="mt-3">
        <small className="text-muted">
          Results are ranked by similarity score (best matches first).
          Scores consider project parameters and favor more recent bids.
        </small>
      </div>
    </div>
  );
}

export default ResultsList;
