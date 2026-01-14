import React, { useEffect, useState } from 'react';
import { Image, CheckCircle2, Clock, Zap } from 'lucide-react';

interface ProcessingStatusProps {
  isProcessing: boolean;
  progress: number;
  currentImage: number;
  totalImages: number;
  estimatedTotalTime?: number; // Optional: estimated time in seconds from backend
  pipeline?: string;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  isProcessing,
  progress,
  currentImage,
  totalImages,
  estimatedTotalTime, // Use backend estimate if provided
  pipeline = 'Amazon Compliant'
}) => {
  const [estimatedProgress, setEstimatedProgress] = useState(0);
  const [timeElapsed, setTimeElapsed] = useState(0);

  // Real time based on production data:
  // 100 images = 230 seconds → 2.3 seconds per image
  const SECONDS_PER_IMAGE = 2.3;

  // If backend sends estimated time, use it. Otherwise calculate.
  const TOTAL_ESTIMATED_TIME = estimatedTotalTime || (totalImages * SECONDS_PER_IMAGE);

  useEffect(() => {
    if (!isProcessing) {
      setEstimatedProgress(0);
      setTimeElapsed(0);
      return;
    }

    // Timer that calculates progress based on actual total images
    const startTime = Date.now();

    const timer = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000; // in seconds
      setTimeElapsed(Math.floor(elapsed));

      if (totalImages > 0) {
        // Progress based on time elapsed and TOTAL_ESTIMATED_TIME
        const progressByTime = Math.min((elapsed / TOTAL_ESTIMATED_TIME) * 100, 99);

        // Use the greater between real backend progress and estimated
        const displayProgress = progress > 0 ? Math.max(progress, progressByTime) : progressByTime;
        setEstimatedProgress(Math.floor(displayProgress));
      }
    }, 100); // Update every 100ms for smoothness

    return () => clearInterval(timer);
  }, [isProcessing, totalImages, progress, TOTAL_ESTIMATED_TIME]);

  // Formatear tiempo en mm:ss
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Estado idle
  if (!isProcessing && estimatedProgress === 0) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
        <div className="flex items-center justify-center mb-3">
          <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center shadow-sm">
            <Zap className="w-7 h-7 text-green-500" />
          </div>
        </div>
        <h3 className="text-base font-semibold text-gray-700 text-center mb-1">
          Ready to Process
        </h3>
        <p className="text-sm text-gray-500 text-center">
          Upload images to start
        </p>
      </div>
    );
  }

  const isComplete = estimatedProgress >= 100 || progress >= 100;
  const displayProgress = isComplete ? 100 : estimatedProgress;

  // Calculate estimated time remaining dynamically
  const estimatedTimeRemaining = Math.max(0, Math.ceil(TOTAL_ESTIMATED_TIME - timeElapsed));

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
      {/* Header */}
      <div className="text-center mb-5">
        <h3 className="text-base font-semibold text-gray-800 mb-1">
          {isComplete ? 'Processing Complete!' : 'Processing Images'}
        </h3>
        <p className="text-xs text-gray-500">
          {isComplete
            ? `${totalImages} image${totalImages !== 1 ? 's' : ''} ready`
            : pipeline
          }
        </p>
      </div>

      {/* Animación principal */}
      <div className="relative w-36 h-36 mx-auto mb-5">
        {/* Ondas de fondo animadas */}
        {!isComplete && (
          <>
            <div className="absolute inset-0 rounded-full bg-green-400 opacity-20 animate-ping"
                 style={{ animationDuration: '2s' }} />
            <div className="absolute inset-0 rounded-full bg-green-400 opacity-10 animate-ping"
                 style={{ animationDuration: '3s', animationDelay: '0.5s' }} />
          </>
        )}

        {/* Círculo principal de progreso */}
        <svg className="w-36 h-36 transform -rotate-90">
          <circle
            cx="72"
            cy="72"
            r="66"
            stroke="#E5E7EB"
            strokeWidth="6"
            fill="none"
          />
          <circle
            cx="72"
            cy="72"
            r="66"
            stroke={isComplete ? "#10B981" : "#22C55E"}
            strokeWidth="6"
            fill="none"
            strokeDasharray={414.69}
            strokeDashoffset={414.69 - (414.69 * displayProgress) / 100}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
            style={{
              filter: isComplete
                ? 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.5))'
                : 'drop-shadow(0 0 6px rgba(34, 197, 94, 0.4))'
            }}
          />
        </svg>

        {/* Contenido central */}
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          {isComplete ? (
            <div className="animate-bounce">
              <CheckCircle2 className="w-14 h-14 text-green-500" strokeWidth={2} />
            </div>
          ) : (
            <>
              {/* Rayo rotatorio tamaño w-12 h-12 (48px) */}
              <div className="relative mb-1">
                <div className="animate-spin" style={{ animationDuration: '2s', animationTimingFunction: 'linear' }}>
                  <Zap className="w-12 h-12 text-green-500" fill="currentColor" strokeWidth={1.5} />
                </div>
              </div>

              {/* Porcentaje */}
              <div className="text-3xl font-bold text-green-600">
                {displayProgress}%
              </div>
            </>
          )}
        </div>

      </div>

      {/* Información detallada */}
      {!isComplete && totalImages > 0 && (
        <div className="space-y-3">
          {/* Barra de progreso secundaria */}
          <div className="bg-gray-100 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-700 ease-out"
              style={{ width: `${displayProgress}%` }}
            />
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-gray-600 bg-gray-50 rounded-lg px-2.5 py-2">
              <Image className="w-3.5 h-3.5 text-green-600" />
              <span className="font-medium">
                {currentImage}/{totalImages}
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-gray-600 bg-gray-50 rounded-lg px-2.5 py-2">
              <Clock className="w-3.5 h-3.5 text-green-600" />
              <span className="font-medium">
                {formatTime(timeElapsed)}
              </span>
            </div>
          </div>

          {/* Tiempo estimado restante */}
          {estimatedTimeRemaining > 0 && (
            <div className="text-center pt-1">
              <p className="text-xs text-gray-500">
                ~{formatTime(estimatedTimeRemaining)} remaining
              </p>
            </div>
          )}

          {/* NUEVO: Animación de barras de procesamiento (equalizer) */}
          <div className="flex items-center justify-center gap-1 pt-2">
            <div className="w-1 h-4 bg-green-500 rounded-full animate-pulse"
                 style={{ animationDelay: '0ms', animationDuration: '1s' }} />
            <div className="w-1 h-5 bg-green-500 rounded-full animate-pulse"
                 style={{ animationDelay: '150ms', animationDuration: '1s' }} />
            <div className="w-1 h-6 bg-green-500 rounded-full animate-pulse"
                 style={{ animationDelay: '300ms', animationDuration: '1s' }} />
            <div className="w-1 h-5 bg-green-500 rounded-full animate-pulse"
                 style={{ animationDelay: '450ms', animationDuration: '1s' }} />
            <div className="w-1 h-4 bg-green-500 rounded-full animate-pulse"
                 style={{ animationDelay: '600ms', animationDuration: '1s' }} />
          </div>
        </div>
      )}

      {/* Mensaje de éxito */}
      {isComplete && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm text-green-800 font-medium text-center">
            ✓ Ready to download
          </p>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;
