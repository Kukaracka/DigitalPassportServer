import { useState, useEffect } from 'react';
import ProductAPI from '../services/productAPI';

export const useProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const userProducts = await ProductAPI.getMyProducts();
      setProducts(userProducts);
      setError(null);
    } catch (error) {
      console.error('Error loading products:', error);
      setError(error.message || 'Ошибка загрузки продуктов');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const addProduct = async (productData) => {
    setLoading(true);
    try {
      const newProduct = await ProductAPI.createProduct(productData);
      setProducts(prev => [newProduct, ...prev]);
      return newProduct;
    } catch (error) {
      console.error('Error adding product:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateProduct = async (productId, productData) => {
    setLoading(true);
    try {
      const updatedProduct = await ProductAPI.updateProduct(productId, productData);
      setProducts(prev => 
        prev.map(product => product.id === productId ? updatedProduct : product)
      );
      return updatedProduct;
    } catch (error) {
      console.error('Error updating product:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (productId) => {
    setLoading(true);
    try {
      await ProductAPI.deleteProduct(productId);
      setProducts(prev => prev.filter(product => product.id !== productId));
    } catch (error) {
      console.error('Error deleting product:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getProductById = (productId) => {
    return products.find(product => product.id === productId);
  };

  const getProductsByCategory = (category) => {
    if (!category || category === 'all') return products;
    return products.filter(product => product.category === category);
  };

  const getProductsByPriceRange = (minPrice, maxPrice) => {
    return products.filter(product => {
      const price = product.price || 0;
      return price >= minPrice && (maxPrice === null || price <= maxPrice);
    });
  };

  const getProductsByDateRange = (startDate, endDate) => {
    return products.filter(product => {
      if (!product.purchase_date) return false;
      const purchaseDate = new Date(product.purchase_date);
      return purchaseDate >= startDate && purchaseDate <= endDate;
    });
  };

  const getProductsByManufacturer = (manufacturer) => {
    if (!manufacturer) return products;
    return products.filter(product => 
      product.manufacturer?.toLowerCase().includes(manufacturer.toLowerCase())
    );
  };

  const sortProducts = (productsList, sortBy, sortOrder = 'asc') => {
    const sorted = [...productsList];
    
    sorted.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'price':
          aValue = a.price || 0;
          bValue = b.price || 0;
          break;
        case 'name':
          aValue = a.name?.toLowerCase() || '';
          bValue = b.name?.toLowerCase() || '';
          break;
        case 'purchase_date':
          aValue = a.purchase_date ? new Date(a.purchase_date).getTime() : 0;
          bValue = b.purchase_date ? new Date(b.purchase_date).getTime() : 0;
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return sorted;
  };

  const getCategories = () => {
    const categories = products.map(p => p.category);
    return [...new Set(categories)].filter(Boolean);
  };

  const getManufacturers = () => {
    const manufacturers = products.map(p => p.manufacturer);
    return [...new Set(manufacturers)].filter(Boolean);
  };

  const getPriceStats = () => {
    const prices = products.map(p => p.price || 0).filter(price => price > 0);
    if (prices.length === 0) return { min: 0, max: 0, avg: 0 };
    
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
      avg: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length)
    };
  };

  return {
    products,
    loading,
    error,
    loadProducts,
    addProduct,
    updateProduct,
    deleteProduct,
    getProductById,
    getProductsByCategory,
    getProductsByPriceRange,
    getProductsByDateRange,
    getProductsByManufacturer,
    sortProducts,
    getCategories,
    getManufacturers,
    getPriceStats
  };
};