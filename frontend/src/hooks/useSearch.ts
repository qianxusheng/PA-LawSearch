import { useState } from 'react';
import { getCases } from '@/api';
import { CaseResult, SearchMethod } from '@/types';

export const useSearch = () => {
  const [results, setResults] = useState<CaseResult[] | null>(null);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (query: string, method: SearchMethod = 'bm25', page: number = 1) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getCases(query, page, 10, method);
      setResults(data.results);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return { results, total, isLoading, error, search };
};
