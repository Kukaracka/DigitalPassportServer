import React, { useEffect } from 'react';
import ProductsList from './ProductsList';
import LoadingSpinner from './LoadingSpinner';
import { useProducts } from '../hooks/useProducts';
import './Products.css';

const Products = ({ user, onBack }) => {
  const { 
    products, 
    loading, 
    error, 
    loadProducts, 
    addProduct, 
    updateProduct, 
    deleteProduct,
    getCategories,
    getManufacturers,
    getPriceStats,
    getProductsByCategory,
    getProductsByPriceRange,
    getProductsByDateRange,
    getProductsByManufacturer,
    sortProducts
  } = useProducts();

  useEffect(() => {
    if (user) {
      loadProducts();
    }
  }, [user]);

  if (loading && products.length === 0) {
    return <LoadingSpinner message="Загрузка продуктов..." />;
  }

  return (
    <div className="products-container">
      <header className="products-page-header">
        <button onClick={onBack} className="back-button">
          ← Назад в Dashboard
        </button>
        <h1>Мои продукты</h1>
      </header>
      
      <main className="products-page-content">
        <ProductsList
          products={products}
          loading={loading}
          error={error}
          onAddProduct={addProduct}
          onEditProduct={updateProduct}
          onDeleteProduct={deleteProduct}
          getProductsByCategory={getProductsByCategory}
          getProductsByPriceRange={getProductsByPriceRange}
          getProductsByDateRange={getProductsByDateRange}
          getProductsByManufacturer={getProductsByManufacturer}
          sortProducts={sortProducts}
          getCategories={getCategories}
          getManufacturers={getManufacturers}
          getPriceStats={getPriceStats}
          onRefresh={loadProducts}
        />
      </main>
    </div>
  );
};

export default Products;