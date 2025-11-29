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
      // Ошибка обрабатывается в useAuth
    }
  };

  const handleRegister = async (userData) => {
    try {
      await register(userData);
      setCurrentView('login');
    } catch (error) {
      // Ошибка обрабатывается в useAuth
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      await updateUser(userData);
    } catch (error) {
      throw error; // Пробрасываем ошибку для обработки в компоненте
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