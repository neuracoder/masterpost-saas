// Mock authentication for development
// In production, replace with proper JWT handling

import { apiClient } from './api';

class MockAuth {
  private token: string | null = null;

  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    // Mock login - accept any credentials for demo
    this.token = 'mock_jwt_token_for_development';

    const user = {
      id: 'demo_user_123',
      email,
      name: 'Demo User',
      plan: 'pro'
    };

    // Set auth token in API client
    apiClient.setAuthToken(this.token);

    // Store in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('user', JSON.stringify(user));
    }

    return { token: this.token, user };
  }

  async logout(): Promise<void> {
    this.token = null;

    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;

    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }

    return null;
  }

  getUser(): any | null {
    if (typeof window !== 'undefined') {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    }

    return null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Initialize auth state from localStorage
  init(): void {
    const token = this.getToken();
    if (token) {
      this.token = token;
      apiClient.setAuthToken(token);
    }
  }
}

export const mockAuth = new MockAuth();

// Auto-initialize on import
if (typeof window !== 'undefined') {
  mockAuth.init();
}