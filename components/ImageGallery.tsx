"use client"

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Download, Loader2 } from 'lucide-react'
import ImagePreview from './ImagePreview'

interface ProcessedImage {
  success: boolean
  original: string
  processed: string
  path?: string
  shadow_applied?: boolean
  shadow_type?: string | null
}

interface ImageGalleryProps {
  images: ProcessedImage[]
  jobId: string
  pipeline?: string
  isLoading?: boolean
  maxVisibleImages?: number
  columns?: 2 | 3 | 4
}

// Validador de imágenes procesadas
function validateProcessedImage(image: any): image is ProcessedImage {
  return (
    image &&
    typeof image === 'object' &&
    typeof image.success === 'boolean' &&
    typeof image.original === 'string' &&
    typeof image.processed === 'string'
  );
}

// Función para normalizar imágenes
function normalizeImage(image: any): ProcessedImage {
  if (validateProcessedImage(image)) {
    return image;
  }

  // Si es un string, crear objeto con valores por defecto
  if (typeof image === 'string') {
    return {
      success: true,
      original: image,
      processed: image,
      path: image,
      shadow_applied: false,
      shadow_type: null
    };
  }

  // Si es un objeto pero no tiene la estructura correcta
  return {
    success: true,
    original: image?.original || image?.processed || image?.filename || 'unknown.jpg',
    processed: image?.processed || image?.filename || 'unknown.jpg',
    path: image?.path || image?.processed || image?.filename || 'unknown.jpg',
    shadow_applied: Boolean(image?.shadow_applied),
    shadow_type: image?.shadow_type || null
  };
}

// Helper function to safely get a string
function safeString(value: any): string {
  // Si es un string directo, devolverlo
  if (typeof value === 'string') return value;

  // Si es un objeto, intentar obtener el nombre del archivo
  if (typeof value === 'object' && value !== null) {
    // Priorizar el campo processed para mostrar la imagen procesada
    if (value.processed) return value.processed;
    // Si no hay processed, buscar en otros campos
    return value.filename || value.name || value.original || 'unknown.jpg';
  }

  // Si no es string ni objeto, devolver valor por defecto
  return 'unknown.jpg';
}

// Helper function to safely check if a string includes a substring
function safeIncludes(value: any, searchStr: string): boolean {
  if (!value || !searchStr) return false;

  let str: string;

  // Si es un objeto con processed o filename
  if (typeof value === 'object' && value !== null) {
    str = value.processed || value.filename || value.name || '';
  } else {
    str = String(value);
  }

  return str.toLowerCase().includes(searchStr.toLowerCase());
}

