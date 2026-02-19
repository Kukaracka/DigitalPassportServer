import React, { useRef, useState } from 'react';
import './AvatarUploader.css';

const AvatarUploader = ({ onUpload, onDelete, hasAvatar, isUploading, error }) => {
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [validationError, setValidationError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file) => {
    // Проверка формата
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      return 'Допустимые форматы: JPEG, PNG, GIF, WEBP';
    }

    // Проверка размера (5 МБ)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return 'Размер файла не должен превышать 5 МБ';
    }

    return '';
  };

  const handleFile = (file) => {
    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      return;
    }

    setValidationError('');

    // Создаем превью
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);

    // Отправляем файл
    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleDelete = () => {
    setPreviewUrl(null);
    onDelete();
  };

  const handleRemovePreview = () => {
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const displayError = error || validationError;

  return (
    <div className="avatar-uploader">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        onChange={handleChange}
        className="avatar-input"
        disabled={isUploading}
      />

      {previewUrl ? (
        <div className="avatar-preview-container">
          <img src={previewUrl} alt="Предпросмотр" className="avatar-preview" />
          <button 
            className="avatar-remove-preview"
            onClick={handleRemovePreview}
            disabled={isUploading}
          >
            ✕
          </button>
        </div>
      ) : (
        <div
          className={`avatar-dropzone ${dragActive ? 'drag-active' : ''} ${isUploading ? 'uploading' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleButtonClick}
        >
          {isUploading ? (
            <div className="avatar-uploading">
              <div className="avatar-spinner"></div>
              <span>Загрузка...</span>
            </div>
          ) : (
            <>
              <div className="avatar-upload-icon">📷</div>
              <span>Нажмите или перетащите фото</span>
              <small>JPEG, PNG, GIF, WEBP до 5 МБ</small>
            </>
          )}
        </div>
      )}

      {displayError && (
        <div className="avatar-error">
          {displayError}
        </div>
      )}

      {hasAvatar && !previewUrl && (
        <button 
          className="avatar-delete-btn"
          onClick={handleDelete}
          disabled={isUploading}
        >
          🗑️ Удалить фото
        </button>
      )}
    </div>
  );
};

export default AvatarUploader;