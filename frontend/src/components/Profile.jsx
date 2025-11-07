import React from 'react';
import './Profile.css';

const Profile = ({ user, onBack }) => {
  const userData = user || {};

  return (
    <div className="profile">
      <header className="profile-header">
        <button onClick={onBack} className="back-button">
          ← Назад
        </button>
        <h1>Профиль пользователя</h1>
      </header>
      
      <main className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            {userData.first_name?.[0]}{userData.last_name?.[0]}
          </div>
          
          <div className="profile-info">
            <h2>{userData.first_name} {userData.last_name}</h2>
            <p className="profile-username">@{userData.username}</p>
            
            <div className="profile-details">
              <div className="detail-item">
                <span className="detail-label">Email:</span>
                <span className="detail-value">{userData.email}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Имя пользователя:</span>
                <span className="detail-value">{userData.username}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Имя:</span>
                <span className="detail-value">{userData.first_name}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Фамилия:</span>
                <span className="detail-value">{userData.last_name}</span>
              </div>
              
              {userData.father_name && (
                <div className="detail-item">
                  <span className="detail-label">Отчество:</span>
                  <span className="detail-value">{userData.father_name}</span>
                </div>
              )}
              
              {userData.phone_number && (
                <div className="detail-item">
                  <span className="detail-label">Телефон:</span>
                  <span className="detail-value">{userData.phone_number}</span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="profile-actions">
          <button className="action-button edit-button">
            ✏️ Редактировать профиль
          </button>
        </div>
      </main>
    </div>
  );
};

export default Profile;