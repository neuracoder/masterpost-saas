"use client"

import React, { useEffect, useState } from 'react'
import { X, ChevronLeft, ChevronRight, Download, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react'

interface ProcessedImage {
  success: boolean
  original: string
  processed: string
  path?: string
  shadow_applied?: boolean
  shadow_type?: string | null
}

interface ImagePreviewProps {
  images: ProcessedImage[]
  currentIndex: number
  jobId: string
  pipeline?: string
  onClose: () => void
  onNext: () => void
  onPrevious: () => void
  onDownload: (filename: string) => void
}

export default function ImagePreview({
  images,
  currentIndex,
  jobId,
  pipeline,
  onClose,
  onNext,
  onPrevious,
  onDownload
}: ImagePreviewProps) {
  const [zoom, setZoom] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const currentImage = images[currentIndex]
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const imageUrl = `${API_URL}/api/v1/processed/${jobId}/${encodeURIComponent(currentImage.processed)}`

  const hasNext = currentIndex < images.length - 1
  const hasPrevious = currentIndex > 0

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          onClose()
          break
        case 'ArrowRight':
          if (hasNext) onNext()
          break
        case 'ArrowLeft':
          if (hasPrevious) onPrevious()
          break
        case '+':
        case '=':
          setZoom((prev) => Math.min(prev + 0.25, 3))
          break
        case '-':
        case '_':
          setZoom((prev) => Math.max(prev - 0.25, 0.5))
          break
        case '0':
          setZoom(1)
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [hasNext, hasPrevious, onNext, onPrevious, onClose])

  // Reset zoom when changing images
  useEffect(() => {
    setZoom(1)
  }, [currentIndex])

  // Prevent body scroll when lightbox is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.25, 0.5))
  }

  const handleResetZoom = () => {
    setZoom(1)
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const getPipelineBadge = () => {
    if (!pipeline) return null

    const pipelineLower = pipeline.toLowerCase()
    if (pipelineLower === 'amazon') {
      return <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold">Amazon</span>
    }
    if (pipelineLower === 'ebay') {
      return <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-semibold">eBay</span>
    }
    if (pipelineLower === 'instagram') {
      return <span className="bg-pink-500 text-white px-3 py-1 rounded-full text-sm font-semibold">Instagram</span>
    }
    return null
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex flex-col animate-fade-in">
      {/* Header Bar */}
      <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 to-transparent p-4 z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            {getPipelineBadge()}
            <div className="text-white">
              <p className="font-medium">{currentImage.original}</p>
              <p className="text-sm text-gray-300">
                {currentIndex + 1} of {images.length}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Zoom Controls */}
            <button
              onClick={handleZoomOut}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Zoom Out (-)"
              disabled={zoom <= 0.5}
            >
              <ZoomOut className="w-5 h-5 text-white" />
            </button>

            <button
              onClick={handleResetZoom}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white text-sm font-medium"
              title="Reset Zoom (0)"
            >
              {Math.round(zoom * 100)}%
            </button>

            <button
              onClick={handleZoomIn}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Zoom In (+)"
              disabled={zoom >= 3}
            >
              <ZoomIn className="w-5 h-5 text-white" />
            </button>

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Toggle Fullscreen"
            >
              <Maximize2 className="w-5 h-5 text-white" />
            </button>

            {/* Download */}
            <button
              onClick={() => onDownload(currentImage.processed)}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Download Image"
            >
              <Download className="w-5 h-5 text-white" />
            </button>

            {/* Close */}
            <button
              onClick={onClose}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Close (Esc)"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Image Area */}
      <div className="flex-1 flex items-center justify-center p-4 pt-20 pb-20 overflow-auto">
        <div className="relative max-w-full max-h-full">
          <img
            src={imageUrl}
            alt={currentImage.original}
            className="max-w-full max-h-full object-contain transition-transform duration-200"
            style={{ transform: `scale(${zoom})` }}
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23333" width="400" height="400"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-size="20"%3EFailed to load image%3C/text%3E%3C/svg%3E'
            }}
          />
        </div>
      </div>

      {/* Navigation Buttons */}
      {hasPrevious && (
        <button
          onClick={onPrevious}
          className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-all hover:scale-110"
          title="Previous (←)"
        >
          <ChevronLeft className="w-8 h-8 text-white" />
        </button>
      )}

      {hasNext && (
        <button
          onClick={onNext}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-all hover:scale-110"
          title="Next (→)"
        >
          <ChevronRight className="w-8 h-8 text-white" />
        </button>
      )}

      {/* Bottom Info Bar */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between text-white text-sm">
            <div className="flex items-center gap-4">
              {currentImage.shadow_applied && (
                <span className="bg-purple-500/80 px-3 py-1 rounded-full">
                  Shadow: {currentImage.shadow_type || 'drop'}
                </span>
              )}
              <span className="text-gray-300">
                Processed: {currentImage.processed}
              </span>
            </div>
            <div className="text-gray-400">
              Use ← → to navigate • +/- to zoom • Esc to close
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }
      `}</style>
    </div>
  )
}
