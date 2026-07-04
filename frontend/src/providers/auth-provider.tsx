"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { setTokenProvider } from "@/lib/api-client";

const TOKEN_KEY = "aarogya_access_token";

export interface AuthUser {
  sub: string;
  roles: string[];
}

interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function decodeTokenPayload(token: string): AuthUser | null {
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload));
    return { sub: decoded.sub, roles: decoded.roles ?? [] };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    isLoading: true,
  });

  // On mount, rehydrate from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      const user = decodeTokenPayload(stored);
      if (user) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setState({ isAuthenticated: true, user, token: stored, isLoading: false });
        setTokenProvider(() => stored);
        return;
      }
    }
    setState(s => ({ ...s, isLoading: false }));
  }, []);

  // Wire token provider so api-client auto-injects JWT header
  useEffect(() => {
    setTokenProvider(() => state.token);
  }, [state.token]);

  const login = (token: string, user: AuthUser) => {
    localStorage.setItem(TOKEN_KEY, token);
    setState({ isAuthenticated: true, user, token, isLoading: false });
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setState({ isAuthenticated: false, user: null, token: null, isLoading: false });
  };

  // Listen for 401 events dispatched by api-client
  useEffect(() => {
    const handler = () => logout();
    window.addEventListener("auth:unauthorized", handler);
    return () => window.removeEventListener("auth:unauthorized", handler);
  }, []);

  const hasRole = (role: string) => {
    return state.user?.roles?.includes(role) || state.user?.roles?.includes("admin") || false;
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