export default function ImageGallery({
  images,
  jobId,
  pipeline,
  isLoading = false,
  maxVisibleImages = 50,
  columns = 4
}: ImageGalleryProps) {
  const [visibleCount, setVisibleCount] = useState(maxVisibleImages)
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null)
  const [loadedImages, setLoadedImages] = useState<Set<number>>(new Set())
  const observerRef = useRef<IntersectionObserver | null>(null)
  const imageRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  // Intersection Observer for lazy loading
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = Number(entry.target.getAttribute('data-index'))
            setLoadedImages((prev) => new Set([...prev, index]))
          }
        })
      },
      { rootMargin: '50px' }
    )

    return () => {
      observerRef.current?.disconnect()
    }
  }, [])

  // Register image refs with observer
  const setImageRef = useCallback((index: number, element: HTMLDivElement | null) => {
    if (element) {
      imageRefs.current.set(index, element)
      observerRef.current?.observe(element)
    } else {
      const existingElement = imageRefs.current.get(index)
      if (existingElement) {
        observerRef.current?.unobserve(existingElement)
        imageRefs.current.delete(index)
      }
    }
  }, [])

  const visibleImages = images.slice(0, visibleCount)
  const hasMore = images.length > visibleCount

  const loadMore = () => {
    setVisibleCount((prev) => Math.min(prev + maxVisibleImages, images.length))
  }

  const openLightbox = (index: number) => {
    setSelectedImageIndex(index)
  }

  const closeLightbox = () => {
    setSelectedImageIndex(null)
  }

  const goToNext = () => {
    if (selectedImageIndex !== null && selectedImageIndex < images.length - 1) {
      setSelectedImageIndex(selectedImageIndex + 1)
    }
  }

  const goToPrevious = () => {
    if (selectedImageIndex !== null && selectedImageIndex > 0) {
      setSelectedImageIndex(selectedImageIndex - 1)
    }
  }

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const downloadImage = (processedValue: any) => {
    // Open image in new tab instead of forcing download
    let filename: string;

    // Si es un objeto ProcessedImage, usar el campo processed
    if (typeof processedValue === 'object' && processedValue.processed) {
      filename = processedValue.processed;
    } else {
      // Si no, usar safeString para obtener el nombre
      filename = safeString(processedValue);
    }

    console.log('Downloading image:', {
      processedValue,
      filename,
      jobId
    });

    const encodedFilename = encodeURIComponent(filename);
    const imageUrl = `/api/v1/processed/${jobId}/${encodedFilename}`;
    window.open(imageUrl, '_blank', 'noopener,noreferrer');
  }

  const getGridClass = () => {
    switch (columns) {
      case 2:
        return 'grid-cols-1 md:grid-cols-2'
      case 3:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
      case 4:
        return 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
      default:
        return 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Loading previews...</span>
      </div>
    )
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No processed images available
      </div>
    )
  }

  // Validar y normalizar las imágenes antes de renderizar
  const normalizedImages = React.useMemo(() => {
    return images.map(img => normalizeImage(img));
  }, [images]);

  // Filtrar las imágenes visibles y normalizarlas
  const visibleNormalizedImages = normalizedImages.slice(0, visibleCount);

  return (
    <>
      <div className={`grid ${getGridClass()} gap-4`}>
        {visibleNormalizedImages.map((image, index) => {
          const isLoaded = loadedImages.has(index)
          // URL encode the filename to handle spaces and special characters
          const encodedFilename = encodeURIComponent(image.processed)
          const imageUrl = `/api/v1/processed/${jobId}/${encodedFilename}`

          return (
            <div
              key={`${jobId}-${index}`}
              ref={(el) => setImageRef(index, el)}
              data-index={index}
              className="group relative bg-gray-100 rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 aspect-square animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Image Container */}
              <div
                className="w-full h-full cursor-pointer"
                onClick={() => openLightbox(index)}
              >
                {isLoaded ? (
                  <img
                    src={imageUrl}
                    alt={image.original}
                    className="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999"%3EError%3C/text%3E%3C/svg%3E'
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin" />
                  </div>
                )}
              </div>

              {/* Overlay with filename and actions */}
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-xs truncate mb-2" title={image.original}>
                  {image.original}
                </p>
                <div className="flex items-center justify-between">
                  {image.shadow_applied && (
                    <span className="text-xs text-green-300 font-semibold">
                      Shadow: {image.shadow_type || 'drop'}
                    </span>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      downloadImage(image.processed)
                    }}
                    className="ml-auto p-1.5 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
                    title="Download image"
                  >
                    <Download className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>

              {/* Pipeline indicator badge */}
              {pipeline && pipeline.toLowerCase() === 'amazon' && (
                <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-lg">
                  Amazon
                </div>
              )}
              {pipeline && pipeline.toLowerCase() === 'ebay' && (
                <div className="absolute top-2 left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-lg">
                  eBay
                </div>
              )}
              {pipeline && pipeline.toLowerCase() === 'instagram' && (
                <div className="absolute top-2 left-2 bg-pink-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-lg">
                  Instagram
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center mt-8">
          <button
            onClick={loadMore}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors duration-200 shadow-md hover:shadow-lg"
          >
            Load More ({normalizedImages.length - visibleCount} remaining)
          </button>
        </div>
      )}

      {/* Lightbox */}
      {selectedImageIndex !== null && (
        <ImagePreview
          images={normalizedImages}
          currentIndex={selectedImageIndex}
          jobId={jobId}
          pipeline={pipeline}
          onClose={closeLightbox}
          onNext={goToNext}
          onPrevious={goToPrevious}
          onDownload={downloadImage}
        />
      )}

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-out forwards;
        }
      `}</style>
    </>
  )
}
