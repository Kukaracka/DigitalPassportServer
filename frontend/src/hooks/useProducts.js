import { useState, useEffect } from 'react';

export const useProducts = (userId) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (userId) {
      loadProducts();
    }
  }, [userId]);

  const loadProducts = () => {
    setLoading(true);
    try {
      const savedProducts = localStorage.getItem(`products_${userId}`);
      if (savedProducts) {
        setProducts(JSON.parse(savedProducts));
      }
    } catch (error) {
      setError('Ошибка загрузки продуктов');
    } finally {
      setLoading(false);
    }
  };

  const addProduct = (productData) => {
    return new Promise((resolve) => {
      const newProduct = {
        id: Date.now(),
        createdAt: new Date().toISOString(),
        ...productData
      };
      
      const updatedProducts = [...products, newProduct];
      setProducts(updatedProducts);
      
      if (userId) {
        localStorage.setItem(`products_${userId}`, JSON.stringify(updatedProducts));
      }
      
      resolve(newProduct);
    });
  };

  const updateProduct = (productId, productData) => {
    return new Promise((resolve) => {
      const updatedProducts = products.map(product => 
        product.id === productId ? { ...product, ...productData } : product
      );
      
      setProducts(updatedProducts);
      
      if (userId) {
        localStorage.setItem(`products_${userId}`, JSON.stringify(updatedProducts));
      }
      
      resolve();
    });
  };

  const deleteProduct = (productId) => {
    return new Promise((resolve) => {
      const updatedProducts = products.filter(product => product.id !== productId);
      
      setProducts(updatedProducts);
      
      if (userId) {
        localStorage.setItem(`products_${userId}`, JSON.stringify(updatedProducts));
      }
      
      resolve();
    });
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
      if (!product.purchaseDate) return false;
      const purchaseDate = new Date(product.purchaseDate);
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
        case 'purchaseDate':
          aValue = a.purchaseDate ? new Date(a.purchaseDate).getTime() : 0;
          bValue = b.purchaseDate ? new Date(b.purchaseDate).getTime() : 0;
          break;
        case 'createdAt':
          aValue = new Date(a.createdAt).getTime();
          bValue = new Date(b.createdAt).getTime();
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