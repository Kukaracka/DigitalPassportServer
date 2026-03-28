from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ImageType(str, Enum):
    RECEIPT = "RECEIPT"        # Чек
    WARRANTY = "WARRANTY"       # Гарантия
    PRODUCT = "PRODUCT"         # Фото товара
    DOCUMENT = "DOCUMENT"       # Документ
    CERTIFICATE = "CERTIFICATE" # Сертификат
    OTHER = "OTHER"             # Другое


class ProductImageBaseSchema(BaseModel):
    file_name: str
    original_name: str
    image_type: ImageType
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    is_main: bool = False
    sort_order: int = 0


class ProductImageCreateSchema(BaseModel):
    original_name: str
    image_type: ImageType = ImageType.OTHER
    file_size: Optional[int] = None
    content_type: Optional[str] = None


class ProductImageUpdateSchema(BaseModel):
    is_main: Optional[bool] = None
    sort_order: Optional[int] = None
    image_type: Optional[ImageType] = None


class ProductImageReadSchema(ProductImageBaseSchema):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    # URL для доступа к изображению
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductImageUploadResponseSchema(BaseModel):
    """Ответ после получения URL для загрузки"""
    id: int
    file_name: str
    original_name: str
    image_type: ImageType
    upload_url: str  # URL для загрузки файла
    image_url: Optional[str] = None  # URL для просмотра после загрузки
    
    model_config = ConfigDict(from_attributes=True)


class ProductImageSummarySchema(BaseModel):
    """Сводка по изображениям продукта"""
    total: int
    by_type: dict[str, int]
    main_image_id: Optional[int] = None
    main_image_url: Optional[str] = None


class ProductWithImagesSchema(BaseModel):
    """Продукт с изображениями"""
    id: int
    name: str
    manufacturer: str
    category: str
    model: str
    serial_number: str
    price: float
    purchase_date: date
    warranty_until: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    
    images: List[ProductImageReadSchema] = []
    images_summary: Optional[ProductImageSummarySchema] = None
    
    model_config = ConfigDict(from_attributes=True)
