from typing import List
from fastapi import APIRouter, Depends, status, Query

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List
from datetime import date

from api.dependencies import (
    get_product_service,
    get_product_image_service,
    get_current_authorised_user,
)
from database.models import UserModel
from schemas.product_schemas import (
    ProductCreateSchema,
    ProductReadSchema,
    ProductUpdateSchema,
)
from schemas.product_image_schemas import (
    ProductImageReadSchema,
    ProductImageUploadResponseSchema,
    ProductImageSummarySchema,
    ProductWithImagesSchema,
    ImageType,
)
from services.product_service import ProductService
from services.product_image_service import ProductImageService


from api.dependencies import get_current_authorised_user, get_product_service
from database.models import UserModel
from schemas.product_image_schemas import ProductImageUploadResponseSchema
from schemas.product_schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductReadSchema,
    ProductListSchema,
)
from services.product_service import ProductService

product_router = APIRouter(prefix="/products", tags=["Products"])


@product_router.post(
    "/",
    response_model=ProductReadSchema,
    status_code=status.HTTP_201_CREATED,
    response_description="Product created successfully",
)
async def create_product(
    product_data: ProductCreateSchema,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Создать новый продукт"""
    return await product_service.create_product(product_data, current_user.id)


@product_router.get(
    "/owner",
    response_model=List[ProductListSchema],
    response_description="User's products retrieved successfully",
)
async def get_my_products(
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить все продукты текущего пользователя"""
    return await product_service.get_user_products(current_user.id)


@product_router.get(
    "/{product_id}",
    response_model=ProductReadSchema,
    response_description="Product retrieved successfully",
)
async def get_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить продукт по ID (только свои продукты)"""
    return await product_service.get_product(product_id, current_user.id)


@product_router.get(
    "/",
    response_model=List[ProductListSchema],
    response_description="All products retrieved successfully",
)
async def get_all_products(
    product_service: ProductService = Depends(get_product_service),
):
    """Получить все продукты (для админов или всех, в зависимости от политики)"""
    return await product_service.get_all_products()


@product_router.put(
    "/{product_id}",
    response_model=ProductReadSchema,
    response_description="Product updated successfully",
)
async def update_product(
    product_id: int,
    update_data: ProductUpdateSchema,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Обновить продукт"""
    return await product_service.update_product(
        product_id, update_data, current_user.id
    )


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Product deleted successfully",
)
async def delete_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Удалить продукт"""
    await product_service.delete_product(product_id, current_user.id)
    return None


@product_router.get(
    "/search/",
    response_model=List[ProductListSchema],
    response_description="Products found successfully",
)
async def search_products(
    query: str = Query(..., min_length=1, description="Search query"),
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Поиск продуктов по названию (только свои)"""
    return await product_service.search_products(query, current_user.id)


@product_router.get(
    "/category/{category}",
    response_model=List[ProductListSchema],
    response_description="Products by category retrieved successfully",
)
async def get_products_by_category(
    category: str,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить продукты по категории (только свои)"""
    return await product_service.get_products_by_category(category, current_user.id)


@product_router.post(
    "/{product_id}/images/upload-url",
    response_model=ProductImageUploadResponseSchema,
    response_description="URL для загрузки изображения",
)
async def get_product_image_upload_url(
    product_id: int,
    filename: str = Form(...),
    image_type: ImageType = Form(ImageType.OTHER),
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Получить presigned URL для загрузки изображения продукта.

    - **filename**: имя файла
    - **image_type**: тип изображения (receipt, warranty, product, document, certificate, other)
    """
    return await image_service.get_upload_url(product_id, filename, image_type)


@product_router.post(
    "/{product_id}/images/upload",
    response_model=ProductImageReadSchema,
    response_description="Изображение загружено",
)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    image_type: ImageType = Form(ImageType.OTHER),
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Загрузить изображение продукта через сервер.
    Поддерживаются все типы изображений.
    """
    # Проверяем тип файла
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    return await image_service.upload_file_direct(product_id, file, image_type)


@product_router.get(
    "/{product_id}/images",
    response_model=List[ProductImageReadSchema],
    response_description="Список всех изображений продукта",
)
async def get_product_images(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """Получить все изображения продукта"""
    return await image_service.get_product_images(product_id)


@product_router.get(
    "/{product_id}/images/by-type/{image_type}",
    response_model=List[ProductImageReadSchema],
    response_description="Изображения продукта по типу",
)
async def get_product_images_by_type(
    product_id: int,
    image_type: ImageType,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Получить изображения продукта определенного типа:
    - **receipt** - чеки
    - **warranty** - гарантии
    - **product** - фото товара
    - **document** - документы
    - **certificate** - сертификаты
    - **other** - другое
    """
    return await image_service.get_product_images_by_type(product_id, image_type)


@product_router.get(
    "/{product_id}/images/summary",
    response_model=ProductImageSummarySchema,
    response_description="Сводка по изображениям продукта",
)
async def get_product_images_summary(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """Получить сводку по изображениям продукта"""
    return await image_service.get_image_summary(product_id)


@product_router.get(
    "/{product_id}/with-images",
    response_model=ProductWithImagesSchema,
    response_description="Продукт со всеми изображениями",
)
async def get_product_with_images(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """Получить продукт вместе со всеми его изображениями"""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    images = await image_service.get_product_images(product_id)
    summary = await image_service.get_image_summary(product_id)

    # Преобразуем product в словарь и добавляем изображения
    product_dict = product.model_dump()
    product_dict["images"] = images
    product_dict["images_summary"] = summary

    return ProductWithImagesSchema(**product_dict)


@product_router.delete("/images/{image_id}", response_description="Изображение удалено")
async def delete_product_image(
    image_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """Удалить изображение продукта"""
    success = await image_service.delete_image(image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}


@product_router.patch(
    "/{product_id}/images/{image_id}/set-main",
    response_model=ProductImageReadSchema,
    response_description="Главное изображение обновлено",
)
async def set_main_product_image(
    product_id: int,
    image_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
):
    """Установить изображение как главное для продукта"""
    return await image_service.set_main_image(product_id, image_id)


@product_router.post(
    "/{product_id}/images/upload",
    response_model=ProductImageReadSchema,
    response_description="Изображение продукта загружено",
)
async def upload_product_image_direct(
    product_id: int,
    file: UploadFile = File(...),
    image_type: ImageType = Form(ImageType.PRODUCT),
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Загрузить изображение продукта напрямую через сервер.

    - **file**: файл изображения (JPG, PNG, GIF)
    - **image_type**: тип изображения (product, receipt, warranty, document, certificate, other)
    """
    # Проверяем доступ к продукту
    product = await product_service.get_product(product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Проверяем тип файла
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Проверяем размер файла (например, максимум 10MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    return await image_service.upload_file_direct(product_id, file, image_type)


@product_router.get(
    "/{product_id}/images",
    response_model=List[ProductImageReadSchema],
    response_description="Список изображений продукта"
)
async def get_product_images(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    image_service: ProductImageService = Depends(get_product_image_service),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Получить все изображения продукта.
    
    Возвращает список изображений с presigned URLs для скачивания.
    """
    # Проверяем, что продукт принадлежит текущему пользователю
    product = await product_service.get_product(product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Получаем изображения
    images = await image_service.get_product_images(product_id)
    
    return images
