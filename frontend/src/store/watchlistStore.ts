import { create } from 'zustand';
import { watchlistApi } from '../api/watchlist';
import type { Watchlist, WatchlistCreate, WatchlistUpdate, StockAdd } from '../types';

interface WatchlistState {
  watchlists: Watchlist[];
  currentWatchlist: Watchlist | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchWatchlists: () => Promise<void>;
  fetchWatchlist: (id: string) => Promise<void>;
  createWatchlist: (data: WatchlistCreate) => Promise<Watchlist>;
  updateWatchlist: (id: string, data: WatchlistUpdate) => Promise<void>;
  deleteWatchlist: (id: string) => Promise<void>;
  addStock: (watchlistId: string, stock: StockAdd) => Promise<void>;
  removeStock: (watchlistId: string, symbol: string) => Promise<void>;
  createFromIndex: (indexName: string, watchlistName?: string) => Promise<Watchlist>;
  uploadExcel: (file: File, watchlistName?: string) => Promise<Watchlist>;
  clearError: () => void;
}

export const useWatchlistStore = create<WatchlistState>((set) => ({
  watchlists: [],
  currentWatchlist: null,
  loading: false,
  error: null,

  fetchWatchlists: async () => {
    set({ loading: true, error: null });
    try {
      const watchlists = await watchlistApi.getAll();
      set({ watchlists, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch watchlists',
        loading: false
      });
    }
  },

  fetchWatchlist: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const watchlist = await watchlistApi.getById(id);
      set({ currentWatchlist: watchlist, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch watchlist',
        loading: false
      });
    }
  },

  createWatchlist: async (data: WatchlistCreate) => {
    set({ loading: true, error: null });
    try {
      const newWatchlist = await watchlistApi.create(data);
      set((state) => ({
        watchlists: [...state.watchlists, newWatchlist],
        loading: false
      }));
      return newWatchlist;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create watchlist',
        loading: false
      });
      throw error;
    }
  },

  updateWatchlist: async (id: string, data: WatchlistUpdate) => {
    set({ loading: true, error: null });
    try {
      const updatedWatchlist = await watchlistApi.update(id, data);
      set((state) => ({
        watchlists: state.watchlists.map((w) =>
          w.id === id ? updatedWatchlist : w
        ),
        currentWatchlist: state.currentWatchlist?.id === id
          ? updatedWatchlist
          : state.currentWatchlist,
        loading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update watchlist',
        loading: false
      });
      throw error;
    }
  },

  deleteWatchlist: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await watchlistApi.delete(id);
      set((state) => ({
        watchlists: state.watchlists.filter((w) => w.id !== id),
        currentWatchlist: state.currentWatchlist?.id === id
          ? null
          : state.currentWatchlist,
        loading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete watchlist',
        loading: false
      });
      throw error;
    }
  },

  addStock: async (watchlistId: string, stock: StockAdd) => {
    set({ loading: true, error: null });
    try {
      const updatedWatchlist = await watchlistApi.addStock(watchlistId, stock);
      set((state) => ({
        watchlists: state.watchlists.map((w) =>
          w.id === watchlistId ? updatedWatchlist : w
        ),
        currentWatchlist: state.currentWatchlist?.id === watchlistId
          ? updatedWatchlist
          : state.currentWatchlist,
        loading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to add stock',
        loading: false
      });
      throw error;
    }
  },

  removeStock: async (watchlistId: string, symbol: string) => {
    set({ loading: true, error: null });
    try {
      const updatedWatchlist = await watchlistApi.removeStock(watchlistId, symbol);
      set((state) => ({
        watchlists: state.watchlists.map((w) =>
          w.id === watchlistId ? updatedWatchlist : w
        ),
        currentWatchlist: state.currentWatchlist?.id === watchlistId
          ? updatedWatchlist
          : state.currentWatchlist,
        loading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to remove stock',
        loading: false
      });
      throw error;
    }
  },

  createFromIndex: async (indexName: string, watchlistName?: string) => {
    set({ loading: true, error: null });
    try {
      const newWatchlist = await watchlistApi.createFromIndex({
        index_name: indexName,
        watchlist_name: watchlistName,
      });
      set((state) => ({
        watchlists: [...state.watchlists, newWatchlist],
        loading: false
      }));
      return newWatchlist;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create watchlist from index',
        loading: false
      });
      throw error;
    }
  },

  uploadExcel: async (file: File, watchlistName?: string) => {
    set({ loading: true, error: null });
    try {
      const newWatchlist = await watchlistApi.uploadExcel(file, watchlistName);
      set((state) => ({
        watchlists: [...state.watchlists, newWatchlist],
        loading: false
      }));
      return newWatchlist;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to upload Excel file',
        loading: false
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
