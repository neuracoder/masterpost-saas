"use client"

import React, { useState } from 'react'

interface ShowcaseImage {
  id: string;
  title: string;
  description: string;
  processingTime: string;
  tier: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

const SHOWCASE_IMAGES: ShowcaseImage[] = [
  {
    id: "bicicleta",
    title: "Complex Vintage Bicycle",
    description: "Multiple angles & spokes",
    processingTime: "6 seconds",
    tier: "Premium"
  },
  {
    id: "lampara",
    title: "Glass & Metal Lamp",
    description: "Transparent glass",
    processingTime: "5 seconds",
    tier: "Premium"
  },
  {
    id: "joyeria",
    title: "Jewelry with Reflections",
    description: "Fine details & shine",
    processingTime: "4 seconds",
    tier: "Premium"
  },
  {
    id: "botella",
    title: "Glass Bottle",
    description: "Transparency & reflections",
    processingTime: "5 seconds",
    tier: "Premium"
  },
  {
    id: "zapato",
    title: "Leather Shoe",
    description: "Textures & details",
    processingTime: "4 seconds",
    tier: "Premium"
  },
  {
    id: "peluche",
    title: "Plush Toy",
    description: "Fuzzy edges",
    processingTime: "5 seconds",
    tier: "Premium"
  }
];

export default function GalleryShowcase() {
  const [selectedImage, setSelectedImage] = useState<ShowcaseImage | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const getImageUrls = (imageId: string) => ({
    original: `${API_URL}/api/v1/gallery/${imageId}/original`,
    processed: `${API_URL}/api/v1/gallery/${imageId}/processed`
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {SHOWCASE_IMAGES.map((image) => {
        const urls = getImageUrls(image.id);
        const isHovered = hoveredId === image.id;

        return (
          <div
            key={image.id}
            className="relative group cursor-pointer bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
            onMouseEnter={() => setHoveredId(image.id)}
            onMouseLeave={() => setHoveredId(null)}
            onClick={() => setSelectedImage(image)}
          >
            {/* Container para las imágenes con aspect ratio fijo */}
            <div className="relative aspect-square overflow-hidden rounded-t-xl">
              {/* Imagen procesada (siempre visible) */}
              <img
                src={urls.processed}
                alt={`${image.title} - Processed`}
                className="absolute inset-0 w-full h-full object-contain"
                loading="lazy"
              />
              
              {/* Imagen original (visible en hover) */}
              <div 
                className={`absolute inset-0 transition-opacity duration-300 ${
                  isHovered ? 'opacity-100' : 'opacity-0'
                }`}
              >
                <img
                  src={urls.original}
                  alt={`${image.title} - Original`}
                  className="w-full h-full object-contain"
                  loading="lazy"
                />
              </div>

              {/* Indicador de hover */}
              <div 
                className={`absolute inset-0 bg-black/50 flex items-center justify-center transition-opacity duration-300 ${
                  isHovered ? 'opacity-100' : 'opacity-0'
                }`}
              >
                <p className="text-white text-lg font-medium">Ver original</p>
              </div>
            </div>

            {/* Información */}
            <div className="p-4">
              <h3 className="text-lg font-semibold text-gray-900">{image.title}</h3>
              <p className="text-sm text-gray-600 mt-1">{image.description}</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-500">{image.processingTime}</span>
                <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                  {image.tier}
                </span>
              </div>
            </div>
          </div>
        );
      })}

      {/* Modal para vista ampliada */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl w-full h-full p-4 flex flex-col items-center justify-center">
            {/* Contenedor de imágenes */}
            <div className="relative w-full max-h-[80vh] flex items-center justify-center">
              {/* Imagen procesada */}
              <img
                src={getImageUrls(selectedImage.id).processed}
                alt={`${selectedImage.title} - Processed`}
                className="max-w-full max-h-[80vh] object-contain"
              />
              
              {/* Hover para ver original */}
              <div 
                className="absolute inset-0 flex items-center justify-center transition-opacity duration-300 cursor-pointer"
                onMouseEnter={(e) => {
                  const target = e.currentTarget;
                  const img = target.querySelector('img');
                  if (img) img.style.opacity = '1';
                }}
                onMouseLeave={(e) => {
                  const target = e.currentTarget;
                  const img = target.querySelector('img');
                  if (img) img.style.opacity = '0';
                }}
              >
                <img
                  src={getImageUrls(selectedImage.id).original}
                  alt={`${selectedImage.title} - Original`}
                  className="max-w-full max-h-[80vh] object-contain opacity-0 transition-opacity duration-300"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <p className="text-white text-xl font-medium bg-black/50 px-4 py-2 rounded-lg">
                    Mantén el cursor aquí para ver el original
                  </p>
                </div>
              </div>
            </div>

            {/* Información */}
            <div className="mt-4 text-center text-white">
              <h2 className="text-2xl font-bold">{selectedImage.title}</h2>
              <p className="text-lg mt-2">{selectedImage.description}</p>
              <div className="flex items-center justify-center space-x-4 mt-2">
                <span>{selectedImage.processingTime}</span>
                <span className="px-3 py-1 bg-purple-500 rounded-full">
                  {selectedImage.tier}
                </span>
              </div>
            </div>

            {/* Botón de cerrar */}
            <button
              className="absolute top-4 right-4 text-white hover:text-gray-300"
              onClick={() => setSelectedImage(null)}
            >
              <svg
                className="w-8 h-8"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}