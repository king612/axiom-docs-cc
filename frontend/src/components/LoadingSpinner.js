import React from 'react';
import { Spinner } from 'react-bootstrap';

function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-spinner">
      <Spinner animation="border" role="status" variant="primary">
        <span className="visually-hidden">{message}</span>
      </Spinner>
      <span className="ms-3 text-muted">{message}</span>
    </div>
  );
}

export default LoadingSpinner;
