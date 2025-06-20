// components/Gallery/ImageGrid.js
import React, { useMemo } from 'react';
import styled from 'styled-components';
import ImageCard from '../common/ImageCard';
import LoadingSpinner from '../common/LoadingSpinner';

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  flex: 1;
  padding: 0;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 8px;
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  text-align: center;
  grid-column: 1 / -1;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const EmptyTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
`;

const EmptyDescription = styled.p`
  font-size: 14px;
  line-height: 1.5;
  max-width: 300px;
`;

const ImageGrid = ({
  images = [],
  isLoading = false,
  selectedImages = new Set(),
  onImageSelect,
  onImageHover,
  filter = 'all',
  searchQuery = '',
  className
}) => {
  // Filter and search images
  const filteredImages = useMemo(() => {
    let filtered = images;

    // Apply filter
    if (filter !== 'all') {
      filtered = filtered.filter(image => {
        return image.status === filter || image.provider === filter;
      });
    }

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(image => {
        return (
          image.prompt_id?.toLowerCase().includes(query) ||
          image.model?.toLowerCase().includes(query) ||
          image.provider?.toLowerCase().includes(query) ||
          image.filename?.toLowerCase().includes(query)
        );
      });
    }

    return filtered;
  }, [images, filter, searchQuery]);

  const handleImageClick = (image) => {
    if (onImageSelect) {
      onImageSelect(image);
    }
  };

  const handleImageHover = (image, isHovering) => {
    if (onImageHover) {
      onImageHover(image, isHovering);
    }
  };

  if (isLoading) {
    return (
      <GridContainer>
        <div style={{ gridColumn: '1 / -1' }}>
          <LoadingSpinner text="Loading images..." />
        </div>
      </GridContainer>
    );
  }

  if (filteredImages.length === 0) {
    return (
      <GridContainer>
        <EmptyState>
          <EmptyIcon>🖼️</EmptyIcon>
          <EmptyTitle>
            {searchQuery ? 'No matching images' : 'No images found'}
          </EmptyTitle>
          <EmptyDescription>
            {searchQuery 
              ? `No images match "${searchQuery}". Try a different search term.`
              : images.length === 0
                ? 'No images have been generated yet. Start by running the generation pipeline.'
                : `No images match the current filter "${filter}". Try selecting a different filter.`
            }
          </EmptyDescription>
        </EmptyState>
      </GridContainer>
    );
  }

  return (
    <GridContainer className={className}>
      {filteredImages.map((image) => (
        <ImageCard
          key={image.id}
          image={image}
          isSelected={selectedImages.has(image.id)}
          onClick={() => handleImageClick(image)}
          onMouseEnter={() => handleImageHover(image, true)}
          onMouseLeave={() => handleImageHover(image, false)}
        />
      ))}
    </GridContainer>
  );
};

// Virtualized version for large datasets
export const VirtualizedImageGrid = ({
  images,
  height = 600,
  itemHeight = 140,
  itemsPerRow = 6,
  ...props
}) => {
  // This would use react-window or react-virtualized for performance
  // For now, fallback to regular grid with a warning for large datasets
  
  if (images.length > 1000) {
    console.warn('Large image dataset detected. Consider implementing virtualization for better performance.');
  }

  return (
    <div style={{ height, overflow: 'auto' }}>
      <ImageGrid images={images} {...props} />
    </div>
  );
};

export default ImageGrid;