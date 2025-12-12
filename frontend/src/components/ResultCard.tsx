import React from 'react';
import { CaseResult } from '@/types';

interface ResultCardProps {
  result: CaseResult;
  onCaseClick: (caseId: string) => void;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, onCaseClick }) => {
  return (
    <div
      className="bg-white border border-gray-300 rounded-lg p-6 ... hover:shadow-lg hover:border-indigo-600 hover:-translate-y-0.5"
      onClick={() => onCaseClick(result.id)}
    >
      <div className="mb-3">
        <h3 className="m-0 text-xl text-indigo-600 leading-snug">
          {result.name}
        </h3>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-600">
        {result.decision_date && (
          <span>
            <strong className="text-gray-900 mr-1">Date:</strong>{' '}
            {new Date(result.decision_date).toLocaleDateString()}
          </span>
        )}
        {result.court_name && (
          <span>
            <strong className="text-gray-900 mr-1">Court:</strong>{' '}
            {result.court_name}
          </span>
        )}
        {result.jurisdiction_name && (
          <span>
            <strong className="text-gray-900 mr-1">Jurisdiction:</strong>{' '}
            {result.jurisdiction_name}
          </span>
        )}
        {typeof result.word_count === 'number' && (
          <span>
            <strong className="text-gray-900 mr-1">Words:</strong>{' '}
            {result.word_count.toLocaleString()}
          </span>
        )}
      </div>

      {result.snippet && (
        <div className="mt-3 text-sm text-gray-700 leading-relaxed">
          {/* snippet comes from backend with <mark> tags for highlights */}
          <span dangerouslySetInnerHTML={{ __html: result.snippet }} />
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
        <span className="text-xs text-gray-400 font-mono">
          ID: {result.id}
        </span>
        <span className="text-indigo-600 text-sm font-medium">
          Click to view details →
        </span>
      </div>
    </div>
  );
};

export default ResultCard;
