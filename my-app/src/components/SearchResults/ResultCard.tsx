import React from 'react';
import { CaseResult } from '../../types';
import './ResultCard.css';

interface ResultCardProps {
  result: CaseResult;
  onCaseClick: (caseId: string) => void;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, onCaseClick }) => {
  return (
    <div
      className="result-card"
      onClick={() => onCaseClick(result.id)}
    >
      <div className="result-header">
        <h3 className="result-title">{result.name || 'Untitled Case'}</h3>
        <span className="result-score">Score: {result.score?.toFixed(2)}</span>
      </div>

      <div className="result-meta">
        {result.decision_date && (
          <span className="meta-item">
            <strong>Date:</strong> {result.decision_date}
          </span>
        )}
        {result.court_name && (
          <span className="meta-item">
            <strong>Court:</strong> {result.court_name}
          </span>
        )}
        {result.jurisdiction_name && (
          <span className="meta-item">
            <strong>Jurisdiction:</strong> {result.jurisdiction_name}
          </span>
        )}
        {result.word_count && (
          <span className="meta-item">
            <strong>Words:</strong> {result.word_count.toLocaleString()}
          </span>
        )}
      </div>

      <div className="result-footer">
        <span className="doc-id">ID: {result.id}</span>
        <span className="click-hint">Click to view details →</span>
      </div>
    </div>
  );
};

export default ResultCard;
