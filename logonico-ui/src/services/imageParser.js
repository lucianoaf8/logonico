// services/imageParser.js
/**
 * Parse generated image filename to extract metadata
 * Handles formats like: circuit_orb_dalle3_20250619_172354.png
 */

export const parseFilename = (filename) => {
    const stem = filename.replace(/\.[^/.]+$/, ''); // Remove extension
    const extension = filename.split('.').pop();
    
    // Split by underscore and look for timestamp pattern
    const parts = stem.split('_');
    
    // Find timestamp (pattern: YYYYMMDD_HHMMSS)
    let timestampIdx = -1;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (part.length === 8 && /^\d{8}$/.test(part)) { // YYYYMMDD
        if (i + 1 < parts.length && parts[i + 1].length === 6 && /^\d{6}$/.test(parts[i + 1])) { // HHMMSS
          timestampIdx = i;
          break;
        }
      }
    }
    
    let promptId, model, timestamp, createdAt;
    
    if (timestampIdx > 0) {
      const promptParts = parts.slice(0, timestampIdx - 1); // Everything before model
      model = parts[timestampIdx - 1]; // Model name
      const timestampParts = parts.slice(timestampIdx, timestampIdx + 2); // Date and time
      
      promptId = promptParts.length > 0 ? promptParts.join('_') : 'unknown';
      timestamp = timestampParts.join('_');
      
      // Parse timestamp
      try {
        const dateStr = timestamp.replace('_', 'T');
        const year = dateStr.substr(0, 4);
        const month = dateStr.substr(4, 2);
        const day = dateStr.substr(6, 2);
        const hour = dateStr.substr(9, 2);
        const minute = dateStr.substr(11, 2);
        const second = dateStr.substr(13, 2);
        
        const date = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
        createdAt = date.toLocaleString();
      } catch {
        createdAt = timestamp;
      }
    } else {
      // Fallback parsing
      promptId = parts[0] || 'unknown';
      model = parts[1] || 'unknown';
      createdAt = 'unknown';
    }
    
    // Determine provider from model name
    const provider = determineProvider(model);
    
    return {
      promptId,
      model,
      provider,
      createdAt,
      extension,
      filename,
      timestamp: timestamp || 'unknown'
    };
  };
  
  export const determineProvider = (model) => {
    const modelLower = model.toLowerCase();
    
    if (modelLower.includes('dalle')) {
      return 'openai';
    }
    
    if (modelLower.includes('flux')) {
      if (modelLower.includes('dev') || modelLower.includes('schnell') || modelLower.includes('lora')) {
        return 'together_ai';
      }
      return 'fal_ai';
    }
    
    if (modelLower.includes('galleri5')) {
      return 'replicate';
    }
    
    if (modelLower.includes('ideogram')) {
      return 'replicate';
    }
    
    if (modelLower.includes('recraft')) {
      return 'replicate';
    }
    
    return 'unknown';
  };
  
  export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 MB';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  export const generateImageId = (filename) => {
    return filename.replace(/\.[^/.]+$/, ''); // Remove extension to use as ID
  };