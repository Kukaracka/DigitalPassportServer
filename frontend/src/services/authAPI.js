import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 10000,
});

class AuthAPI {
  async login(credentials) {
    try {
      const response = await api.post('/login', {
        username: credentials.username,
        password: credentials.password
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async register(userData) {
    try {
      const response = await api.post('/register', {
        username: userData.username,
        password: userData.password,
        email: userData.email,
        first_name: userData.firstName,
        last_name: userData.lastName,
        father_name: userData.fatherName || ''
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async checkAuth() {
    try {
      const response = await api.get('/login_check');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCurrentUser() {
    try {
      // Пробуем новый эндпоинт /users/me
      const response = await api.get('/users/me');
      return response.data;
    } catch (error) {
      // Если новый эндпоинт не работает, пробуем старый
      console.log('⚠️ /users/me failed, trying /users/');
      const response = await api.get('/users/');
      const users = response.data;
      
      // Берем первого пользователя как fallback
      if (users && users.length > 0) {
        return users[0];
      }
      throw new Error('No users found');
    }
  }

  handleError(error) {
    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail);
    }
    if (error.response?.status === 401) {
      return new Error('Неверные учетные данные');
    }
    if (error.response?.status === 409) {
      return new Error('Пользователь уже существует');
    }
    if (error.request) {
      return new Error('Нет подключения к серверу');
    }
    return new Error('Произошла ошибка');
  }
}

export default new AuthAPI();