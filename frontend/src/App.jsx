import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import LoadingSpinner from './components/LoadingSpinner';
import { useAuth } from './hooks/useAuth';
import './App.css';

function App() {
  const { 
    isAuthenticated, 
    user, 
    loading, 
    error, 
    login, 
    register, 
    updateUser,
    uploadAvatar,
    logout,
    clearError 
  } = useAuth();

  const [currentView, setCurrentView] = useState('login');
  const [transitionLoading, setTransitionLoading] = useState(false);

  useEffect(() => {
    if (error) {
      clearError();
    }
  }, [currentView]);

  const handleLogin = async (credentials) => {
    setTransitionLoading(true);
    try {
      await login(credentials);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleRegister = async (userData) => {
    setTransitionLoading(true);
    try {
      await register(userData);
      setCurrentView('login');
    } catch (error) {
      console.error('Register error:', error);
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleUpdateUser = async (userData) => {
    setTransitionLoading(true);
    try {
      await updateUser(userData);
    } catch (error) {
      throw error;
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleAvatarUpload = async (file) => {
    setTransitionLoading(true);
    try {
      await uploadAvatar(file);
    } catch (error) {
      throw error;
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleLogout = async () => {
    setTransitionLoading(true);
    try {
      await logout();
      setCurrentView('login');
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleSwitchToLogin = () => {
    setCurrentView('login');
  };

  const handleSwitchToRegister = () => {
    setCurrentView('register');
  };

  // Показываем спиннер при загрузке
  if (loading || transitionLoading) {
    return <LoadingSpinner message="Загрузка..." />;
  }

  return (
    <div className="App">
      {error && (
        <div className="error-message">
          {error}
          <button 
            onClick={clearError} 
            style={{
              marginLeft: '10px',
              background: 'transparent',
              border: 'none',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
      )}
      
      {isAuthenticated ? (
        <Dashboard 
          user={user} 
          onLogout={handleLogout}
          onUpdateUser={handleUpdateUser}
          onAvatarUpload={handleAvatarUpload}
        />
      ) : (
        currentView === 'login' ? (
          <Login 
            onSwitchToRegister={handleSwitchToRegister}
            onLogin={handleLogin}
            error={error}
          />
        ) : (
          <Register 
            onSwitchToLogin={handleSwitchToLogin}
            onRegister={handleRegister}
            error={error}
          />
        )
      )}
    </div>
  );
}

export default App;