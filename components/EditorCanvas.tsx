"use client"

import React, { useRef, useEffect, useState } from 'react';

interface ImageData {
  localUrl: string;
  serverPath: string;
  filename: string;
  jobId: string;
  sessionId?: string;
}

interface EditorCanvasProps {
  imageData: ImageData;
  onImageEdited: (downloadUrl: string) => void;
  onCancel?: () => void;
}

const EditorCanvas: React.FC<EditorCanvasProps> = ({ imageData, onImageEdited, onCancel }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const originalImageRef = useRef<HTMLImageElement | null>(null);

  const [isCanvasReady, setIsCanvasReady] = useState(false);
  const [tool, setTool] = useState<'erase' | 'white-brush' | 'restore'>('erase');
  const [brushSize, setBrushSize] = useState(20);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // NUEVO - Estados para zoom y pan
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  console.log("🎨 EditorCanvas - Estado actual:", {
    tool,
    brushSize,
    zoomLevel,
    isCanvasReady,
    hasChanges
  });

  useEffect(() => {
    if (imageData && imageData.localUrl && canvasRef.current) {
      console.log("✅ Condiciones cumplidas, cargando imagen...");
      loadImageToCanvas();
    }
  }, [imageData]);

  const loadImageToCanvas = () => {
    console.log("🖼️ Cargando imagen con transparencia correcta...");

    const canvas = canvasRef.current;
    if (!canvas) {
      console.error("❌ Canvas no encontrado");
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error("❌ No se pudo obtener contexto 2D");
      return;
    }

    const img = new Image();

    img.onload = () => {
      console.log("✅ Imagen cargada - configurando canvas para transparencia");

      // Configurar canvas con transparencia
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;

      // IMPORTANTE: Limpiar con transparencia, no blanco
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // FONDO A CUADROS PARA VER TRANSPARENCIA
      drawTransparencyBackground(ctx, canvas.width, canvas.height);

      // Dibujar imagen original
      ctx.drawImage(img, 0, 0);

      // Guardar referencia a la imagen original
      originalImageRef.current = img;

      setIsCanvasReady(true);
      setHasChanges(false);
      console.log("🎨 Canvas listo con soporte de transparencia");
    };

    img.onerror = (error) => {
      console.error("❌ Error cargando imagen:", error);
    };

    img.src = imageData.localUrl;
  };

  // Fondo a cuadros para visualizar transparencia
  const drawTransparencyBackground = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const size = 20;
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = '#E0E0E0';
    for (let y = 0; y < height; y += size) {
      for (let x = 0; x < width; x += size) {
        if ((x / size + y / size) % 2 === 0) {
          ctx.fillRect(x, y, size, size);
        }
      }
    }
  };

  const getMousePosition = (e: React.MouseEvent): { x: number; y: number } => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isCanvasReady) {
      console.log("⚠️ Canvas no listo, ignorando mouse down");
      return;
    }

    const pos = getMousePosition(e);

    if (e.altKey || e.button === 1) {
      // Pan mode (Alt + click o rueda del mouse)
      setIsDragging(true);
      setDragStart(pos);
      return;
    }

    setIsDrawing(true);
    startDrawing(pos.x, pos.y);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isCanvasReady) return;

    const pos = getMousePosition(e);

    if (isDragging) {
      // Pan/arrastrar canvas
      const deltaX = pos.x - dragStart.x;
      const deltaY = pos.y - dragStart.y;
      setPanOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      return;
    }

    if (isDrawing) {
      draw(pos.x, pos.y);
    }
  };

  const handleMouseUp = () => {
    if (isDrawing) {
      setIsDrawing(false);
    }
    if (isDragging) {
      setIsDragging(false);
    }
  };

  const startDrawing = (x: number, y: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    console.log(`🖌️ Iniciando dibujo con herramienta: ${tool}`);

    // CONFIGURACIÓN CORRECTA DE HERRAMIENTAS
    if (tool === 'erase') {
      // BORRAR = HACER TRANSPARENTE
      ctx.globalCompositeOperation = 'destination-out';
      console.log("🧽 Modo BORRAR - destination-out");
    } else if (tool === 'restore') {
      // RESTAURAR = COPIAR DE IMAGEN ORIGINAL
      ctx.globalCompositeOperation = 'source-over';
      console.log("🔄 Modo RESTAURAR - copiando original");
    } else if (tool === 'white-brush') {
      // PINCEL BLANCO NORMAL
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = '#FFFFFF';
      ctx.fillStyle = '#FFFFFF';
      console.log("⚪ Modo PINCEL BLANCO - color blanco");
    }

    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(x, y);

    // Para herramientas que no borran, pintar primer punto
    if (tool !== 'erase') {
      if (tool === 'restore' && originalImageRef.current) {
        // Para restaurar, copiar del original
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        if (tempCtx && originalImageRef.current) {
          tempCanvas.width = originalImageRef.current.width;
          tempCanvas.height = originalImageRef.current.height;
          tempCtx.drawImage(originalImageRef.current, 0, 0);

          ctx.drawImage(tempCanvas,
            x - brushSize/2, y - brushSize/2, brushSize, brushSize,
            x - brushSize/2, y - brushSize/2, brushSize, brushSize
          );
        }
      } else {
        // Para pincel blanco
        ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.beginPath();
      ctx.moveTo(x, y);
    }

    setHasChanges(true);
  };

  const draw = (x: number, y: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (tool === 'restore' && originalImageRef.current) {
      // Para restaurar, copiar línea del original
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d');
      if (tempCtx && originalImageRef.current) {
        tempCanvas.width = originalImageRef.current.width;
        tempCanvas.height = originalImageRef.current.height;
        tempCtx.drawImage(originalImageRef.current, 0, 0);

        // Dibujar línea de restauración
        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.moveTo(x, y);
      }
    } else {
      // Para borrar y pincel blanco
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.moveTo(x, y);
    }
  };

  // Funciones de zoom
  const handleZoom = (delta: number) => {
    const newZoom = Math.max(0.1, Math.min(5, zoomLevel + delta));
    setZoomLevel(newZoom);
    console.log(`🔍 Zoom ajustado a: ${newZoom.toFixed(1)}x`);
  };

  const resetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    console.log("🔄 Vista resetada");
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    handleZoom(delta);
  };

  const saveImageToServer = async () => {
    console.log("💾 Guardando imagen con transparencia...");

    const canvas = canvasRef.current;
    if (!canvas) {
      console.error("❌ Canvas no disponible");
      return;
    }

    setIsSaving(true);

    try {
      // IMPORTANTE: Guardar como PNG para mantener transparencia
      canvas.toBlob(async (blob) => {
        if (!blob) {
          throw new Error('Error al crear blob de la imagen');
        }

        console.log("📦 Blob creado:", blob.size, "bytes");

        const formData = new FormData();
        const filename = `edited_${imageData.filename.replace(/\.[^/.]+$/, ".png")}`;
        formData.append('edited_image', blob, filename);
        formData.append('job_id', imageData.jobId || imageData.sessionId || '');

        console.log("📤 Enviando imagen editada al servidor...");

        const response = await fetch('/api/v1/manual-editor/save-edited', {
          method: 'POST',
          body: formData
        });

        console.log("📥 Respuesta del servidor:", response.status);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log("✅ Imagen guardada exitosamente:", result);

        // Llamar callback con la URL de descarga
        if (result.download_url) {
          onImageEdited(result.download_url);
        }

        setHasChanges(false);

        // Mostrar mensaje informativo
        const successMessage = `✅ ¡Imagen guardada exitosamente!\n\n` +
          `📦 Nombre: ${result.filename}\n` +
          `🌐 Disponible para descarga desde el servidor\n` +
          `🎨 Formato: PNG con transparencia\n\n` +
          `La imagen editada está lista para descargar.`;

        alert(successMessage);

      }, 'image/png'); // IMPORTANTE: PNG para transparencia

    } catch (error) {
      console.error("❌ Error guardando imagen:", error);
      alert(`❌ Error al guardar: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setIsSaving(false);
    }
  };

  const downloadImage = () => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error("❌ Canvas no disponible para descargar");
      return;
    }

    console.log("📥 Iniciando descarga directa...");

    try {
      canvas.toBlob((blob) => {
        if (!blob) {
          console.error("❌ Error al crear blob para descarga");
          return;
        }

        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `edited_${imageData.filename.replace(/\.[^/.]+$/, '')}.png`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);

        console.log("✅ Descarga iniciada");

      }, 'image/png');

    } catch (error) {
      console.error("❌ Error en descarga:", error);
      alert(`❌ Error al descargar: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  // Si no hay datos, mostrar mensaje
  if (!imageData) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h3>❌ No hay datos de imagen</h3>
        <p>El componente EditorCanvas no recibió datos de imagen</p>
      </div>
    );
  }

  if (!imageData.localUrl) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h3>❌ No hay URL de imagen</h3>
        <p>Los datos de imagen no incluyen localUrl</p>
        <pre>{JSON.stringify(imageData, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div className="editor-canvas-container" style={{ display: 'flex', gap: '20px', padding: '20px' }}>

      {/* PANEL DE HERRAMIENTAS MEJORADO */}
      <div style={{
        width: '320px',
        background: '#f8f9fa',
        padding: '20px',
        borderRadius: '10px',
        height: 'fit-content'
      }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333' }}>🛠️ Herramientas de Edición</h3>

        {/* Herramientas principales */}
        <div style={{ marginBottom: '25px' }}>
          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>🎨 Herramientas</h4>

          <button
            onClick={() => setTool('erase')}
            style={{
              width: '100%',
              padding: '12px',
              margin: '4px 0',
              background: tool === 'erase' ? '#dc3545' : '#fff',
              color: tool === 'erase' ? '#fff' : '#000',
              border: '2px solid #dc3545',
              cursor: 'pointer',
              borderRadius: '6px',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            🧽 Borrar Fondo (Transparente)
          </button>

          <button
            onClick={() => setTool('white-brush')}
            style={{
              width: '100%',
              padding: '12px',
              margin: '4px 0',
              background: tool === 'white-brush' ? '#6c757d' : '#fff',
              color: tool === 'white-brush' ? '#fff' : '#000',
              border: '2px solid #6c757d',
              cursor: 'pointer',
              borderRadius: '6px',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            ⚪ Pincel Blanco
          </button>

          <button
            onClick={() => setTool('restore')}
            style={{
              width: '100%',
              padding: '12px',
              margin: '4px 0',
              background: tool === 'restore' ? '#28a745' : '#fff',
              color: tool === 'restore' ? '#fff' : '#000',
              border: '2px solid #28a745',
              cursor: 'pointer',
              borderRadius: '6px',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            🔄 Restaurar Original
          </button>
        </div>

        {/* Control de tamaño de pincel */}
        <div style={{ marginBottom: '25px' }}>
          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>📏 Tamaño del Pincel: {brushSize}px</h4>
          <input
            type="range"
            min="1"
            max="100"
            value={brushSize}
            onChange={(e) => setBrushSize(parseInt(e.target.value))}
            style={{ width: '100%', marginBottom: '8px' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666' }}>
            <span>Fino (1px)</span>
            <span>Grueso (100px)</span>
          </div>
        </div>

        {/* Controles de zoom */}
        <div style={{ marginBottom: '25px' }}>
          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>🔍 Zoom: {zoomLevel.toFixed(1)}x</h4>
          <div style={{ display: 'flex', gap: '6px', marginBottom: '10px' }}>
            <button
              onClick={() => handleZoom(-0.2)}
              style={{
                flex: 1,
                padding: '8px',
                background: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              🔍➖
            </button>
            <button
              onClick={() => handleZoom(0.2)}
              style={{
                flex: 1,
                padding: '8px',
                background: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              🔍➕
            </button>
            <button
              onClick={resetView}
              style={{
                flex: 1,
                padding: '8px',
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              🎯
            </button>
          </div>
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={zoomLevel}
            onChange={(e) => setZoomLevel(parseFloat(e.target.value))}
            style={{ width: '100%', marginBottom: '8px' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666' }}>
            <span>10%</span>
            <span>500%</span>
          </div>
        </div>

        {/* Estados */}
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>📊 Estado</h4>
          <div style={{ fontSize: '13px' }}>
            <p><strong>Archivo:</strong> {imageData.filename}</p>
            <p><strong>Canvas:</strong> {isCanvasReady ? '✅ Listo' : '⏳ Cargando'}</p>
            <p><strong>Herramienta:</strong> {tool === 'erase' ? '🧽 Borrar' : tool === 'white-brush' ? '⚪ Pincel' : '🔄 Restaurar'}</p>
            <p><strong>Pincel:</strong> {brushSize}px</p>
            <p><strong>Zoom:</strong> {zoomLevel.toFixed(1)}x</p>
            <p><strong>Cambios:</strong> {hasChanges ? '🟡 Sin guardar' : '✅ Guardado'}</p>
          </div>
        </div>

        {/* Instrucciones */}
        <div style={{
          background: '#e9ecef',
          padding: '12px',
          borderRadius: '6px',
          fontSize: '12px',
          marginBottom: '20px'
        }}>
          <strong>💡 Instrucciones:</strong>
          <ul style={{ margin: '8px 0', paddingLeft: '15px', lineHeight: '1.4' }}>
            <li>🧽 <strong>Borrar:</strong> Hace transparente (sin fondo)</li>
            <li>⚪ <strong>Pincel Blanco:</strong> Pinta color blanco sólido</li>
            <li>🔄 <strong>Restaurar:</strong> Recupera imagen original</li>
            <li>🔍 <strong>Zoom:</strong> Rueda del mouse o controles</li>
            <li>✋ <strong>Pan:</strong> Alt + arrastrar para mover</li>
            <li>💾 <strong>Formato:</strong> Se guarda como PNG</li>
          </ul>
        </div>

        {/* Advertencias */}
        {hasChanges && (
          <div style={{
            padding: '10px',
            background: '#fff3cd',
            border: '1px solid #ffeaa7',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#856404',
            marginBottom: '15px'
          }}>
            ⚠️ Tienes cambios sin guardar
          </div>
        )}

        {/* Acciones */}
        <div>
          <button
            onClick={() => {
              loadImageToCanvas();
              resetView();
              setHasChanges(false);
            }}
            style={{
              width: '100%',
              padding: '10px',
              margin: '4px 0',
              background: '#ffc107',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            🔄 Reiniciar Todo
          </button>

          <button
            onClick={saveImageToServer}
            disabled={!hasChanges || isSaving}
            style={{
              width: '100%',
              padding: '12px',
              margin: '6px 0',
              background: hasChanges && !isSaving ? '#28a745' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: hasChanges && !isSaving ? 'pointer' : 'not-allowed',
              fontWeight: 'bold',
              fontSize: '15px'
            }}
          >
            {isSaving ? '💾 Guardando...' : '💾 Guardar como PNG'}
          </button>

          <button
            onClick={downloadImage}
            disabled={!isCanvasReady}
            style={{
              width: '100%',
              padding: '10px',
              margin: '4px 0',
              background: isCanvasReady ? '#17a2b8' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: isCanvasReady ? 'pointer' : 'not-allowed',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            📥 Descarga Directa
          </button>

          {onCancel && (
            <button
              onClick={onCancel}
              style={{
                width: '100%',
                padding: '10px',
                margin: '8px 0 0 0',
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              ❌ Cancelar
            </button>
          )}
        </div>
      </div>

      {/* CANVAS CON ZOOM Y PAN */}
      <div
        ref={containerRef}
        style={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#f0f0f0',
          borderRadius: '10px',
          padding: '20px',
          minHeight: '600px',
          overflow: 'hidden',
          position: 'relative'
        }}
        onWheel={handleWheel}
      >
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          style={{
            maxWidth: 'none',
            maxHeight: 'none',
            width: 'auto',
            height: 'auto',
            border: '2px solid #ddd',
            cursor: isCanvasReady ? (isDragging ? 'grabbing' : tool === 'erase' ? 'crosshair' : 'copy') : 'wait',
            background: 'white',
            transform: `scale(${zoomLevel}) translate(${panOffset.x}px, ${panOffset.y}px)`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.1s ease',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
          }}
        />

        {!isCanvasReady && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            background: 'rgba(255,255,255,0.95)',
            padding: '30px',
            borderRadius: '10px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}>
            <div style={{ fontSize: '32px', marginBottom: '15px' }}>⏳</div>
            <div style={{ fontSize: '16px', fontWeight: 'bold' }}>Cargando imagen...</div>
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              Preparando canvas con transparencia
            </div>
          </div>
        )}

        {/* Indicador de zoom en esquina */}
        {isCanvasReady && (
          <div style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}>
            🔍 {zoomLevel.toFixed(1)}x
          </div>
        )}
      </div>
    </div>
  );
};

export default EditorCanvas;