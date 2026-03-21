import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Загрузка...' }) => {
  return (
    <div className="loading-overlay">
      <div className="loading-spinner-container">
        <div className="loading-spinner"></div>
        <p className="loading-message">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;