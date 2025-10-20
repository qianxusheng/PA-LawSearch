import { API_BASE_URL, PAGINATION } from '../constants';
import { SearchResponse, CaseDetail } from '../types';

export const getCases = async (
  query: string,
  page: number = PAGINATION.DEFAULT_PAGE,
  size: number = PAGINATION.DEFAULT_PAGE_SIZE
): Promise<SearchResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/cases?query=${encodeURIComponent(query)}&size=${size}&page=${page}`
  );

  if (!response.ok) {
    throw new Error('Search failed');
  }

  return response.json();
};

export const getCaseDetail = async (caseId: string): Promise<CaseDetail> => {
  const response = await fetch(`${API_BASE_URL}/cases/${caseId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch case details');
  }

  return response.json();
};
