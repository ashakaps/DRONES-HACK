// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/authService.js';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  console.log("user:", user);
  useEffect(() => {
    const token = localStorage.getItem('token');
    (async () => {
        if (token) {
            try {
                const me = await authService.getProfile();
                setUser(me);
            } catch {
                localStorage.removeItem('token');
            }
        }
    setLoading(false);
    }) ();
  }, []);

  const login = async (email, password) => {
    try {
      const auth_response = await authService.login(email, password);
    console.log("auth_response:", auth_response);
    console.log("access_token:", auth_response.access_token);
    localStorage.setItem('token', auth_response.access_token);
      
      const me = await authService.getProfile();
        setUser(me);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = React.useMemo( () => ({
    user,
    login,
    logout,
    loading,
    isAdmin: user?.role === 'admin',
    isOperator: user?.role === 'operator'
  }), [user, loading]);

  return (
    <AuthContext.Provider value={value}>
      {loading ? <div className="splash">Загрузка...</div> : children}
    </AuthContext.Provider>
  );
};
