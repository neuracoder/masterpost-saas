import React from 'react';

interface ProcessingSpinnerProps {
  progress?: number;
  isProcessing?: boolean;
  currentImage?: number;
  totalImages?: number;
}

const ProcessingSpinner: React.FC<ProcessingSpinnerProps> = ({
  progress = 0,
  isProcessing = false,
  currentImage = 0,
  totalImages = 0
}) => {
  if (!isProcessing) return null;

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-8">
      {/* Spinner circular animado */}
      <div className="relative w-24 h-24">
        {/* Círculo de fondo */}
        <svg className="w-24 h-24 transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r="44"
            stroke="#E5E7EB"
            strokeWidth="6"
            fill="none"
          />
          {/* Círculo de progreso */}
          <circle
            cx="48"
            cy="48"
            r="44"
            stroke="url(#spinner-gradient)"
            strokeWidth="6"
            fill="none"
            strokeDasharray={276.46}
            strokeDashoffset={276.46 - (276.46 * progress) / 100}
            strokeLinecap="round"
            className="transition-all duration-300 ease-out"
          />
          <defs>
            <linearGradient id="spinner-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8B5CF6" />
              <stop offset="50%" stopColor="#A855F7" />
              <stop offset="100%" stopColor="#EC4899" />
            </linearGradient>
          </defs>
        </svg>

        {/* Porcentaje en el centro */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {progress}%
            </div>
          </div>
        </div>

        {/* Ícono rotatorio decorativo */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="absolute w-3 h-3 bg-purple-600 rounded-full animate-spin"
            style={{
              top: '6px',
              left: '50%',
              transform: 'translateX(-50%)',
              animationDuration: '2s'
            }}
          />
        </div>
      </div>

      {/* Status text */}
      <div className="text-center">
        <p className="text-sm font-medium text-gray-700 mb-1">
          Processing images...
        </p>
        {totalImages > 0 && (
          <p className="text-xs text-gray-500 mb-2">
            Image {currentImage} of {totalImages}
          </p>
        )}
        <div className="flex items-center justify-center gap-1">
          <span className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '200ms' }} />
          <span className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '400ms' }} />
        </div>
      </div>

      {/* Estimated time */}
      {currentImage > 0 && totalImages > 0 && (
        <div className="text-xs text-gray-500">
          Estimated time: {Math.round((totalImages - currentImage) * 2.5)} seconds
        </div>
      )}
    </div>
  );
};

export default ProcessingSpinner;
