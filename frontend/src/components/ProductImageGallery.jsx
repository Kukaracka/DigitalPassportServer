import React, { useState, useEffect } from 'react';
import { ImageType, ImageTypeLabels, ImageTypeColors } from '../types/product.types';
import './ProductImageGallery.css';

const ProductImageGallery = ({ 
  productId, 
  images = [], 
  onUpload, 
  onDelete, 
  onSetMain,
  loading 
}) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadType, setUploadType] = useState(ImageType.PRODUCT);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileUpload = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }
    onUpload(productId, file, uploadType);
    setShowUploadModal(false);
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  // Группируем изображения по типам
  const imagesByType = images.reduce((acc, img) => {
    if (!acc[img.image_type]) {
      acc[img.image_type] = [];
    }
    acc[img.image_type].push(img);
    return acc;
  }, {});

  return (
    <div className="product-image-gallery">
      {/* Шапка с кнопкой добавления */}
      <div className="gallery-header">
        <h3>📸 Фотографии и документы</h3>
        <button 
          className="add-image-btn"
          onClick={() => setShowUploadModal(true)}
        >
          + Добавить фото
        </button>
      </div>

      {/* Модалка выбора типа изображения */}
      {showUploadModal && (
        <div className="upload-modal">
          <div className="upload-modal-content">
            <h4>Выберите тип изображения</h4>
            <div className="image-type-selector">
              {Object.values(ImageType).map(type => (
                <button
                  key={type}
                  className={`type-btn ${uploadType === type ? 'active' : ''}`}
                  style={{ backgroundColor: uploadType === type ? ImageTypeColors[type] : '#f0f0f0' }}
                  onClick={() => setUploadType(type)}
                >
                  {ImageTypeLabels[type]}
                </button>
              ))}
            </div>

            {/* Drag & drop зона */}
            <div
              className={`upload-area ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="image-upload-input"
              />
              <label htmlFor="image-upload-input" className="upload-label">
                <div className="upload-icon">📷</div>
                <div>Нажмите или перетащите файл</div>
                <small>Поддерживаются все форматы изображений</small>
              </label>
            </div>

            <button 
              className="close-modal-btn"
              onClick={() => setShowUploadModal(false)}
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {/* Сетка изображений по типам */}
      {Object.entries(imagesByType).map(([type, typeImages]) => (
        <div key={type} className="image-type-section">
          <h4 style={{ color: ImageTypeColors[type] }}>
            {ImageTypeLabels[type]} ({typeImages.length})
          </h4>
          <div className="image-grid">
            {typeImages.map(image => (
              <div 
                key={image.id} 
                className={`image-card ${image.is_main ? 'main-image' : ''}`}
                onClick={() => setSelectedImage(image)}
              >
                <img src={image.image_url} alt={image.original_name} />
                
                {/* Бейдж "Главное" */}
                {image.is_main && (
                  <div className="main-badge">⭐ Главное</div>
                )}

                {/* Оверлей с кнопками при наведении */}
                <div className="image-overlay">
                  {!image.is_main && (
                    <button
                      className="overlay-btn set-main-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSetMain(productId, image.id);
                      }}
                      title="Сделать главным"
                    >
                      ⭐
                    </button>
                  )}
                  <button
                    className="overlay-btn delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Удалить изображение?')) {
                        onDelete(image.id);
                      }
                    }}
                    title="Удалить"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Если изображений нет */}
      {images.length === 0 && (
        <div className="no-images">
          <p>Нет загруженных изображений</p>
          <button onClick={() => setShowUploadModal(true)}>
            Загрузить первое фото
          </button>
        </div>
      )}

      {/* Модалка просмотра изображения */}
      {selectedImage && (
        <div className="image-viewer-modal" onClick={() => setSelectedImage(null)}>
          <div className="image-viewer-content" onClick={e => e.stopPropagation()}>
            <img src={selectedImage.image_url} alt={selectedImage.original_name} />
            <div className="image-info">
              <p><strong>Тип:</strong> {ImageTypeLabels[selectedImage.image_type]}</p>
              <p><strong>Имя файла:</strong> {selectedImage.original_name}</p>
              {selectedImage.file_size && (
                <p><strong>Размер:</strong> {(selectedImage.file_size / 1024).toFixed(2)} KB</p>
              )}
            </div>
            <button className="close-viewer" onClick={() => setSelectedImage(null)}>✕</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductImageGallery;