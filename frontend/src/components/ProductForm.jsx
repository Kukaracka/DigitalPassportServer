import React, { useState, useEffect } from 'react';
import './ProductForm.css';

const ProductForm = ({ product, onSubmit, onCancel, isEditing = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    manufacturer: '',
    model: '',
    serialNumber: '',
    price: '',
    purchaseDate: '',
    warrantyUntil: '',
    description: '',
    notes: ''
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        category: product.category || '',
        manufacturer: product.manufacturer || '',
        model: product.model || '',
        serialNumber: product.serialNumber || '',
        price: product.price || '',
        purchaseDate: product.purchaseDate ? product.purchaseDate.split('T')[0] : '',
        warrantyUntil: product.warrantyUntil ? product.warrantyUntil.split('T')[0] : '',
        description: product.description || '',
        notes: product.notes || ''
      });
    }
  }, [product]);

  const categories = [
    'Ноутбук', 'Смартфон', 'Планшет', 'Наушники',
    'Телевизор', 'Фотоаппарат', 'Игровая консоль',
    'Другое'
  ];

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Введите название продукта';
    }
    
    if (!formData.category) {
      newErrors.category = 'Выберите категорию';
    }
    
    if (formData.price && isNaN(Number(formData.price))) {
      newErrors.price = 'Введите корректную цену';
    }
    
    if (formData.purchaseDate && new Date(formData.purchaseDate) > new Date()) {
      newErrors.purchaseDate = 'Дата покупки не может быть в будущем';
    }
    
    if (formData.warrantyUntil && formData.purchaseDate && 
        new Date(formData.warrantyUntil) < new Date(formData.purchaseDate)) {
      newErrors.warrantyUntil = 'Дата окончания гарантии не может быть раньше даты покупки';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      const productData = {
        ...formData,
        price: formData.price ? Number(formData.price) : null,
        purchaseDate: formData.purchaseDate || null,
        warrantyUntil: formData.warrantyUntil || null
      };
      
      onSubmit(productData);
    }
  };

  return (
    <div className="product-form-container">
      <div className="product-form-header">
        <h1>{isEditing ? 'Редактирование продукта' : 'Добавление нового продукта'}</h1>
        <button className="cancel-btn" onClick={onCancel}>
          ✖
        </button>
      </div>

      <form onSubmit={handleSubmit} className="product-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="name">Название продукта *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Например: MacBook Pro 2023"
              className={errors.name ? 'error' : ''}
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="category">Категория *</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className={errors.category ? 'error' : ''}
            >
              <option value="">Выберите категорию</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            {errors.category && <span className="error-message">{errors.category}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="manufacturer">Производитель</label>
            <input
              type="text"
              id="manufacturer"
              name="manufacturer"
              value={formData.manufacturer}
              onChange={handleChange}
              placeholder="Например: Apple, Samsung"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="model">Модель</label>
            <input
              type="text"
              id="model"
              name="model"
              value={formData.model}
              onChange={handleChange}
              placeholder="Например: iPhone 14 Pro"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="serialNumber">Серийный номер</label>
            <input
              type="text"
              id="serialNumber"
              name="serialNumber"
              value={formData.serialNumber}
              onChange={handleChange}
              placeholder="SN123456789"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="price">Цена (₽)</label>
            <input
              type="number"
              id="price"
              name="price"
              value={formData.price}
              onChange={handleChange}
              placeholder="Например: 99999"
              min="0"
              step="1"
              className={errors.price ? 'error' : ''}
            />
            {errors.price && <span className="error-message">{errors.price}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="purchaseDate">Дата покупки</label>
            <input
              type="date"
              id="purchaseDate"
              name="purchaseDate"
              value={formData.purchaseDate}
              onChange={handleChange}
              className={errors.purchaseDate ? 'error' : ''}
            />
            {errors.purchaseDate && <span className="error-message">{errors.purchaseDate}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="warrantyUntil">Гарантия до</label>
            <input
              type="date"
              id="warrantyUntil"
              name="warrantyUntil"
              value={formData.warrantyUntil}
              onChange={handleChange}
              className={errors.warrantyUntil ? 'error' : ''}
            />
            {errors.warrantyUntil && <span className="error-message">{errors.warrantyUntil}</span>}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="description">Описание</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Дополнительная информация о продукте..."
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Заметки</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Любые заметки, сервисные истории и т.д."
            rows="3"
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="submit-btn">
            {isEditing ? 'Сохранить изменения' : 'Добавить продукт'}
          </button>
          <button type="button" className="cancel-form-btn" onClick={onCancel}>
            Отмена
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;