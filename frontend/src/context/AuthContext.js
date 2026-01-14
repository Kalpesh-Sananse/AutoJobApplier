import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (token) {
      // If we have a stored user, set it immediately (optimistic)
      if (storedUser) {
        try {
          const user = JSON.parse(storedUser);
          setUser(user);
          setIsAuthenticated(true);
        } catch (e) {
          // Invalid stored user, clear it
          localStorage.removeItem('user');
        }
      }
      
      // Then verify with backend
      try {
        const response = await api.get('/auth/me');
        if (response.data.success) {
          setUser(response.data.data.user);
          setIsAuthenticated(true);
          // Update stored user
          localStorage.setItem('user', JSON.stringify(response.data.data.user));
        } else {
          // Token invalid, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        // Only clear on 401 (unauthorized), not on network errors
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
          setIsAuthenticated(false);
        } else if (!error.response) {
          // Network error (backend not running), keep token but log warning
          console.warn('Backend not reachable, using cached authentication');
          // Keep the optimistic state we set above
        }
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data && response.data.success) {
        const { user, token } = response.data.data;
        
        // Store token in localStorage
        // Note: In production, consider using http-only cookies for better security
        // localStorage is used here for simplicity, but http-only cookies are more secure
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        // Update state immediately
        setUser(user);
        setIsAuthenticated(true);
        setLoading(false); // Ensure loading is false after successful login
        
        return { success: true };
      }
      return {
        success: false,
        message: response.data?.message || 'Login failed. Please try again.'
      };
    } catch (error) {
      console.error('Login error:', error);
      
      // Handle network errors
      if (!error.response) {
        return {
          success: false,
          message: 'Cannot connect to server. Please make sure the backend is running.'
        };
      }
      
      // Handle API errors
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.errors?.[0]?.msg ||
                          'Login failed. Please check your credentials and try again.';
      
      return {
        success: false,
        message: errorMessage
      };
    }
  };

  const register = async (email, password) => {
    try {
      const response = await api.post('/auth/register', { email, password });
      if (response.data && response.data.success) {
        const { user, token } = response.data.data;
        
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        // Update state immediately
        setUser(user);
        setIsAuthenticated(true);
        setLoading(false); // Ensure loading is false after successful registration
        
        return { success: true };
      }
      return {
        success: false,
        message: response.data?.message || 'Registration failed. Please try again.'
      };
    } catch (error) {
      console.error('Registration error:', error);
      
      // Handle network errors
      if (!error.response) {
        return {
          success: false,
          message: 'Cannot connect to server. Please make sure the backend is running.'
        };
      }
      
      // Handle API errors
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.errors?.[0]?.msg ||
                          'Registration failed. Please try again.';
      
      return {
        success: false,
        message: errorMessage
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
