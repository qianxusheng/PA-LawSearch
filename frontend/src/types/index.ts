// Search method types
export type SearchMethod = 'bm25' | 'dense' | 'dense_rerank';

// backend api response type
export interface SearchResponse {
  total: number;
  page: number;
  size: number;
  method?: SearchMethod;
  results: CaseResult[];
}

export interface CaseResult {
  id: string;
  name: string;
  score: number;
  decision_date?: string;
  court_name?: string;
  jurisdiction_name?: string;
  word_count?: number;
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
