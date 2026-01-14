import React from 'react';
import { Loader2, Image, CheckCircle } from 'lucide-react';

interface ProcessingAnimationProps {
  isProcessing: boolean;
  progress?: number;
  currentImage?: number;
  totalImages?: number;
  platform?: string;
}

const ProcessingAnimation: React.FC<ProcessingAnimationProps> = ({
  isProcessing,
  progress = 0,
  currentImage = 0,
  totalImages = 0,
  platform = 'Amazon'
}) => {
  if (!isProcessing && progress === 0) return null;

  const isComplete = progress >= 100;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all">

        {/* Header */}
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-2">
            {isComplete ? '¡Procesamiento Completo!' : 'Procesando Imágenes'}
          </h3>
          <p className="text-gray-600">
            {isComplete
              ? `${totalImages} imagen${totalImages !== 1 ? 'es' : ''} lista${totalImages !== 1 ? 's' : ''} para ${platform}`
              : `Optimizando para ${platform}...`
            }
          </p>
        </div>

        {/* Animación circular principal */}
        <div className="relative flex items-center justify-center mb-8">
          {/* Círculo de fondo */}
          <svg className="w-48 h-48 transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="#E5E7EB"
              strokeWidth="12"
              fill="none"
            />
            {/* Círculo de progreso animado */}
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke={isComplete ? "#10B981" : "url(#gradient)"}
              strokeWidth="12"
              fill="none"
              strokeDasharray={552.92}
              strokeDashoffset={552.92 - (552.92 * progress) / 100}
              strokeLinecap="round"
              className="transition-all duration-300 ease-out"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8B5CF6" />
                <stop offset="100%" stopColor="#EC4899" />
              </linearGradient>
            </defs>
          </svg>

          {/* Contenido central */}
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            {isComplete ? (
              <div className="animate-bounce">
                <CheckCircle className="w-16 h-16 text-green-500" strokeWidth={2.5} />
              </div>
            ) : (
              <>
                <Loader2
                  className="w-16 h-16 text-purple-600 animate-spin mb-2"
                  strokeWidth={2.5}
                />
                <span className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {progress}%
                </span>
              </>
            )}
          </div>
        </div>

        {/* Información de progreso */}
        {!isComplete && totalImages > 0 && (
          <div className="space-y-4">
            {/* Barra de progreso secundaria */}
            <div className="bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-500 ease-out rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Contador de imágenes */}
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <Image className="w-4 h-4" />
                <span>Imagen {currentImage} de {totalImages}</span>
              </div>
              <span className="text-purple-600 font-semibold">
                {Math.round((currentImage / totalImages) * 100)}%
              </span>
            </div>

            {/* Indicador de actividad */}
            <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
              </div>
              <span>Aplicando optimizaciones...</span>
            </div>
          </div>
        )}

        {/* Mensaje de completado */}
        {isComplete && (
          <div className="mt-6 p-4 bg-green-50 rounded-xl border border-green-200">
            <p className="text-green-800 text-center font-medium">
              ✨ Tus imágenes están listas para descargar
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingAnimation;
