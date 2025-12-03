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

// API Response types
export interface ApiError {
  detail: string;
}
