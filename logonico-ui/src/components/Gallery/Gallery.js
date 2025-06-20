import React from 'react';
import { useAppState } from '../../hooks/useAppState';
import ImageCard from '../common/ImageCard';
import FilterButton from '../common/FilterButton';

export default function Gallery() {
  const { allImages, selectedImages, setSelectedImages } = useAppState(); // Removed unused 'stats'
  const [filter,setFilter] = React.useState('all');

  const filtered = allImages.filter(img=>{
    if(filter==='all') return true;
    return img.status===filter||img.provider===filter;
  });

  const toggle = id=>{
    const s = new Set(selectedImages);
    s.has(id)?s.delete(id):s.add(id);
    setSelectedImages(s);
  };

  return (
    <main className="gallery">
      <div className="gallery-header">
        <h2 className="gallery-title">
          Generated Gallery ({filtered.length})
        </h2>
        <div className="gallery-filters">
          {['all','success','openai','replicate','together_ai','fal_ai']
            .map(f=>(
              <FilterButton
                key={f}
                active={filter===f}
                onClick={()=>setFilter(f)}
                label={f==='all'?'All':f}
              />
            ))
          }
        </div>
      </div>
      <div className="gallery-grid">
        {filtered.length
          ? filtered.map(img=>(
              <ImageCard
                key={img.id}
                img={img}
                selected={selectedImages.has(img.id)}
                onClick={()=>toggle(img.id)}
              />
            ))
          : <div className="loading">No images found</div>
        }
      </div>
    </main>
  );
}