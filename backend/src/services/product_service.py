from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

from repositories.product_repository import ProductRepository
from schemas.product_schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductReadSchema,
    ProductListSchema,
)
from database.models import ProductModel


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo: ProductRepository = product_repo

    async def create_product(
        self, product_data: ProductCreateSchema, owner_id: int
    ) -> ProductReadSchema:
        """Создать новый продукт"""
        # Проверка уникальности серийного номера
        existing_product = await self.product_repo.get_by_serial_number(
            product_data.serial_number
        )
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this serial number already exists",
            )

        product_dict = product_data.model_dump()
        product_dict["owner_id"] = owner_id
        
        # Убираем часовой пояс из datetime объектов
        now = datetime.now()
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        
        product_dict["created_at"] = now
        product_dict["updated_at"] = now

        product_id = await self.product_repo.create_one(product_dict)

        created_product = await self.product_repo.read_one(product_id)
        return ProductReadSchema.model_validate(created_product)

    async def get_product(
        self, product_id: int, owner_id: Optional[int] = None
    ) -> ProductReadSchema:
        """Получить продукт по ID"""
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if owner_id and product.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this product",
            )

        return ProductReadSchema.model_validate(product)

    async def get_user_products(self, owner_id: int) -> List[ProductListSchema]:
        """Получить все продукты пользователя"""
        products = await self.product_repo.get_by_owner(owner_id)
        return [ProductListSchema.model_validate(product) for product in products]

    async def get_all_products(self) -> List[ProductListSchema]:
        """Получить все продукты (для админов)"""
        products = await self.product_repo.read_all()
        return [ProductListSchema.model_validate(product) for product in products]

    async def update_product(
        self, product_id: int, update_data: ProductUpdateSchema, owner_id: int
    ) -> ProductReadSchema:
        """Обновить продукт"""
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if product.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this product",
            )

        if (
            update_data.serial_number
            and update_data.serial_number != product.serial_number
        ):
            existing = await self.product_repo.get_by_serial_number(
                update_data.serial_number
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this serial number already exists",
                )

        update_dict = update_data.model_dump(exclude_unset=True)
        await self.product_repo.update_one(product_id, update_dict)

        updated_product = await self.product_repo.read_one(product_id)
        return ProductReadSchema.model_validate(updated_product)

    async def delete_product(self, product_id: int, owner_id: int) -> bool:
        """Удалить продукт"""
        product = await self.product_repo.read_one(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if product.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this product",
            )

        await self.product_repo.delete_one(product_id)
        return True

    async def search_products(
        self, query: str, owner_id: Optional[int] = None
    ) -> List[ProductListSchema]:
        """Поиск продуктов по названию"""
        products = await self.product_repo.search_by_name(query)

        if owner_id:
            products = [p for p in products if p.owner_id == owner_id]

        return [ProductListSchema.model_validate(product) for product in products]

    async def get_products_by_category(
        self, category: str, owner_id: Optional[int] = None
    ) -> List[ProductListSchema]:
        """Получить продукты по категории"""
        products = await self.product_repo.get_by_category(category)

        if owner_id:
            products = [p for p in products if p.owner_id == owner_id]

        return [ProductListSchema.model_validate(product) for product in products]
