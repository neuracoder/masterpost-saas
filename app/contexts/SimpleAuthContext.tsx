'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  email: string | null;
  accessCode: string | null;
  credits: number;
  isAuthenticated: boolean;
  login: (email: string, code: string) => Promise<boolean>;
  logout: () => void;
  refreshCredits: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function SimpleAuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [accessCode, setAccessCode] = useState<string | null>(null);
  const [credits, setCredits] = useState(0);

  useEffect(() => {
    // Load from localStorage on mount
    const savedEmail = localStorage.getItem('mp_email');
    const savedCode = localStorage.getItem('mp_access_code');

    if (savedEmail && savedCode) {
      setEmail(savedEmail);
      setAccessCode(savedCode);
      // Fetch credits immediately on mount
      const fetchCredits = async () => {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const response = await fetch("/api/v1/auth/credits", {
            headers: { 'x-user-email': savedEmail }
          });

          if (response.ok) {
            const data = await response.json();
            setCredits(data.credits);
          }
        } catch (error) {
          console.error('Error fetching credits:', error);
        }
      };
      fetchCredits();
    }
  }, []);

  const login = async (email: string, code: string): Promise<boolean> => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch("/api/v1/test/login", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, access_code: code })
      });

      if (response.ok) {
        const data = await response.json();
        setEmail(email);
        setAccessCode(code);
        setCredits(data.credits);

        localStorage.setItem('mp_email', email);
        localStorage.setItem('mp_access_code', code);

        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    setEmail(null);
    setAccessCode(null);
    setCredits(0);
    localStorage.removeItem('mp_email');
    localStorage.removeItem('mp_access_code');
  };

  const refreshCredits = async () => {
    if (!email) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch("/api/v1/auth/credits", {
        headers: { 'x-user-email': email }
      });

      if (response.ok) {
        const data = await response.json();
        setCredits(data.credits);
      }
    } catch (error) {
      console.error('Error refreshing credits:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        email,
        accessCode,
        credits,
        isAuthenticated: !!email && !!accessCode,
        login,
        logout,
        refreshCredits
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useSimpleAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useSimpleAuth must be used within SimpleAuthProvider');
  }
  return context;
};
