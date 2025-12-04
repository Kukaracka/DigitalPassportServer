import React, { useState } from 'react';
import Profile from './Profile';
import Products from './Products';
import './Dashboard.css';

const Dashboard = ({ user, onLogout, onUpdateUser }) => {
  const [currentView, setCurrentView] = useState('dashboard');

  const currentUser = user;

  if (currentView === 'profile') {
    return (
      <Profile 
        user={user} 
        onBack={() => setCurrentView('dashboard')}
        onUpdateUser={onUpdateUser}
      />
    );
  }

  if (currentView === 'products') {
    return (
      <Products 
        user={user}
        onBack={() => setCurrentView('dashboard')}
      />
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>DigitalPassport</h1>
        <div className="user-info">
          <span>Добро пожаловать, {currentUser?.first_name || 'Пользователь'}!</span>
          <button onClick={onLogout} className="logout-button">
            Выйти
          </button>
        </div>
      </header>
      
      <main className="dashboard-content">
        <div className="dashboard-welcome">
          <h2>Добро пожаловать в ваш цифровой паспорт!</h2>
          <p>Управляйте вашими цифровыми документами и данными в одном безопасном месте</p>
        </div>
        
        <div 
          className="dashboard-card clickable-card"
          onClick={() => setCurrentView('profile')}
        >
          <h3>👤 Профиль</h3>
          <p>Просмотр и редактирование личной информации</p>
          <div className="card-hint">Нажмите чтобы открыть</div>
        </div>
        
        <div 
          className="dashboard-card clickable-card"
          onClick={() => setCurrentView('products')}
        >
          <h3>📦 Мои продукты</h3>
          <p>Управление вашей техникой и устройствами</p>
          <div className="card-hint">Нажмите чтобы открыть</div>
        </div>
        
        <div className="dashboard-card">
          <h3>📈 История</h3>
          <p>История действий и последние операции с вашими документами</p>
        </div>
        
        <div className="dashboard-card">
          <h3>🛠️ Настройки</h3>
          <p>Настройте приложение под ваши потребности и предпочтения</p>
        </div>
        
      </main>
    </div>
  );
};

export default Dashboard;