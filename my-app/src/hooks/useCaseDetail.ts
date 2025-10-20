import { useState, useEffect } from 'react';
import { getCaseDetail } from '../api';
import { CaseDetail } from '../types';

export const useCaseDetail = (caseId: string | null) => {
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) {
      setCaseData(null);
      return;
    }

    const fetchCase = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await getCaseDetail(caseId);
        setCaseData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCase();
  }, [caseId]);

  return { caseData, isLoading, error };
};
