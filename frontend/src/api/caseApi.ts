import { API_BASE_URL, PAGINATION } from '../constants';
import { SearchResponse, CaseDetail, SearchMethod, SearchFilters } from '../types';

export const getCases = async (
  query: string,
  page: number = PAGINATION.DEFAULT_PAGE,
  size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  method: SearchMethod = 'bm25',
  filters?: SearchFilters
): Promise<SearchResponse> => {
  const params = new URLSearchParams({
    query,
    size: String(size),
    page: String(page),
    method,
  });

  if (filters?.court) {
    params.append('court', filters.court);
  }
  if (filters?.startDate) {
    params.append('start_date', filters.startDate);
  }
  if (filters?.endDate) {
    params.append('end_date', filters.endDate);
  }

  const response = await fetch(`${API_BASE_URL}/cases?${params.toString()}`);

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
