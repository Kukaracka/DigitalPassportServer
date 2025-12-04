import React, { useState } from 'react';
import ProductForm from './ProductForm';
import './ProductDetail.css';

const ProductDetail = ({ product, onEdit, onDelete, onClose }) => {
  const [isEditing, setIsEditing] = useState(false);

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusText = (status) => {
    const statuses = {
      'active': 'Активен',
      'inactive': 'Неактивен',
      'repair': 'В ремонте'
    };
    return statuses[status] || status;
  };

  const getStatusColor = (status) => {
    const colors = {
      'active': '#43e97b',
      'inactive': '#ff6b6b',
      'repair': '#ffa502',
      'default': '#718096'
    };
    return colors[status] || colors.default;
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

          <div 
            className="product-status-badge" 
            style={{ backgroundColor: getStatusColor(product.status) }}
          >
            {getStatusText(product.status)}
          </div>
        </div>

        <div className="product-detail-info">
          <div className="info-section">
            <h3>📋 Основная информация</h3>
            <div className="info-grid">
              {product.manufacturer && (
                <div className="info-item">
                  <span className="info-label">Производитель:</span>
                  <span className="info-value">{product.manufacturer}</span>
                </div>
              )}
              
              {product.model && (
                <div className="info-item">
                  <span className="info-label">Модель:</span>
                  <span className="info-value">{product.model}</span>
                </div>
              )}
              
              {product.serialNumber && (
                <div className="info-item">
                  <span className="info-label">Серийный номер:</span>
                  <span className="info-value">{product.serialNumber}</span>
                </div>
              )}
              
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
                <span className="info-value">{formatDate(product.purchaseDate)}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Гарантия до:</span>
                <span className="info-value">{formatDate(product.warrantyUntil)}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Добавлен:</span>
                <span className="info-value">{formatDate(product.createdAt)}</span>
              </div>
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