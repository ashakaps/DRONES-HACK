import React, { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

type Role = "admin" | "operator";
type User = {
  id: number; email: string; role: Role;
  created_at: string; last_login_at?: string | null;
};

type AuthState = {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const AuthCtx = createContext<AuthState>(null!);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const refreshMe = async () => {
    try {
      const { data } = await api.get<User>("/auth/me");
      setUser(data);
    } catch {
      setUser(null);
    }
  };

  const login = async (email: string, password: string) => {
    const { data } = await api.post<{access_token: string}>("/auth/login", { email, password });
    localStorage.setItem("token", data.access_token);
    await refreshMe();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  useEffect(() => { if (localStorage.getItem("token")) refreshMe(); }, []);

  return (
    <AuthCtx.Provider value={{ user, login, logout, refreshMe }}>
      {children}
    </AuthCtx.Provider>
  );
};

export const useAuth = () => useContext(AuthCtx);
