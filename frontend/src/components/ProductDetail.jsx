import React, { useState } from 'react';
import ProductForm from './ProductForm';
import './ProductDetail.css';

const ProductDetail = ({ product, onEdit, onDelete, onClose }) => {
  const [isEditing, setIsEditing] = useState(false);

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
        product={product}
        onSubmit={handleSave}
        onCancel={() => setIsEditing(false)}
        isEditing={true}
      />
    );
  }

  return (
    <div className="product-detail">
      <div className="product-detail-header">
        <button className="back-btn" onClick={onClose}>
          ← Назад к списку
        </button>
        <h1>Информация о продукте</h1>
        <div className="product-actions">
          <button className="edit-btn" onClick={handleEdit}>
            ✏️ Редактировать
          </button>
          <button className="delete-btn" onClick={handleDelete}>
            🗑️ Удалить
          </button>
        </div>
      </div>

      <div className="product-detail-content">
        <div className="product-detail-main">
          <div className="product-title-section">
            <div className="product-icon-large">
              {getCategoryIcon(product.category)}
            </div>
            <div>
              <h2>{product.name}</h2>
              <p className="product-category-detail">{product.category || 'Без категории'}</p>
            </div>
          </div>
        </div>

        <div className="product-detail-info">
          <div className="info-section">
            <h3>📋 Основная информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Производитель:</span>
                <span className="info-value">{product.manufacturer || 'Не указан'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Модель:</span>
                <span className="info-value">{product.model || 'Не указана'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Серийный номер:</span>
                <span className="info-value">{product.serial_number || 'Не указан'}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Цена:</span>
                <span className="info-value">
                  {product.price ? `${product.price.toLocaleString('ru-RU')} ₽` : 'Не указана'}
                </span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>📅 Даты</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Дата покупки:</span>
                <span className="info-value">{formatDate(product.purchase_date)}</span>
              </div>
              
              {product.warranty_until && (
                <div className="info-item">
                  <span className="info-label">Гарантия до:</span>
                  <span className="info-value">{formatDate(product.warranty_until)}</span>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Добавлен:</span>
                <span className="info-value">{formatDateTime(product.created_at)}</span>
              </div>
              
              {product.updated_at && (
                <div className="info-item">
                  <span className="info-label">Обновлен:</span>
                  <span className="info-value">{formatDateTime(product.updated_at)}</span>
                </div>
              )}
            </div>
          </div>

          {product.description && (
            <div className="info-section">
              <h3>📝 Описание</h3>
              <p className="product-description">{product.description}</p>
            </div>
          )}

          {product.notes && (
            <div className="info-section">
              <h3>🗒️ Заметки</h3>
              <p className="product-notes">{product.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;