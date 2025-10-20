import React from 'react';
import { useCaseDetail } from '@/hooks';

interface CaseDetailProps {
  caseId: string;
  onClose: () => void;
}

const CaseDetail: React.FC<CaseDetailProps> = ({ caseId, onClose }) => {
  const { caseData, isLoading, error } = useCaseDetail(caseId);

  if (!caseId) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-[1000] p-8" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto relative shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <button
          className="absolute top-4 right-4 bg-gray-100 text-gray-600 border-none rounded-full w-10 h-10 text-2xl cursor-pointer z-10 transition-all flex items-center justify-center leading-none hover:bg-red-500 hover:text-white"
          onClick={onClose}
        >
          ✕
        </button>

        {isLoading && (
          <div className="p-12 text-center text-lg">Loading case details...</div>
        )}

        {error && (
          <div className="p-12 text-center text-lg text-red-600">Error: {error}</div>
        )}

        {caseData && (
          <div className="p-10 pt-14">
            <h2 className="text-3xl text-gray-900 m-0 mb-6 leading-snug">
              {caseData.name || 'Untitled Case'}
            </h2>

            <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4 p-4 bg-gray-50 rounded-lg mb-6">
              {caseData.decision_date && (
                <div className="text-sm text-gray-700">
                  <strong className="text-gray-900 block mb-1">Decision Date:</strong> {caseData.decision_date}
                </div>
              )}
              {caseData.court_name && (
                <div className="text-sm text-gray-700">
                  <strong className="text-gray-900 block mb-1">Court:</strong> {caseData.court_name}
                </div>
              )}
              {caseData.jurisdiction_name && (
                <div className="text-sm text-gray-700">
                  <strong className="text-gray-900 block mb-1">Jurisdiction:</strong> {caseData.jurisdiction_name}
                </div>
              )}
              {caseData.word_count && (
                <div className="text-sm text-gray-700">
                  <strong className="text-gray-900 block mb-1">Word Count:</strong> {caseData.word_count.toLocaleString()}
                </div>
              )}
            </div>

            {caseData.parties && (
              <div className="mb-6">
                <h3 className="text-xl text-gray-800 m-0 mb-3 pb-2 border-b-2 border-indigo-600">Parties</h3>
                <p className="m-0 leading-relaxed text-gray-700">{caseData.parties}</p>
              </div>
            )}

            {caseData.judges && (
              <div className="mb-6">
                <h3 className="text-xl text-gray-800 m-0 mb-3 pb-2 border-b-2 border-indigo-600">Judges</h3>
                <p className="m-0 leading-relaxed text-gray-700">{caseData.judges}</p>
              </div>
            )}

            {caseData.full_text && (
              <div className="mb-6">
                <h3 className="text-xl text-gray-800 m-0 mb-3 pb-2 border-b-2 border-indigo-600">Full Text</h3>
                <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-indigo-600 whitespace-pre-wrap text-base leading-relaxed text-gray-800 max-h-[500px] overflow-y-auto">
                  {caseData.full_text}
                </div>
              </div>
            )}

            <div className="mt-8 pt-4 border-t border-gray-200 text-center text-gray-400">
              <small>Document ID: {caseData.id}</small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseDetail;
