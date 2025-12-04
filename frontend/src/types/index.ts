// User types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
  is_active: boolean;
}

export interface UserRegister {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Watchlist types
export interface Stock {
  symbol: string;
  name?: string;
  added_at: string;
}

export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  stocks: Stock[];
  created_at: string;
  updated_at: string;
  is_default: boolean;
}

export interface WatchlistCreate {
  name: string;
  description?: string;
  stocks?: StockAdd[];
}

export interface WatchlistUpdate {
  name?: string;
  description?: string;
}

export interface StockAdd {
  symbol: string;
  name?: string;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}

export interface StockInfo {
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
  industry: string;
  marketCap: number;
  currentPrice: number;
  previousClose: number;
  dayHigh: number;
  dayLow: number;
  volume: number;
  averageVolume: number;
}

export interface IndexWatchlistCreate {
  index_name: string;
  watchlist_name?: string;
}

// API Response types
export interface ApiError {
  detail: string;
}
