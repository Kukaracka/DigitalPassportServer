import React, { useState, useEffect } from 'react';
import Profile from './Profile';
import Products from './Products';
import './Dashboard.css';

const Dashboard = ({ user, onLogout, onUpdateUser, onAvatarUpload }) => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const currentUser = user;
  const avatarUrl = user?.avatar_url; // URL уже готов!

  const getDisplayName = () => {
    if (!currentUser?.first_name) return 'Пользователь';
    
    const name = currentUser.first_name;
    if (windowWidth <= 768 && name.length > 12) {
      return name.substring(0, 10) + '...';
    }
    return name;
  };

  if (currentView === 'profile') {
    return (
      <Profile 
        user={user} 
        onBack={() => setCurrentView('dashboard')}
        onUpdateUser={onUpdateUser}
        onAvatarUpload={onAvatarUpload}
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
          {avatarUrl ? (
            <img 
              src={avatarUrl} 
              alt="avatar" 
              className="header-avatar"
              onError={(e) => console.error('❌ Failed to load avatar in header:', avatarUrl)}
            />
          ) : (
            <div className="header-avatar-placeholder">
              {currentUser?.first_name?.[0]}{currentUser?.last_name?.[0]}
            </div>
          )}
          <span title={`Добро пожаловать, ${currentUser?.first_name || 'Пользователь'}!`}>
            Добро пожаловать, {getDisplayName()}!
          </span>
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