import apiClient from './client';
import type {
  Watchlist,
  WatchlistCreate,
  WatchlistUpdate,
  StockAdd,
  IndexWatchlistCreate,
} from '../types';

export const watchlistApi = {
  // Get all watchlists
  getAll: async (): Promise<Watchlist[]> => {
    const response = await apiClient.get('/watchlists');
    return response.data;
  },

  // Get a specific watchlist
  getById: async (id: string): Promise<Watchlist> => {
    const response = await apiClient.get(`/watchlists/${id}`);
    return response.data;
  },

  // Create a new watchlist
  create: async (data: WatchlistCreate): Promise<Watchlist> => {
    const response = await apiClient.post('/watchlists', data);
    return response.data;
  },

  // Update watchlist metadata
  update: async (id: string, data: WatchlistUpdate): Promise<Watchlist> => {
    const response = await apiClient.put(`/watchlists/${id}`, data);
    return response.data;
  },

  // Delete a watchlist
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/watchlists/${id}`);
  },

  // Add stock to watchlist
  addStock: async (watchlistId: string, stock: StockAdd): Promise<Watchlist> => {
    const response = await apiClient.post(`/watchlists/${watchlistId}/stocks`, stock);
    return response.data;
  },

  // Remove stock from watchlist
  removeStock: async (watchlistId: string, symbol: string): Promise<Watchlist> => {
    const response = await apiClient.delete(`/watchlists/${watchlistId}/stocks/${symbol}`);
    return response.data;
  },

  // Create watchlist from index
  createFromIndex: async (data: IndexWatchlistCreate): Promise<Watchlist> => {
    const response = await apiClient.post('/watchlists/from-index', data);
    return response.data;
  },

  // Upload Excel file to create watchlist
  uploadExcel: async (file: File, watchlistName?: string): Promise<Watchlist> => {
    const formData = new FormData();
    formData.append('file', file);
    if (watchlistName) {
      formData.append('watchlist_name', watchlistName);
    }

    const response = await apiClient.post('/upload/excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Append Excel file to existing watchlist
  appendExcel: async (watchlistId: string, file: File): Promise<Watchlist> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(`/upload/excel/append/${watchlistId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
