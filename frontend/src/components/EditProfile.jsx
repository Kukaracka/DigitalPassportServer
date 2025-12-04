import React, { useState, useEffect } from 'react';
import './Auth.css';

const EditProfile = ({ user, onUpdate, onCancel, error }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    fatherName: '',
    phoneNumber: ''
  });
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState('');

  // Заполняем форму данными пользователя при загрузке
  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        firstName: user.first_name || '',
        lastName: user.last_name || '',
        fatherName: user.father_name || '',
        phoneNumber: user.phone_number || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (validationError) setValidationError('');
  };

  const validateForm = () => {
    const requiredFields = ['username', 'email', 'firstName', 'lastName'];
    for (let field of requiredFields) {
      if (!formData[field].trim()) {
        return 'Заполните все обязательные поля';
      }
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Введите корректный email адрес';
    }

    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationResult = validateForm();
    if (validationResult) {
      setValidationError(validationResult);
      return;
    }

    setLoading(true);
    setValidationError('');
    
    try {
      await onUpdate(formData);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-content">
          <h2>Редактирование профиля</h2>
          
          {(error || validationError) && (
            <div className="form-error">
              {error || validationError}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">Имя *</label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  placeholder="Введите ваше имя"
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="lastName">Фамилия *</label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  placeholder="Введите вашу фамилию"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="fatherName">Отчество</label>
              <input
                type="text"
                id="fatherName"
                name="fatherName"
                value={formData.fatherName}
                onChange={handleChange}
                placeholder="Введите ваше отчество"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="username">Имя пользователя *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Введите имя пользователя"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Введите ваш email"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="phoneNumber">Телефон</label>
              <input
                type="tel"
                id="phoneNumber"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                placeholder="Введите ваш телефон"
                disabled={loading}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button 
                type="submit" 
                className="auth-button"
                disabled={loading}
                style={{ flex: 1 }}
              >
                {loading ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button 
                type="button" 
                className="auth-button"
                onClick={onCancel}
                disabled={loading}
                style={{ 
                  flex: 1, 
                  background: 'linear-gradient(135deg, #718096 0%, #4a5568 100%)' 
                }}
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditProfile;