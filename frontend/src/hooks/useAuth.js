import { useState, useEffect } from 'react';
import AuthAPI from '../services/authAPI';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      setLoading(true);
      await AuthAPI.checkAuth();
      setIsAuthenticated(true);
      
      const userData = await AuthAPI.getCurrentUser();
      setUser(userData);
      
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setError(null);
      setLoading(true);
      
      const result = await AuthAPI.login(credentials);
      setIsAuthenticated(true);
      
      const userData = await AuthAPI.getCurrentUser();
      setUser(userData);
      
      return result;
    } catch (error) {
      const errorMessage = error.message;
      setError(errorMessage);
      setIsAuthenticated(false);
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);
      
      const result = await AuthAPI.register(userData);
      return result;
    } catch (error) {
      const errorMessage = error.message;
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
    document.cookie = 'my_access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  };

  const clearError = () => {
    setError(null);
  };

  return {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth,
    clearError
  };
};