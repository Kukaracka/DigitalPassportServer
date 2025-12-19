import React, { useState, useEffect } from 'react';
import './ProductForm.css';

const ProductForm = ({ product, onSubmit, onCancel, isEditing = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    manufacturer: '',
    model: '',
    serial_number: '',
    price: '',
    purchase_date: '',
    warranty_until: '',
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
        serial_number: product.serial_number || '',
        price: product.price || '',
        purchase_date: product.purchase_date ? product.purchase_date.split('T')[0] : '',
        warranty_until: product.warranty_until ? product.warranty_until.split('T')[0] : '',
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
    
    if (!formData.manufacturer) {
      newErrors.manufacturer = 'Введите производителя';
    }
    
    if (!formData.model) {
      newErrors.model = 'Введите модель';
    }
    
    if (!formData.serial_number) {
      newErrors.serial_number = 'Введите серийный номер';
    }
    
    if (!formData.price || isNaN(Number(formData.price)) || Number(formData.price) <= 0) {
      newErrors.price = 'Введите корректную цену';
    }
    
    if (!formData.purchase_date) {
      newErrors.purchase_date = 'Введите дату покупки';
    } else if (new Date(formData.purchase_date) > new Date()) {
      newErrors.purchase_date = 'Дата покупки не может быть в будущем';
    }
    
    if (formData.warranty_until && formData.purchase_date && 
        new Date(formData.warranty_until) < new Date(formData.purchase_date)) {
      newErrors.warranty_until = 'Дата окончания гарантии не может быть раньше даты покупки';
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
        price: Number(formData.price),
        purchase_date: formData.purchase_date,
        warranty_until: formData.warranty_until || null,
        description: formData.description || null,
        notes: formData.notes || null
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
            <label htmlFor="manufacturer">Производитель *</label>
            <input
              type="text"
              id="manufacturer"
              name="manufacturer"
              value={formData.manufacturer}
              onChange={handleChange}
              placeholder="Например: Apple, Samsung"
              className={errors.manufacturer ? 'error' : ''}
            />
            {errors.manufacturer && <span className="error-message">{errors.manufacturer}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="model">Модель *</label>
            <input
              type="text"
              id="model"
              name="model"
              value={formData.model}
              onChange={handleChange}
              placeholder="Например: iPhone 14 Pro"
              className={errors.model ? 'error' : ''}
            />
            {errors.model && <span className="error-message">{errors.model}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="serial_number">Серийный номер *</label>
            <input
              type="text"
              id="serial_number"
              name="serial_number"
              value={formData.serial_number}
              onChange={handleChange}
              placeholder="SN123456789"
              className={errors.serial_number ? 'error' : ''}
            />
            {errors.serial_number && <span className="error-message">{errors.serial_number}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="price">Цена (₽) *</label>
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
            <label htmlFor="purchase_date">Дата покупки *</label>
            <input
              type="date"
              id="purchase_date"
              name="purchase_date"
              value={formData.purchase_date}
              onChange={handleChange}
              className={errors.purchase_date ? 'error' : ''}
            />
            {errors.purchase_date && <span className="error-message">{errors.purchase_date}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="warranty_until">Гарантия до</label>
            <input
              type="date"
              id="warranty_until"
              name="warranty_until"
              value={formData.warranty_until}
              onChange={handleChange}
              className={errors.warranty_until ? 'error' : ''}
            />
            {errors.warranty_until && <span className="error-message">{errors.warranty_until}</span>}
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