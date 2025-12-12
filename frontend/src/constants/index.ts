export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  DEFAULT_PAGE: 1,
} as const;

export const ROUTES = {
  HOME: '/',
  SEARCH: '/search',
} as const;
