import React, { useState } from 'react';
import './Auth.css';

const Register = ({ onSwitchToLogin, onRegister, error }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    firstName: '',
    lastName: '',
    fatherName: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (validationError) setValidationError('');
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Пароль должен содержать минимум 8 символов';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Пароль должен содержать хотя бы одну заглавную букву';
    }
    if (!/\d/.test(password)) {
      return 'Пароль должен содержать хотя бы одну цифру';
    }
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      setValidationError(passwordError);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    
    try {
      await onRegister(formData);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const EyeIcon = ({ isVisible }) => (
    <svg 
      className="eye-icon" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2"
    >
      {isVisible ? (
        <>
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </>
      ) : (
        <>
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </>
      )}
    </svg>
  );

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-content">
          <h2>Регистрация в DigitalPassport</h2>
          
          {(error || validationError) && (
            <div className="form-error">
              {error || validationError}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">Имя</label>
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
                <label htmlFor="lastName">Фамилия</label>
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
                placeholder="Введите ваше отчество (необязательно)"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="username">Имя пользователя</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Придумайте имя пользователя"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
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
            
            <div className="form-group password-group">
              <label htmlFor="password">Пароль</label>
              <div className="password-input-container">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="Создайте пароль"
                  disabled={loading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={togglePasswordVisibility}
                  disabled={loading}
                >
                  <EyeIcon isVisible={showPassword} />
                </button>
              </div>
              <div className="password-hint">
                Минимум 8 символов, заглавная буква и цифра
              </div>
            </div>

            <div className="form-group password-group">
              <label htmlFor="confirmPassword">Подтвердите пароль</label>
              <div className="password-input-container">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  placeholder="Повторите пароль"
                  disabled={loading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={toggleConfirmPasswordVisibility}
                  disabled={loading}
                >
                  <EyeIcon isVisible={showConfirmPassword} />
                </button>
              </div>
            </div>

            <button 
              type="submit" 
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          <div className="auth-switch">
            <p>Уже есть аккаунт? 
              <span className="switch-link" onClick={onSwitchToLogin}>
                Войти
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;