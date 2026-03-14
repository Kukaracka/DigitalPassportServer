export const ImageType = {
  RECEIPT: 'receipt',        // Чек
  WARRANTY: 'warranty',       // Гарантия
  PRODUCT: 'product',         // Фото товара
  DOCUMENT: 'document',       // Документ
  CERTIFICATE: 'certificate', // Сертификат
  OTHER: 'other'              // Другое
};

// Русские названия для отображения
export const ImageTypeLabels = {
  [ImageType.RECEIPT]: 'Чек',
  [ImageType.WARRANTY]: 'Гарантия',
  [ImageType.PRODUCT]: 'Фото товара',
  [ImageType.DOCUMENT]: 'Документ',
  [ImageType.CERTIFICATE]: 'Сертификат',
  [ImageType.OTHER]: 'Другое'
};

// Цвета для типов изображений
export const ImageTypeColors = {
  [ImageType.RECEIPT]: '#4CAF50',
  [ImageType.WARRANTY]: '#FF9800',
  [ImageType.PRODUCT]: '#2196F3',
  [ImageType.DOCUMENT]: '#9C27B0',
  [ImageType.CERTIFICATE]: '#FF5722',
  [ImageType.OTHER]: '#607D8B'
};