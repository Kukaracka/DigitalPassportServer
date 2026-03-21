import React, { useState, useEffect } from 'react';
import ProductForm from './ProductForm';
import ProductImageGallery from './ProductImageGallery';
import LoadingSpinner from './LoadingSpinner';
import { useProducts } from '../hooks/useProducts';
import './ProductDetail.css';

const ProductDetail = ({ product, onEdit, onDelete, onClose }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [productData, setProductData] = useState(product);
  const [productImages, setProductImages] = useState([]);
  const [loadingImages, setLoadingImages] = useState(false);
  
  const { 
    getProductWithImages, 
    uploadProductImage, 
    deleteProductImage, 
    setMainProductImage 
  } = useProducts();

  useEffect(() => {
    loadProductWithImages();
  }, [product.id]);

  const loadProductWithImages = async () => {
    setLoadingImages(true);
    try {
      const data = await getProductWithImages(product.id);
      if (data) {
        setProductData(data);
        setProductImages(data.images || []);
      }
    } catch (error) {
      console.error('Error loading product with images:', error);
      setProductData(product);
    } finally {
      setLoadingImages(false);
    }
  };

  const handleUploadImage = async (productId, file, imageType) => {
    try {
      await uploadProductImage(productId, file, imageType);
      await loadProductWithImages();
    } catch (error) {
      alert(error.message);
    }
  };

  const handleDeleteImage = async (imageId) => {
    try {
      await deleteProductImage(imageId);
      await loadProductWithImages();
    } catch (error) {
      alert(error.message);
    }
  };

  const handleSetMainImage = async (productId, imageId) => {
    try {
      await setMainProductImage(productId, imageId);
      await loadProductWithImages();
    } catch (error) {
      alert(error.message);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Ноутбук': '💻',
      'Смартфон': '📱',
      'Планшет': '📟',
      'Наушники': '🎧',
      'Телевизор': '📺',
      'Фотоаппарат': '📷',
      'Игровая консоль': '🎮',
      'Другое': '📦'
    };
    return icons[category] || '📦';
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = (updatedData) => {
    onEdit(product.id, updatedData);
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (window.confirm('Вы уверены, что хотите удалить этот продукт?')) {
      onDelete(product.id);
    }
  };

  if (isEditing) {
    return (
      <ProductForm
        product={productData}
        onSubmit={handleSave}
        onCancel={() => setIsEditing(false)}
        isEditing={true}
      />
    );
  }

  if (loadingImages && !productData) {
    return <LoadingSpinner message="Загрузка информации о продукте..." />;
  }

  return (
    <div className="product-detail">
      <div className="product-detail-header">
        <button className="back-btn" onClick={onClose}>
          ← Назад
        </button>
        <h1>Информация о продукте</h1>
      </div>

      <div className="product-detail-content">
        <div className="product-detail-main">
          <div className="product-title-section">
            <div className="product-icon-large">
              {getCategoryIcon(productData.category)}
            </div>
            <div>
              <h2>{productData.name}</h2>
              <p className="product-category-detail">{productData.category || 'Без категории'}</p>
            </div>
          </div>
        </div>

        <div className="product-detail-info">
          <div className="info-section">
            <h3>📋 Основная информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Производитель:</span>
                <span className="info-value">{productData.manufacturer || 'Не указан'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Модель:</span>
                <span className="info-value">{productData.model || 'Не указана'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Серийный номер:</span>
                <span className="info-value">{productData.serial_number || 'Не указан'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Цена:</span>
                <span className="info-value">
                  {productData.price ? `${productData.price.toLocaleString('ru-RU')} ₽` : 'Не указана'}
                </span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>📅 Даты</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Дата покупки:</span>
                <span className="info-value">{formatDate(productData.purchase_date)}</span>
              </div>
              
              {productData.warranty_until && (
                <div className="info-item">
                  <span className="info-label">Гарантия до:</span>
                  <span className="info-value">{formatDate(productData.warranty_until)}</span>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Добавлен:</span>
                <span className="info-value">{formatDateTime(productData.created_at)}</span>
              </div>
              
              {productData.updated_at && (
                <div className="info-item">
                  <span className="info-label">Обновлен:</span>
                  <span className="info-value">{formatDateTime(productData.updated_at)}</span>
                </div>
              )}
            </div>
          </div>

          {productData.description && (
            <div className="info-section">
              <h3>📝 Описание</h3>
              <p className="product-description">{productData.description}</p>
            </div>
          )}

          {productData.notes && (
            <div className="info-section">
              <h3>🗒️ Заметки</h3>
              <p className="product-notes">{productData.notes}</p>
            </div>
          )}
        </div>

        <div className="product-action-buttons">
          <button className="edit-btn-large" onClick={handleEdit}>
            ✏️ Редактировать
          </button>
          <button className="delete-btn-large" onClick={handleDelete}>
            🗑️ Удалить
          </button>
        </div>

        <ProductImageGallery
          productId={productData.id}
          images={productImages}
          onUpload={handleUploadImage}
          onDelete={handleDeleteImage}
          onSetMain={handleSetMainImage}
          loading={loadingImages}
        />
      </div>
    </div>
  );
};

export default ProductDetail;