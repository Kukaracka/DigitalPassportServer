import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 10000,
});

class ProductAPI {
  async createProduct(productData) {
    try {
      const response = await api.post('/products/', productData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getMyProducts() {
    try {
      const response = await api.get('/products/owner');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAllProducts() {
    try {
      const response = await api.get('/products/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getProduct(productId) {
    try {
      const response = await api.get(`/products/${productId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateProduct(productId, productData) {
    try {
      const response = await api.put(`/products/${productId}`, productData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteProduct(productId) {
    try {
      await api.delete(`/products/${productId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async searchProducts(query) {
    try {
      const response = await api.get(`/products/search/?query=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getProductsByCategory(category) {
    try {
      const response = await api.get(`/products/category/${encodeURIComponent(category)}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail);
    }
    if (error.response?.status === 401) {
      return new Error('Необходима авторизация');
    }
    if (error.response?.status === 403) {
      return new Error('Нет доступа к этому ресурсу');
    }
    if (error.response?.status === 404) {
      return new Error('Продукт не найден');
    }
    if (error.request) {
      return new Error('Нет подключения к серверу');
    }
    return new Error('Произошла ошибка при работе с продуктами');
  }
}

export default new ProductAPI();
