import React from 'react';
import './ProductCard.css';

const ProductCard = ({ product, onClick }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
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
    return icons[category] || icons.default;
  };

  return (
    <div className="product-card" onClick={() => onClick(product)}>
      <div className="product-card-header">
        <div className="product-icon">
          {getCategoryIcon(product.category)}
        </div>
      </div>
      
      <div className="product-card-body">
        <h3 className="product-title">{product.name}</h3>
        <p className="product-category">{product.category}</p>
        
        {product.manufacturer && (
          <div className="product-info">
            <span className="info-label">Производитель:</span>
            <span className="info-value">{product.manufacturer}</span>
          </div>
        )}
        
        {product.model && (
          <div className="product-info">
            <span className="info-label">Модель:</span>
            <span className="info-value">{product.model}</span>
          </div>
        )}
        
        {product.purchase_date && (
          <div className="product-info">
            <span className="info-label">Куплен:</span>
            <span className="info-value">{formatDate(product.purchase_date)}</span>
          </div>
        )}
      </div>
      
      <div className="product-card-footer">
        <div className="product-price">
          {product.price ? `${product.price.toLocaleString('ru-RU')} ₽` : 'Цена не указана'}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;