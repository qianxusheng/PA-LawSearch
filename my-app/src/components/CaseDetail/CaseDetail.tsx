import React, { useEffect, useState } from 'react';
import { CaseDetail as CaseDetailType } from '../../types';
import './CaseDetail.css';

interface CaseDetailProps {
  caseId: string;
  onClose: () => void;
}

const CaseDetail: React.FC<CaseDetailProps> = ({ caseId, onClose }) => {
  const [caseData, setCaseData] = useState<CaseDetailType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCase = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`http://localhost:5000/cases/${caseId}`);

        if (!response.ok) {
          throw new Error('Failed to fetch case details');
        }

        const data = await response.json();
        setCaseData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  if (!caseId) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>

        {isLoading && (
          <div className="modal-loading">Loading case details...</div>
        )}

        {error && (
          <div className="modal-error">Error: {error}</div>
        )}

        {caseData && (
          <div className="case-detail">
            <h2 className="case-title">{caseData.name || 'Untitled Case'}</h2>

            <div className="case-metadata">
              {caseData.decision_date && (
                <div className="metadata-item">
                  <strong>Decision Date:</strong> {caseData.decision_date}
                </div>
              )}
              {caseData.court_name && (
                <div className="metadata-item">
                  <strong>Court:</strong> {caseData.court_name}
                </div>
              )}
              {caseData.jurisdiction_name && (
                <div className="metadata-item">
                  <strong>Jurisdiction:</strong> {caseData.jurisdiction_name}
                </div>
              )}
              {caseData.word_count && (
                <div className="metadata-item">
                  <strong>Word Count:</strong> {caseData.word_count.toLocaleString()}
                </div>
              )}
            </div>

            {caseData.parties && (
              <div className="case-section">
                <h3>Parties</h3>
                <p>{caseData.parties}</p>
              </div>
            )}

            {caseData.judges && (
              <div className="case-section">
                <h3>Judges</h3>
                <p>{caseData.judges}</p>
              </div>
            )}

            {caseData.full_text && (
              <div className="case-section">
                <h3>Full Text</h3>
                <div className="case-full-text">
                  {caseData.full_text}
                </div>
              </div>
            )}

            <div className="case-footer">
              <small>Document ID: {caseData.id}</small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseDetail;
