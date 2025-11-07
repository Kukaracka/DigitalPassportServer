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
    logout,
    clearError 
  } = useAuth();

  const [currentView, setCurrentView] = useState('login');

  // Очищаем ошибки при переключении между формами
  useEffect(() => {
    if (error) {
      clearError();
    }
  }, [currentView]);

  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
      // Успешный логин автоматически перенаправит в dashboard через состояние isAuthenticated
    } catch (error) {
      // Ошибка уже обработана в хуке
      console.error('Login failed:', error);
    }
  };

  const handleRegister = async (userData) => {
    try {
      await register(userData);
      // После успешной регистрации переключаем на форму логина
      setCurrentView('login');
    } catch (error) {
      // Ошибка уже обработана в хуке
      console.error('Registration failed:', error);
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

  // Показываем загрузку только при первоначальной проверке auth
  if (loading && !isAuthenticated) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Проверка авторизации...</p>
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
        <Dashboard user={user} onLogout={handleLogout} />
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