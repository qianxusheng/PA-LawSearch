// Search method types
export type SearchMethod = 'bm25' | 'dense' | 'dense_rerank' | 'bm25_rerank';

export interface SearchFilters {
  court?: string;
  startDate?: string;
  endDate?: string;
}

export interface CaseResult {
  id: string;
  name: string;
  score: number;
  decision_date?: string;
  court_name?: string;
  jurisdiction_name?: string;
  word_count?: number;
  // highlight snippet returned by backend (contains <mark> tags)
  snippet?: string;
}

export interface SearchResponse {
  total: number;
  page: number;
  size: number;
  method?: SearchMethod;
  results: CaseResult[];
}

export interface CaseDetail {
  id: string;
  name: string;
  decision_date?: string;
  court_name?: string;
  jurisdiction_name?: string;
  word_count?: number;
  parties?: string;
  judges?: string;
  full_text?: string;
}
