import React from 'react';
import { CaseResult } from '@/types';

interface ResultCardProps {
  result: CaseResult;
  onCaseClick: (caseId: string) => void;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, onCaseClick }) => {
  return (
    <div
      className="bg-white border border-gray-300 rounded-lg p-6 transition-all cursor-pointer hover:shadow-lg hover:border-indigo-600 hover:-translate-y-0.5"
      onClick={() => onCaseClick(result.id)}
    >
      <div className="flex justify-between items-start mb-3 gap-4">
        <h3 className="m-0 text-xl text-indigo-600 flex-1 leading-snug">
          {result.name || 'Untitled Case'}
        </h3>
        <span className="text-sm text-gray-600 bg-gray-100 px-2.5 py-1 rounded-lg whitespace-nowrap">
          Score: {result.score?.toFixed(2)}
        </span>
      </div>

      <div className="flex flex-wrap gap-4 mb-3 text-sm">
        {result.decision_date && (
          <span className="text-gray-700">
            <strong className="text-gray-900 mr-1">Date:</strong> {result.decision_date}
          </span>
        )}
        {result.court_name && (
          <span className="text-gray-700">
            <strong className="text-gray-900 mr-1">Court:</strong> {result.court_name}
          </span>
        )}
        {result.jurisdiction_name && (
          <span className="text-gray-700">
            <strong className="text-gray-900 mr-1">Jurisdiction:</strong> {result.jurisdiction_name}
          </span>
        )}
        {result.word_count && (
          <span className="text-gray-700">
            <strong className="text-gray-900 mr-1">Words:</strong> {result.word_count.toLocaleString()}
          </span>
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
        <span className="text-xs text-gray-400 font-mono">ID: {result.id}</span>
        <span className="text-indigo-600 text-sm font-medium">Click to view details →</span>
      </div>
    </div>
  );
};

export default ResultCard;
