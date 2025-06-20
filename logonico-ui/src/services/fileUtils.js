// services/fileUtils.js
/**
 * File utility functions for download, size calculation, and file operations
 */

export const downloadImage = async (imageUrl, filename) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Download failed:', error);
      return false;
    }
  };
  
  export const downloadMultipleImages = async (images, onProgress) => {
    const results = [];
    
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      const success = await downloadImage(image.url, image.filename);
      results.push({ image, success });
      
      if (onProgress) {
        onProgress({
          current: i + 1,
          total: images.length,
          percentage: ((i + 1) / images.length) * 100
        });
      }
      
      // Small delay to prevent overwhelming the browser
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return results;
  };
  
  export const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };
  
  export const getFileSizeFromUrl = async (url) => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const contentLength = response.headers.get('content-length');
      return contentLength ? parseInt(contentLength, 10) : 0;
    } catch (error) {
      console.warn('Could not get file size:', error);
      return 0;
    }
  };
  
  export const validateImageFile = (file) => {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml'];
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    if (!validTypes.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please use PNG, JPEG, or SVG.' };
    }
    
    if (file.size > maxSize) {
      return { valid: false, error: 'File too large. Maximum size is 50MB.' };
    }
    
    return { valid: true };
  };
  
  export const createImageFromFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          resolve({
            file,
            image: img,
            url: e.target.result,
            width: img.width,
            height: img.height
          });
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };
  
  export const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Copy failed:', error);
      return false;
    }
  };
  
  export const openInNewTab = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };
  
  export const calculateTotalSize = (images) => {
    return images.reduce((total, image) => {
      return total + (image.size_mb || 0);
    }, 0);
  };
  
  export const groupImagesByProvider = (images) => {
    return images.reduce((groups, image) => {
      const provider = image.provider || 'unknown';
      if (!groups[provider]) {
        groups[provider] = [];
      }
      groups[provider].push(image);
      return groups;
    }, {});
  };
  
  export const groupImagesByPrompt = (images) => {
    return images.reduce((groups, image) => {
      const promptId = image.prompt_id || 'unknown';
      if (!groups[promptId]) {
        groups[promptId] = [];
      }
      groups[promptId].push(image);
      return groups;
    }, {});
  };