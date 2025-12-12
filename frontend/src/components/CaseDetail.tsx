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
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4 sm:p-8 transition-opacity duration-200"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl max-w-5xl w-full max-h-[92vh] overflow-hidden relative shadow-2xl transform transition-all duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with gradient background */}
        <div className="sticky top-0 bg-indigo-600 px-8 py-6 flex justify-between items-center shadow-lg z-20">
          <div className="flex items-center gap-3">
            <div className="w-2 h-8 bg-white rounded-full"></div>
            <h2 className="text-2xl font-bold text-white m-0 line-clamp-2">
              {caseData?.name || (isLoading ? 'Loading...' : 'Case Details')}
            </h2>
          </div>
          <button
            className="bg-white/20 hover:bg-white/30 text-white border-none rounded-full w-10 h-10 text-xl cursor-pointer transition-all flex items-center justify-center leading-none backdrop-blur-sm hover:rotate-90 duration-300"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Content area with scroll */}
        <div className="overflow-y-auto max-h-[calc(92vh-88px)]">
          {isLoading && (
            <div className="p-20 text-center">
              <div className="inline-block w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-600 text-lg">Loading case details...</p>
            </div>
          )}

          {error && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <span className="text-3xl">⚠️</span>
              </div>
              <p className="text-red-600 text-lg font-medium">Error: {error}</p>
            </div>
          )}

          {caseData && (
            <div className="p-8 space-y-6">
              {/* Metadata Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {caseData.decision_date && (
                  <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-1">Decision Date</div>
                    <div className="text-gray-900 font-medium">{caseData.decision_date}</div>
                  </div>
                )}
                {caseData.court_name && (
                  <div className="bg-purple-50 p-4 rounded-xl border border-purple-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-xs font-semibold text-purple-600 uppercase tracking-wide mb-1">Court</div>
                    <div className="text-gray-900 font-medium line-clamp-2">{caseData.court_name}</div>
                  </div>
                )}
                {caseData.jurisdiction_name && (
                  <div className="bg-pink-50 p-4 rounded-xl border border-pink-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-xs font-semibold text-pink-600 uppercase tracking-wide mb-1">Jurisdiction</div>
                    <div className="text-gray-900 font-medium line-clamp-2">{caseData.jurisdiction_name}</div>
                  </div>
                )}
                {caseData.word_count && (
                  <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="text-xs font-semibold text-orange-600 uppercase tracking-wide mb-1">Word Count</div>
                    <div className="text-gray-900 font-medium">{caseData.word_count.toLocaleString()}</div>
                  </div>
                )}
              </div>

              {/* Parties Section */}
              {caseData.parties && (
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-6 bg-indigo-600 rounded-full"></div>
                    <h3 className="text-xl font-bold text-gray-900 m-0">Parties</h3>
                  </div>
                  <p className="m-0 leading-relaxed text-gray-700 text-base">{caseData.parties}</p>
                </div>
              )}

              {/* Judges Section */}
              {caseData.judges && (
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-6 bg-purple-600 rounded-full"></div>
                    <h3 className="text-xl font-bold text-gray-900 m-0">Judges</h3>
                  </div>
                  <p className="m-0 leading-relaxed text-gray-700 text-base">{caseData.judges}</p>
                </div>
              )}

              {/* Full Text Section */}
              {caseData.full_text && (
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-6 bg-pink-600 rounded-full"></div>
                    <h3 className="text-xl font-bold text-gray-900 m-0">Full Text</h3>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-xl whitespace-pre-wrap text-base leading-relaxed text-gray-800 max-h-[500px] overflow-y-auto">
                    {caseData.full_text}
                  </div>
                </div>
              )}

              {/* Footer */}
              <div className="mt-8 pt-6 border-t border-gray-200 flex items-center justify-center gap-2">
                <span className="text-xs text-gray-400 font-mono bg-gray-100 px-3 py-1.5 rounded-lg">
                  Document ID: {caseData.id}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;
