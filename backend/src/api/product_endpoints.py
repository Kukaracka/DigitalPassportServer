from typing import List
from fastapi import APIRouter, Depends, status, Query

from api.dependencies import get_current_authorised_user, get_product_service
from database.models import UserModel
from schemas.product_schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductReadSchema,
    ProductListSchema
)
from services.product_service import ProductService

product_router = APIRouter(prefix="/products", tags=["Products"])


@product_router.post(
    "/",
    response_model=ProductReadSchema,
    status_code=status.HTTP_201_CREATED,
    response_description="Product created successfully"
)
async def create_product(
    product_data: ProductCreateSchema,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Создать новый продукт"""
    return await product_service.create_product(product_data, current_user.id)


@product_router.get(
    "/owner",
    response_model=List[ProductListSchema],
    response_description="User's products retrieved successfully"
)
async def get_my_products(
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Получить все продукты текущего пользователя"""
    return await product_service.get_user_products(current_user.id)


@product_router.get(
    "/{product_id}",
    response_model=ProductReadSchema,
    response_description="Product retrieved successfully"
)
async def get_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Получить продукт по ID (только свои продукты)"""
    return await product_service.get_product(product_id, current_user.id)


@product_router.get(
    "/",
    response_model=List[ProductListSchema],
    response_description="All products retrieved successfully"
)
async def get_all_products(
    product_service: ProductService = Depends(get_product_service)
):
    """Получить все продукты (для админов или всех, в зависимости от политики)"""
    return await product_service.get_all_products()


@product_router.put(
    "/{product_id}",
    response_model=ProductReadSchema,
    response_description="Product updated successfully"
)
async def update_product(
    product_id: int,
    update_data: ProductUpdateSchema,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Обновить продукт"""
    return await product_service.update_product(product_id, update_data, current_user.id)


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Product deleted successfully"
)
async def delete_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Удалить продукт"""
    await product_service.delete_product(product_id, current_user.id)
    return None


@product_router.get(
    "/search/",
    response_model=List[ProductListSchema],
    response_description="Products found successfully"
)
async def search_products(
    query: str = Query(..., min_length=1, description="Search query"),
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Поиск продуктов по названию (только свои)"""
    return await product_service.search_products(query, current_user.id)


@product_router.get(
    "/category/{category}",
    response_model=List[ProductListSchema],
    response_description="Products by category retrieved successfully"
)
async def get_products_by_category(
    category: str,
    current_user: UserModel = Depends(get_current_authorised_user),
    product_service: ProductService = Depends(get_product_service)
):
    """Получить продукты по категории (только свои)"""
    return await product_service.get_products_by_category(category, current_user.id)
