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
      const response = await api.get('/users/me');
      console.log('📥 User data from server:', response.data);
      return response.data; // Бэкенд уже возвращает avatar_url!
    } catch (error) {
      console.log('⚠️ /users/me failed, trying /users/');
      const response = await api.get('/users/');
      const users = response.data;
      
      if (users && users.length > 0) {
        return users[0];
      }
      throw new Error('No users found');
    }
  }

  async updateUser(userData) {
    try {
      const response = await api.put('/users/', {
        username: userData.username,
        email: userData.email,
        first_name: userData.firstName,
        last_name: userData.lastName,
        father_name: userData.fatherName || '',
        phone_number: userData.phoneNumber || ''
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Загрузка аватарки через API (новый эндпоинт)
  async uploadAvatar(file) {
    try {
      console.log('📤 Uploading avatar:', file.name);
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('✅ Upload response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Upload error:', error);
      throw this.handleError(error);
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
    if (error.response?.status === 400) {
      return new Error(error.response.data.detail || 'Ошибка загрузки файла');
    }
    if (error.response?.status === 413) {
      return new Error('Файл слишком большой (макс. 5MB)');
    }
    if (error.request) {
      return new Error('Нет подключения к серверу');
    }
    return new Error('Произошла ошибка');
  }
}

export default new AuthAPI();