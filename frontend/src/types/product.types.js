export const ImageType = {
  RECEIPT: 'RECEIPT',        // Чек
  WARRANTY: 'WARRANTY',       // Гарантия
  PRODUCT: 'PRODUCT',         // Фото товара
  DOCUMENT: 'DOCUMENT',       // Документ
  CERTIFICATE: 'CERTIFICATE', // Сертификат
  OTHER: 'OTHER'              // Другое
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
