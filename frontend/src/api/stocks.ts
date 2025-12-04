import apiClient from './client';
import type { StockSearchResult, StockInfo } from '../types';

export const stocksApi = {
  // Search for stocks
  search: async (query: string): Promise<StockSearchResult[]> => {
    const response = await apiClient.get('/stocks/search', {
      params: { q: query },
    });
    return response.data;
  },

  // Get stock information
  getInfo: async (symbol: string): Promise<StockInfo> => {
    const response = await apiClient.get(`/stocks/${symbol}/info`);
    return response.data;
  },

  // Get historical data
  getHistorical: async (
    symbol: string,
    period: string = '1mo',
    interval: string = '1d'
  ): Promise<any> => {
    const response = await apiClient.get(`/stocks/${symbol}/historical`, {
      params: { period, interval },
    });
    return response.data;
  },

  // Validate stock symbol
  validate: async (symbol: string): Promise<{ symbol: string; valid: boolean }> => {
    const response = await apiClient.get(`/stocks/${symbol}/validate`);
    return response.data;
  },
};
