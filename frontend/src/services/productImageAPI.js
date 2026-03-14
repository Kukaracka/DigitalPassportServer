import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 10000,
});

class ProductImageAPI {
  // 1. Получить presigned URL для загрузки
  async getUploadUrl(productId, filename, imageType) {
    try {
      const formData = new FormData();
      formData.append('filename', filename);
      formData.append('image_type', imageType);

      const response = await api.post(
        `/products/${productId}/images/upload-url`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 2. Загрузить файл напрямую через сервер (ОСНОВНОЙ МЕТОД)
  async uploadImageDirect(productId, file, imageType) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('image_type', imageType);

      const response = await api.post(
        `/products/${productId}/images/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      // В ответе приходит ProductImageReadSchema с image_url
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 3. Получить все изображения продукта
  async getProductImages(productId) {
    try {
      const response = await api.get(`/products/${productId}/images`);
      return response.data; // Массив ProductImageReadSchema
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 4. Получить изображения по типу
  async getImagesByType(productId, imageType) {
    try {
      const response = await api.get(`/products/${productId}/images/by-type/${imageType}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 5. Получить сводку по изображениям
  async getImageSummary(productId) {
    try {
      const response = await api.get(`/products/${productId}/images/summary`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 6. Получить продукт со всеми изображениями (НОВЫЙ МЕТОД)
  async getProductWithImages(productId) {
    try {
      const response = await api.get(`/products/${productId}/with-images`);
      return response.data; // ProductWithImagesSchema
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 7. Удалить изображение
  async deleteImage(imageId) {
    try {
      await api.delete(`/products/images/${imageId}`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // 8. Установить главное изображение
  async setMainImage(productId, imageId) {
    try {
      const response = await api.patch(`/products/${productId}/images/${imageId}/set-main`);
      return response.data; // Обновленное ProductImageReadSchema
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
      return new Error('Изображение не найдено');
    }
    if (error.request) {
      return new Error('Нет подключения к серверу');
    }
    return new Error('Произошла ошибка при работе с изображениями');
  }
}

export default new ProductImageAPI();