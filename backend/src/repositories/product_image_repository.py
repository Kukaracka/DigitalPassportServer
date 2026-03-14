# /home/kukaracka/Projects/DigitalPassport/backend/src/repositories/product_image_repository.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from database.models import ProductImageModel, ImageType, Session
from datetime import datetime
import pytz


class ProductImageRepository:
    def __init__(self):
        self.session = Session()

    def _get_naive_datetime(self) -> datetime:
        """Возвращает datetime без часового пояса"""
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        # Убираем часовой пояс
        return now.replace(tzinfo=None)

    async def create(
        self, 
        product_id: int, 
        file_name: str, 
        original_name: str,
        image_type: ImageType = ImageType.OTHER,
        file_size: int = None, 
        content_type: str = None
    ) -> ProductImageModel:
        """Создать запись об изображении"""
        # Проверяем, есть ли уже изображения у продукта
        existing_images = await self.get_by_product(product_id)
        
        # Если это первое изображение, делаем его главным
        is_main = len(existing_images) == 0
        
        # Получаем текущее время без часового пояса
        now = self._get_naive_datetime()
        
        image = ProductImageModel(
            product_id=product_id,
            file_name=file_name,
            original_name=original_name,
            image_type=image_type,
            file_size=file_size,
            content_type=content_type,
            is_main=is_main,
            sort_order=len(existing_images),
            created_at=now,  # Используем datetime без tzinfo
            updated_at=now   # Используем datetime без tzinfo
        )
        
        self.session.add(image)
        await self.session.flush()
        return image

    async def get_by_product(self, product_id: int) -> List[ProductImageModel]:
        """Получить все изображения продукта"""
        query = select(ProductImageModel).where(
            ProductImageModel.product_id == product_id
        ).order_by(ProductImageModel.sort_order)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())  # Преобразуем Sequence в List

    async def get_by_product_and_type(
        self, 
        product_id: int, 
        image_type: ImageType
    ) -> List[ProductImageModel]:
        """Получить изображения продукта по типу"""
        query = select(ProductImageModel).where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.image_type == image_type
            )
        ).order_by(ProductImageModel.sort_order)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())  # Преобразуем Sequence в List

    async def get_by_id(self, image_id: int) -> Optional[ProductImageModel]:
        """Получить изображение по ID"""
        return await self.session.get(ProductImageModel, image_id)

    async def get_main_image(self, product_id: int) -> Optional[ProductImageModel]:
        """Получить главное изображение продукта"""
        query = select(ProductImageModel).where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.is_main.is_(True)  # Исправляем сравнение с True
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, image_id: int) -> bool:
        """Удалить изображение"""
        image = await self.get_by_id(image_id)
        if image:
            await self.session.delete(image)
            await self.session.flush()
            return True
        return False

    async def delete_by_product(self, product_id: int) -> None:
        """Удалить все изображения продукта"""
        await self.session.execute(
            delete(ProductImageModel).where(
                ProductImageModel.product_id == product_id
            )
        )
        await self.session.flush()

    async def set_main_image(self, product_id: int, image_id: int) -> bool:
        """Установить изображение как главное"""
        # Сначала сбрасываем главное у всех изображений продукта
        stmt = ProductImageModel.__table__.update().where(
            ProductImageModel.product_id == product_id
        ).values(is_main=False)
        
        await self.session.execute(stmt)
        
        # Устанавливаем новое главное
        image = await self.get_by_id(image_id)
        if image and image.product_id == product_id:
            image.is_main = True
            image.updated_at = self._get_naive_datetime()  # Обновляем время
            await self.session.flush()
            return True
        return False

    async def reorder_images(self, product_id: int, image_ids: List[int]):
        """Изменить порядок изображений"""
        for idx, image_id in enumerate(image_ids):
            stmt = ProductImageModel.__table__.update().where(
                and_(
                    ProductImageModel.id == image_id,
                    ProductImageModel.product_id == product_id
                )
            ).values(sort_order=idx)
            
            await self.session.execute(stmt)
        await self.session.flush()

    async def count_by_product(self, product_id: int) -> int:
        """Посчитать количество изображений продукта"""
        query = select(ProductImageModel).where(
            ProductImageModel.product_id == product_id
        )
        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def get_image_summary(self, product_id: int) -> dict:
        """Получить сводку по изображениям продукта"""
        images = await self.get_by_product(product_id)
        
        summary = {
            "total": len(images),
            "by_type": {},
            "main_image_id": None
        }
        
        for image in images:
            img_type = image.image_type.value if hasattr(image.image_type, 'value') else str(image.image_type)
            if img_type not in summary["by_type"]:
                summary["by_type"][img_type] = 0
            summary["by_type"][img_type] += 1
            
            if image.is_main:
                summary["main_image_id"] = image.id
        
        return summary
