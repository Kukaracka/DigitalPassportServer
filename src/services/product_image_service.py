import logging
import uuid
from typing import List
import asyncio

from fastapi import HTTPException, UploadFile
from database.models import ImageType as ImageTypeModel
from repositories.product_image_repository import ProductImageRepository
from repositories.product_repository import ProductRepository
from schemas.product_image_schemas import (
    ImageType,
    ProductImageReadSchema,
    ProductImageSummarySchema,
    ProductImageUploadResponseSchema,
)
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ProductImageService:
    def __init__(
        self,
        image_repo: ProductImageRepository,
        product_repo: ProductRepository,
        storage_service: StorageService,
    ):
        self.image_repo = image_repo
        self.product_repo = product_repo
        self.storage = storage_service

    async def get_upload_url(
        self, product_id: int, filename: str, image_type: ImageType = ImageType.OTHER
    ) -> ProductImageUploadResponseSchema:
        """Получить URL для загрузки изображения"""
        # Проверяем, существует ли продукт
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Генерируем уникальное имя файла
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        file_name = f"products/{product_id}/{image_type.value}/{uuid.uuid4()}.{ext}"

        # ИСПРАВЛЕНИЕ: используем get_upload_url (есть в StorageService)
        upload_url = self.storage.get_upload_url(file_name=file_name, expires=3600)

        if not upload_url:
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")

        # Создаем запись в БД
        image = await self.image_repo.create(
            product_id=product_id,
            file_name=file_name,
            original_name=filename,
            image_type=ImageTypeModel(image_type),
            content_type=f"image/{ext}",
        )

        # Получаем URL для просмотра (используем get_download_url)
        image_url = self.storage.get_download_url(file_name=file_name, expires=3600)

        return ProductImageUploadResponseSchema(
            id=image.id,
            file_name=file_name,
            original_name=filename,
            image_type=image_type,
            upload_url=upload_url,
            image_url=image_url,
        )

    async def _check_product_access(
        self,
        product_id: int,
        owner_id: int | None = None,
    ):
        product = await self.product_repo.read_one(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if owner_id is not None and product.owner_id != owner_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return product

    async def get_product_images(self, product_id: int) -> List[ProductImageReadSchema]:
        """Получить все изображения продукта с presigned URLs"""
        # Проверяем, существует ли продукт (опционально)
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Получаем изображения из БД
        images = await self.image_repo.get_by_product(product_id)

        logger.info(f"Found {len(images)} images for product {product_id}")

        # Преобразуем каждое изображение в схему с URL
        result = []
        for image in images:
            # Валидируем модель БД в Pydantic схему
            image_schema = ProductImageReadSchema.model_validate(image)

            # Добавляем presigned URL для скачивания
            # Используем get_download_url из storage_service
            download_url = self.storage.get_download_url(
                file_name=image.file_name,
                expires=3600,  # ссылка действительна 1 час
            )

            if download_url:
                image_schema.image_url = download_url

            result.append(image_schema)

        return result

    async def get_product_images_by_type(
        self, product_id: int, image_type: ImageType
    ) -> List[ProductImageReadSchema]:
        """Получить изображения продукта по типу"""
        # Проверяем продукт
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        images = await self.image_repo.get_by_product_and_type(
            product_id, ImageTypeModel(image_type)
        )

        # Добавляем URL к каждому изображению
        result = []
        for image in images:
            image_schema = ProductImageReadSchema.model_validate(image)
            download_url = self.storage.get_download_url(
                file_name=image.file_name, expires=3600
            )
            if download_url:
                image_schema.image_url = download_url
            result.append(image_schema)

        return result

    async def get_image_summary(self, product_id: int) -> ProductImageSummarySchema:
        """Получить сводку по изображениям продукта"""
        summary = await self.image_repo.get_image_summary(product_id)

        # Добавляем URL главного изображения
        main_image_url = None
        if summary["main_image_id"]:
            main_image = await self.image_repo.get_by_id(summary["main_image_id"])
            if main_image:
                main_image_url = self.storage.get_download_url(
                    file_name=main_image.file_name, expires=3600
                )

        return ProductImageSummarySchema(
            total=summary["total"],
            by_type=summary["by_type"],
            main_image_id=summary["main_image_id"],
            main_image_url=main_image_url,
        )

    async def delete_image(self, image_id: int) -> bool:
        """Удалить изображение"""
        # Получаем изображение из БД
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            return False

        # Удаляем файл из MinIO
        try:
            self.storage.client.remove_object(self.storage.bucket, image.file_name)
        except Exception as e:
            logger.error(f"Failed to delete file from MinIO: {e}")

        # Удаляем запись из БД
        return await self.image_repo.delete(image_id)

    async def set_main_image(
        self, product_id: int, image_id: int
    ) -> ProductImageReadSchema:
        """Установить изображение как главное"""
        success = await self.image_repo.set_main_image(product_id, image_id)
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")

        # Получаем обновленное изображение
        image = await self.image_repo.get_by_id(image_id)
        image_schema = ProductImageReadSchema.model_validate(image)
        download_url = self.storage.get_download_url(
            file_name=image.file_name, expires=3600
        )
        if download_url:
            image_schema.image_url = download_url

        return image_schema

    async def upload_file_direct(
        self,
        product_id: int,
        file: UploadFile,
        image_type: ImageType = ImageType.PRODUCT,
    ) -> ProductImageReadSchema:
        """Прямая загрузка файла через сервер"""
        # Проверяем продукт
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Читаем файл
        file_data = await file.read()  # Читаем байты

        # Проверяем filename на None
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Генерируем имя
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_name = f"products/{product_id}/{image_type.value}/{uuid.uuid4()}.{ext}"

        # ИСПРАВЛЕНИЕ: используем правильное имя параметра file_data
        success = await asyncio.to_thread(
            self.storage.upload_file,
            file_data,
            file_name,
            file.content_type or f"image/{ext}"
        )

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to upload file to storage"
            )

        # Создаем запись в БД
        original_name = file.filename if file.filename is not None else "unknown.jpg"

        image = await self.image_repo.create(
            product_id=product_id,
            file_name=file_name,
            original_name=original_name,
            image_type=ImageTypeModel(image_type),
            file_size=len(file_data),
            content_type=file.content_type or f"image/{ext}",
        )

        # Преобразуем в схему с URL
        image_schema = ProductImageReadSchema.model_validate(image)
        image_schema.image_url = self.storage.get_download_url(
            file_name=file_name, expires=3600
        )

        return image_schema
