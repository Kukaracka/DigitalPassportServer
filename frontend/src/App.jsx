import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
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

  useEffect(() => {
    if (error) {
      clearError();
    }
  }, [currentView]);

  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  const handleRegister = async (userData) => {
    try {
      await register(userData);
      setCurrentView('login');
    } catch (error) {
      console.error('Register error:', error);
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      await updateUser(userData);
    } catch (error) {
      throw error; 
    }
  };

  const handleAvatarUpload = async (file) => {
    try {
      await uploadAvatar(file);
    } catch (error) {
      throw error;
    }
  };

  const handleLogout = async () => {
    await logout();
    setCurrentView('login');
  };

  const handleSwitchToLogin = () => {
    setCurrentView('login');
  };

  const handleSwitchToRegister = () => {
    setCurrentView('register');
  };

  console.log('🔄 App render - user:', user);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>
    );
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