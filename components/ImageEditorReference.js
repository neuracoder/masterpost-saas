import React, { useState, useRef, useEffect } from 'react';
import { 
  Palette, 
  Type, 
  Smile, 
  Image as ImageIcon, 
  Square, 
  Filter,
  Sliders,
  RotateCcw,
  Download,
  X,
  Plus,
  Minus,
  Move,
  AlignCenter,
  Bold,
  Italic,
  Circle,
  Triangle,
  ArrowRight,
  Crop,
  Layers,
  ChevronUp,
  ChevronDown,
  Eye,
  EyeOff,
  RotateCw,
  FlipHorizontal,
  FlipVertical
} from 'lucide-react';

// 🎨 Configuración API de Giphy Stickers
const GIPHY_API_KEY = '98MUB4ScqiTpP5nEiBM6YOqxHDBVSagP';
const GIPHY_BASE_URL = 'https://api.giphy.com/v1/stickers';

const ImageEditor = ({ imageData, onSave, onCancel }) => {
  // Early return with error UI if essential props are missing
  if (!imageData || !imageData.file || !imageData.preview) {
    console.error('ImageEditor: Missing required imageData props:', { imageData });
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div className="bg-white p-6 rounded-lg max-w-md mx-auto text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Error: Datos de imagen inválidos</h3>
          <p className="text-gray-600 mb-4">
            No se pudo cargar el editor de imagen. Los datos de imagen están incompletos.
          </p>
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  }

  if (!onSave || !onCancel) {
    console.error('ImageEditor: Missing required callback functions:', { onSave, onCancel });
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div className="bg-white p-6 rounded-lg max-w-md mx-auto text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Error: Configuración inválida</h3>
          <p className="text-gray-600 mb-4">
            El editor de imagen no está configurado correctamente.
          </p>
        </div>
      </div>
    );
  }

  const canvasRef = useRef(null);
  const [image, setImage] = useState(null);
  const [activeTab, setActiveTab] = useState('filters');
  
  // Estados para edición
  const [filters, setFilters] = useState({
    brightness: 100,
    contrast: 100,
    saturation: 100,
    blur: 0,
    sepia: 0,
    grayscale: 0,
    hue: 0
  });
  
  const [textElements, setTextElements] = useState([]);
  const [selectedTextId, setSelectedTextId] = useState(null);
  const [selectedElementId, setSelectedElementId] = useState(null);
  const [selectedElementType, setSelectedElementType] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [textStyle, setTextStyle] = useState({
    fontSize: 32,
    color: '#FFFFFF',
    fontFamily: 'Arial',
    fontWeight: 'bold',
    textAlign: 'center',
    shadow: true,
    outline: true
  });

  // Estados para drag & drop de texto
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [hoveredTextId, setHoveredTextId] = useState(null);
  const [hoveredElementId, setHoveredElementId] = useState(null);
  
  // Estados para redimensionado de texto
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState(null); // 'nw', 'ne', 'sw', 'se'
  const [resizeStartData, setResizeStartData] = useState(null);

  // Estados para elementos decorativos
  const [decorativeElements, setDecorativeElements] = useState([]);
  const [selectedFrame, setSelectedFrame] = useState('none');
  
  // Estados para formas geométricas
  const [shapes, setShapes] = useState([]);
  const [selectedShape, setSelectedShape] = useState(null);
  
  // Estados para líneas y flechas
  const [lines, setLines] = useState([]);
  const [selectedLine, setSelectedLine] = useState(null);
  
  // Estados para sistema de capas
  const [layers, setLayers] = useState([]);
  const [selectedLayer, setSelectedLayer] = useState(null);
  
  // Estados para herramienta de recorte
  const [cropMode, setCropMode] = useState(false);
  const [cropArea, setCropArea] = useState(null);
  const [cropAspectRatio, setCropAspectRatio] = useState('free');
  
  // Estados para múltiple selección
  const [multiSelect, setMultiSelect] = useState(false);
  const [selectedElements, setSelectedElements] = useState([]);
  
  // Estados para fondos de texto
  const [textBackgrounds, setTextBackgrounds] = useState([]);
  
  // Estados para transformaciones
  const [isRotating, setIsRotating] = useState(false);
  
  
  // Estados para Giphy Stickers
  const [giphyStickers, setGiphyStickers] = useState([]);
  const [isLoadingStickers, setIsLoadingStickers] = useState(false);
  const [stickerQuery, setStickerQuery] = useState('trending');
  const [stickerCategory, setStickerCategory] = useState('trending');
  const [currentStickers, setCurrentStickers] = useState([]);
  const [stickerLoading, setStickerLoading] = useState(false);
  const [stickerSearchQuery, setStickerSearchQuery] = useState('');

  useEffect(() => {
    if (imageData) {
      const img = new Image();
      img.crossOrigin = 'Anonymous'; //  <-- IMPORTANTE para CORS
      img.onload = () => {
        setImage(img);
        drawCanvas(img);
      };
      
      // Usar directamente la URL del preview (ya viene proxificada desde App.js)
      img.src = imageData.preview;
    }
  }, [imageData]);

  useEffect(() => {
    if (image) {
      drawCanvas(image);
    }
  }, [filters, textElements, decorativeElements, shapes, lines, textBackgrounds, selectedFrame, cropArea, image]);

  // Initialize Giphy stickers with trending category
  useEffect(() => {
    console.log('🚀 Inicializando stickers trending');
    searchGiphyStickers('', 'trending');
  }, []);

  const drawCanvas = (img) => {
    const canvas = canvasRef.current;
    if (!canvas || !img) {
      console.warn('DrawCanvas: Missing canvas or image:', { hasCanvas: !!canvas, hasImg: !!img });
      return;
    }
    
    let ctx;
    try {
      ctx = canvas.getContext('2d');
      if (!ctx) {
        console.error('DrawCanvas: Could not get 2d context from canvas');
        return;
      }
    } catch (error) {
      console.error('DrawCanvas: Error getting canvas context:', error);
      return;
    }
    
    // Configurar tamaño del canvas manteniendo aspect ratio
    const maxSize = 600;
    const imgAspectRatio = img.naturalWidth / img.naturalHeight;
    
    if (imgAspectRatio > 1) {
      // Imagen más ancha que alta
      canvas.width = maxSize;
      canvas.height = maxSize / imgAspectRatio;
    } else {
      // Imagen más alta que ancha
      canvas.width = maxSize * imgAspectRatio;
      canvas.height = maxSize;
    }
    
    // Aplicar filtros
    ctx.filter = `
      brightness(${filters.brightness}%) 
      contrast(${filters.contrast}%) 
      saturate(${filters.saturation}%) 
      blur(${filters.blur}px) 
      sepia(${filters.sepia}%) 
      grayscale(${filters.grayscale}%) 
      hue-rotate(${filters.hue}deg)
    `;
    
    // Dibujar imagen principal
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    // Resetear filtros para elementos decorativos
    ctx.filter = 'none';
    
    // Dibujar marco si está seleccionado
    drawFrame(ctx, canvas);
    
    // Dibujar fondos de texto (más atrás)
    textBackgrounds.forEach(bg => {
      drawTextBackground(ctx, bg);
    });
    
    // Dibujar formas geométricas (detrás del texto)
    shapes.forEach(shape => {
      drawShape(ctx, shape);
    });
    
    // Dibujar líneas y flechas (detrás del texto)
    lines.forEach(line => {
      drawLine(ctx, line);
    });
    
    // Dibujar elementos de texto (encima de formas)
    textElements.forEach(textEl => {
      drawText(ctx, textEl);
    });
    
    // Dibujar elementos decorativos (emojis, iconos) - al frente
    decorativeElements.forEach(element => {
      drawDecorativeElement(ctx, element);
    });
    
    // Dibujar área de recorte si está activa (siempre al frente)
    if (cropMode && cropArea) {
      drawCropArea(ctx, cropArea);
    }
  };

  //  MARCOS AVANZADOS ÚNICOS
  const frameStyles = {
    none: { name: 'Sin marco', preview: '' },
    classic: { name: 'Clásico Dorado', preview: '', description: 'Marco dorado elegante' },
    modern: { name: 'Gradiente Moderno', preview: '', description: 'Gradiente azul-púrpura' },
    vintage: { name: 'Vintage Madera', preview: '', description: 'Estilo madera envejecida' },
    neon: { name: 'Neón Brillante', preview: '', description: 'Efecto neón colorido' },
    polaroid: { name: 'Polaroid Retro', preview: '', description: 'Marco de foto instantánea' },
    film: { name: 'Rollo de Película', preview: '️', description: 'Bordes de película' },
    gold_ornate: { name: 'Oro Ornamentado', preview: '', description: 'Decoración dorada lujosa' },
    silver_tech: { name: 'Tech Plateado', preview: '️', description: 'Marco metálico futurista' },
    rainbow_gradient: { name: 'Arcoíris', preview: '', description: 'Gradiente arcoíris' },
    diamond: { name: 'Diamante', preview: '', description: 'Efecto cristal diamante' },
    fire: { name: 'Llamas', preview: '', description: 'Marco de fuego ardiente' },
    ice: { name: 'Hielo', preview: '️', description: 'Cristal de hielo' },
    nature: { name: 'Naturaleza', preview: '', description: 'Marco orgánico natural' },
    galaxy: { name: 'Galaxia', preview: '', description: 'Espacio cósmico' },
    geometric: { name: 'Geométrico', preview: '', description: 'Patrones geométricos' },
    watercolor: { name: 'Acuarela', preview: '', description: 'Efecto acuarela artística' },
    grunge: { name: 'Grunge', preview: '', description: 'Textura desgastada' },
    minimalist: { name: 'Minimalista', preview: '▫️', description: 'Líneas limpias simples' },
    baroque: { name: 'Barroco', preview: '', description: 'Ornamentación clásica' }
  };

  const drawFrame = (ctx, canvas) => {
    if (selectedFrame === 'none') return;
    
    const implementations = {
      classic: () => {
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 8;
        ctx.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
      },
      modern: () => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 12;
        ctx.strokeRect(6, 6, canvas.width - 12, canvas.height - 12);
      },
      vintage: () => {
        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 15;
        ctx.strokeRect(7, 7, canvas.width - 14, canvas.height - 14);
        ctx.strokeStyle = '#DEB887';
        ctx.lineWidth = 3;
        ctx.strokeRect(15, 15, canvas.width - 30, canvas.height - 30);
      },
      neon: () => {
        ctx.shadowColor = '#00FFFF';
        ctx.shadowBlur = 20;
        ctx.strokeStyle = '#00FFFF';
        ctx.lineWidth = 6;
        ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
        ctx.shadowColor = '#FF00FF';
        ctx.strokeStyle = '#FF00FF';
        ctx.lineWidth = 4;
        ctx.strokeRect(12, 12, canvas.width - 24, canvas.height - 24);
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
      },
      polaroid: () => {
        // Marco blanco grueso como Polaroid
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 20, 20, canvas.width - 40, canvas.height - 80);
        ctx.fillStyle = '#F0F0F0';
        ctx.fillRect(20, canvas.height - 80, canvas.width - 40, 60);
      },
      film: () => {
        // Perforaciones de película
        ctx.fillStyle = '#000000';
        for (let i = 0; i < canvas.width; i += 20) {
          ctx.fillRect(i, 0, 10, 15);
          ctx.fillRect(i, canvas.height - 15, 10, 15);
        }
      },
      gold_ornate: () => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        gradient.addColorStop(0, '#FFD700');
        gradient.addColorStop(0.5, '#FFA500');
        gradient.addColorStop(1, '#FFD700');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 20;
        ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
        // Decoraciones en las esquinas
        ctx.fillStyle = '#FFD700';
        const cornerSize = 30;
        [[10, 10], [canvas.width - 40, 10], [10, canvas.height - 40], [canvas.width - 40, canvas.height - 40]].forEach(([x, y]) => {
          ctx.fillRect(x, y, cornerSize, cornerSize);
        });
      },
      silver_tech: () => {
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#C0C0C0');
        gradient.addColorStop(0.5, '#808080');
        gradient.addColorStop(1, '#C0C0C0');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 16;
        ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
      },
      rainbow_gradient: () => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        gradient.addColorStop(0, '#FF0000');
        gradient.addColorStop(1/6, '#FF8000');
        gradient.addColorStop(2/6, '#FFFF00');
        gradient.addColorStop(3/6, '#00FF00');
        gradient.addColorStop(4/6, '#0080FF');
        gradient.addColorStop(5/6, '#8000FF');
        gradient.addColorStop(1, '#FF0080');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 12;
        ctx.strokeRect(6, 6, canvas.width - 12, canvas.height - 12);
      },
      diamond: () => {
        ctx.strokeStyle = '#E6E6FA';
        ctx.lineWidth = 8;
        ctx.shadowColor = '#DDA0DD';
        ctx.shadowBlur = 15;
        // Marco con efecto cristal
        ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
        ctx.strokeStyle = '#DDA0DD';
        ctx.lineWidth = 2;
        ctx.strokeRect(12, 12, canvas.width - 24, canvas.height - 24);
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
      },
      fire: () => {
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#FF4500');
        gradient.addColorStop(0.5, '#FF0000');
        gradient.addColorStop(1, '#8B0000');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 14;
        ctx.shadowColor = '#FF4500';
        ctx.shadowBlur = 20;
        ctx.strokeRect(7, 7, canvas.width - 14, canvas.height - 14);
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
      },
      ice: () => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#E0FFFF');
        gradient.addColorStop(0.5, '#B0E0E6');
        gradient.addColorStop(1, '#87CEEB');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 12;
        ctx.shadowColor = '#87CEEB';
        ctx.shadowBlur = 10;
        ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
      },
      nature: () => {
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#8FBC8F');
        gradient.addColorStop(0.5, '#556B2F');
        gradient.addColorStop(1, '#228B22');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 16;
        ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
      },
      galaxy: () => {
        const gradient = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 0, canvas.width/2, canvas.height/2, canvas.width/2);
        gradient.addColorStop(0, '#4B0082');
        gradient.addColorStop(0.5, '#191970');
        gradient.addColorStop(1, '#000000');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 18;
        ctx.strokeRect(9, 9, canvas.width - 18, canvas.height - 18);
      },
      geometric: () => {
        ctx.strokeStyle = '#4169E1';
        ctx.lineWidth = 3;
        const size = 20;
        // Patrón geométrico en los bordes
        for (let i = 0; i < canvas.width; i += size) {
          for (let j = 0; j < canvas.height; j += size) {
            if (i < size || i > canvas.width - size*2 || j < size || j > canvas.height - size*2) {
              ctx.strokeRect(i, j, size, size);
            }
          }
        }
      },
      watercolor: () => {
        // Efecto acuarela con múltiples capas
        const colors = ['#FF69B4', '#87CEEB', '#98FB98', '#DDA0DD', '#F0E68C'];
        colors.forEach((color, index) => {
          ctx.strokeStyle = color;
          ctx.lineWidth = 8 - index;
          const offset = index * 2;
          ctx.strokeRect(8 + offset, 8 + offset, canvas.width - 16 - offset*2, canvas.height - 16 - offset*2);
        });
      },
      grunge: () => {
        ctx.strokeStyle = '#696969';
        ctx.lineWidth = 14;
        ctx.strokeRect(7, 7, canvas.width - 14, canvas.height - 14);
        // Efectos de desgaste
        ctx.strokeStyle = '#2F2F2F';
        ctx.lineWidth = 2;
        for (let i = 0; i < 20; i++) {
          ctx.strokeRect(
            Math.random() * canvas.width,
            Math.random() * 20,
            Math.random() * 30 + 10,
            5
          );
        }
      },
      minimalist: () => {
        ctx.strokeStyle = '#E5E5E5';
        ctx.lineWidth = 2;
        ctx.strokeRect(15, 15, canvas.width - 30, canvas.height - 30);
      },
      baroque: () => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#DAA520');
        gradient.addColorStop(0.5, '#B8860B');
        gradient.addColorStop(1, '#DAA520');
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 24;
        ctx.strokeRect(12, 12, canvas.width - 24, canvas.height - 24);
        // Ornamentación barroca
        ctx.fillStyle = '#DAA520';
        const ornamentSize = 40;
        [[12, 12], [canvas.width - 52, 12], [12, canvas.height - 52], [canvas.width - 52, canvas.height - 52]].forEach(([x, y]) => {
          ctx.fillRect(x, y, ornamentSize, ornamentSize);
        });
      }
    };
    
    implementations[selectedFrame]?.();
  };

  const getTextBounds = (textEl, ctx) => {
    ctx.font = `${textEl.fontWeight} ${textEl.fontSize}px ${textEl.fontFamily}`;
    ctx.textAlign = textEl.textAlign;
    
    const metrics = ctx.measureText(textEl.text);
    const width = metrics.width;
    const height = textEl.fontSize;
    
    let x = textEl.x;
    if (textEl.textAlign === 'center') x -= width / 2;
    else if (textEl.textAlign === 'right') x -= width;
    
    return {
      x: x,
      y: textEl.y - height,
      width: width,
      height: height * 1.2
    };
  };

  const drawText = (ctx, textEl) => {
    ctx.font = `${textEl.fontWeight} ${textEl.fontSize}px ${textEl.fontFamily}`;
    ctx.fillStyle = textEl.color;
    
    const x = textEl.x || canvasRef.current.width / 2;
    const y = textEl.y || canvasRef.current.height / 2;
    const lines = textEl.lines || [textEl.text];
    const lineHeight = textEl.fontSize * 1.2;
    
    // Dibujar borde de contenedor y handles si está seleccionado
    if (selectedTextId === textEl.id) {
      const containerWidth = textEl.width || 200;
      const containerHeight = textEl.height || (lines.length * lineHeight);
      const containerX = x - containerWidth / 2;
      const containerY = y - containerHeight / 2;
      
      // Borde del contenedor
      ctx.strokeStyle = '#3B82F6';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(containerX, containerY, containerWidth, containerHeight);
      ctx.setLineDash([]);
      
      // Dibujar handles de redimensionado
      const handleSize = 8;
      ctx.fillStyle = '#3B82F6';
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 1;
      
      const handles = [
        { id: 'nw', x: containerX - handleSize/2, y: containerY - handleSize/2 },
        { id: 'ne', x: containerX + containerWidth - handleSize/2, y: containerY - handleSize/2 },
        { id: 'sw', x: containerX - handleSize/2, y: containerY + containerHeight - handleSize/2 },
        { id: 'se', x: containerX + containerWidth - handleSize/2, y: containerY + containerHeight - handleSize/2 }
      ];
      
      handles.forEach(handle => {
        ctx.fillRect(handle.x, handle.y, handleSize, handleSize);
        ctx.strokeRect(handle.x, handle.y, handleSize, handleSize);
      });
    }
    
    // Sombra
    if (textEl.shadow) {
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      ctx.shadowBlur = 4;
    }
    
    // Dibujar cada línea de texto con wrapping optimizado
    const containerWidth = textEl.width || 200;
    const maxWidth = containerWidth - 20; // Padding interno
    
    let renderedLines = [];
    
    // Word wrapping optimizado - usar cache si el texto no ha cambiado
    if (textEl.cachedLines && textEl.cachedWidth === containerWidth) {
      renderedLines = textEl.cachedLines;
    } else {
      // Procesar cada línea para word wrapping
      ctx.font = `${textEl.fontWeight} ${textEl.fontSize}px ${textEl.fontFamily}`;
      
      lines.forEach(line => {
        if (!line.trim()) {
          renderedLines.push('');
          return;
        }
        
        // Estimación rápida: si la línea es corta, no hacer wrapping
        if (line.length < 20) {
          const metrics = ctx.measureText(line);
          if (metrics.width <= maxWidth) {
            renderedLines.push(line);
            return;
          }
        }
        
        const words = line.split(' ');
        let currentLine = '';
        
        for (let i = 0; i < words.length; i++) {
          const testLine = currentLine + (currentLine ? ' ' : '') + words[i];
          const metrics = ctx.measureText(testLine);
          
          if (metrics.width > maxWidth && currentLine) {
            renderedLines.push(currentLine);
            currentLine = words[i];
          } else {
            currentLine = testLine;
          }
        }
        
        if (currentLine) {
          renderedLines.push(currentLine);
        }
      });
      
      // Cache del resultado para renders futuros
      setTimeout(() => {
        setTextElements(prev => prev.map(t => 
          t.id === textEl.id 
            ? { ...t, cachedLines: renderedLines, cachedWidth: containerWidth } 
            : t
        ));
      }, 0);
    }
    
    // Actualizar altura del contenedor si es necesario (con throttling para evitar lag)
    const newHeight = renderedLines.length * lineHeight;
    if (Math.abs(newHeight - textEl.height) > 5) { // Solo actualizar si hay diferencia significativa
      setTimeout(() => {
        setTextElements(prev => prev.map(t => 
          t.id === textEl.id ? { ...t, height: newHeight } : t
        ));
      }, 0); // Defer para evitar actualizaciones durante el render
    }
    
    // Dibujar cada línea renderizada
    const finalStartY = y - (renderedLines.length - 1) * lineHeight / 2;
    renderedLines.forEach((line, index) => {
      const lineY = finalStartY + (index * lineHeight);
      
      // Contorno
      if (textEl.outline) {
        ctx.strokeStyle = textEl.outline === true ? '#000000' : textEl.outline;
        ctx.lineWidth = 3;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.strokeText(line, x, lineY);
      }
      
      // Texto
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(line, x, lineY);
    });
    
    // Resetear efectos
    ctx.shadowColor = 'transparent';
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    ctx.shadowBlur = 0;
  };

  const drawDecorativeElement = (ctx, element) => {
    if (element.type === 'emoji') {
      const size = element.size || 40;
      ctx.save();
      ctx.font = `${size}px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", Arial, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Dibujar emoji centrado correctamente
      ctx.fillText(element.content, element.x, element.y);
      ctx.restore();
      
      // Re-aplicar configuración para selección
      const halfSize = size / 2;
      
      // Dibujar borde de selección si está seleccionado
      if (selectedElementId === element.id) {
        drawSelectionBorder(ctx, element.x - halfSize, element.y - halfSize, size, size, '#3B82F6');
      }
    }
    
    // 🎨 Renderizar Giphy Stickers
    else if (element.type === 'sticker' && element.loaded && element.image) {
      const halfWidth = element.width / 2;
      const halfHeight = element.height / 2;
      
      // Dibujar sticker centrado
      ctx.drawImage(
        element.image, 
        element.x - halfWidth, 
        element.y - halfHeight, 
        element.width, 
        element.height
      );
      
      // Dibujar borde de selección si está seleccionado
      if (selectedElementId === element.id) {
        drawSelectionBorder(ctx, element.x - halfWidth, element.y - halfHeight, element.width, element.height, '#10B981');
      }
    }
  };

  // Nueva función para dibujar formas geométricas
  const drawShape = (ctx, shape) => {
    ctx.save();
    
    // Aplicar estilo
    ctx.fillStyle = shape.fillColor || '#FF6B6B';
    ctx.strokeStyle = shape.strokeColor || '#000000';
    ctx.lineWidth = shape.strokeWidth || 2;
    
    if (shape.type === 'rectangle') {
      if (shape.filled) {
        ctx.fillRect(shape.x, shape.y, shape.width, shape.height);
      }
      ctx.strokeRect(shape.x, shape.y, shape.width, shape.height);
    }
    
    else if (shape.type === 'circle') {
      ctx.beginPath();
      ctx.arc(shape.x + shape.width/2, shape.y + shape.height/2, Math.min(shape.width, shape.height)/2, 0, 2 * Math.PI);
      if (shape.filled) {
        ctx.fill();
      }
      ctx.stroke();
    }
    
    else if (shape.type === 'triangle') {
      ctx.beginPath();
      ctx.moveTo(shape.x + shape.width/2, shape.y);
      ctx.lineTo(shape.x, shape.y + shape.height);
      ctx.lineTo(shape.x + shape.width, shape.y + shape.height);
      ctx.closePath();
      if (shape.filled) {
        ctx.fill();
      }
      ctx.stroke();
    }
    
    ctx.restore();
    
    // Dibujar borde de selección si está seleccionado
    if (selectedShape === shape.id) {
      drawSelectionBorder(ctx, shape.x, shape.y, shape.width, shape.height, '#F59E0B');
    }
  };

  // Nueva función para dibujar líneas y flechas
  const drawLine = (ctx, line) => {
    ctx.save();
    ctx.strokeStyle = line.color || '#000000';
    ctx.lineWidth = line.width || 2;
    
    ctx.beginPath();
    ctx.moveTo(line.startX, line.startY);
    ctx.lineTo(line.endX, line.endY);
    ctx.stroke();
    
    // Dibujar flecha si es necesario
    if (line.type === 'arrow') {
      const angle = Math.atan2(line.endY - line.startY, line.endX - line.startX);
      const arrowLength = 15;
      const arrowAngle = Math.PI / 6;
      
      ctx.beginPath();
      ctx.moveTo(line.endX, line.endY);
      ctx.lineTo(
        line.endX - arrowLength * Math.cos(angle - arrowAngle),
        line.endY - arrowLength * Math.sin(angle - arrowAngle)
      );
      ctx.moveTo(line.endX, line.endY);
      ctx.lineTo(
        line.endX - arrowLength * Math.cos(angle + arrowAngle),
        line.endY - arrowLength * Math.sin(angle + arrowAngle)
      );
      ctx.stroke();
    }
    
    ctx.restore();
    
    // Dibujar puntos de control si está seleccionado
    if (selectedLine === line.id) {
      drawLineControls(ctx, line);
    }
  };

  // Nueva función para dibujar fondos de texto
  const drawTextBackground = (ctx, bg) => {
    ctx.save();
    ctx.fillStyle = bg.color || 'rgba(0, 0, 0, 0.5)';
    
    if (bg.shape === 'rectangle') {
      ctx.fillRect(bg.x, bg.y, bg.width, bg.height);
    } else if (bg.shape === 'rounded') {
      const radius = bg.radius || 10;
      ctx.beginPath();
      ctx.roundRect(bg.x, bg.y, bg.width, bg.height, radius);
      ctx.fill();
    } else if (bg.shape === 'circle') {
      ctx.beginPath();
      ctx.arc(bg.x + bg.width/2, bg.y + bg.height/2, Math.min(bg.width, bg.height)/2, 0, 2 * Math.PI);
      ctx.fill();
    }
    
    ctx.restore();
    
    // Dibujar borde de selección si está seleccionado
    if (selectedElementId === bg.id) {
      drawSelectionBorder(ctx, bg.x, bg.y, bg.width, bg.height, '#8B5CF6');
    }
  };

  // Nueva función para dibujar área de recorte
  const drawCropArea = (ctx, crop) => {
    const canvas = ctx.canvas;
    
    // Overlay oscuro
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Área clara de recorte
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillRect(crop.x, crop.y, crop.width, crop.height);
    
    ctx.globalCompositeOperation = 'source-over';
    
    // Borde del área de recorte
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 4]);
    ctx.strokeRect(crop.x, crop.y, crop.width, crop.height);
    ctx.setLineDash([]);
    
    // Manijas de redimensionamiento
    drawResizeHandles(ctx, crop.x, crop.y, crop.width, crop.height, '#ffffff');
    
    ctx.restore();
  };

  // Función universal para dibujar bordes de selección con manijas
  const drawSelectionBorder = (ctx, x, y, width, height, color = '#3B82F6') => {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 4]);
    ctx.strokeRect(x - 4, y - 4, width + 8, height + 8);
    ctx.setLineDash([]);
    
    // Manijas de redimensionamiento
    drawResizeHandles(ctx, x, y, width, height, color);
    
    ctx.restore();
  };

  // Función para dibujar manijas de redimensionamiento
  const drawResizeHandles = (ctx, x, y, width, height, color = '#3B82F6') => {
    const handleSize = 8;
    ctx.fillStyle = color;
    
    const handles = [
      { x: x - handleSize/2, y: y - handleSize/2 }, // Top-left
      { x: x + width/2 - handleSize/2, y: y - handleSize/2 }, // Top-center
      { x: x + width - handleSize/2, y: y - handleSize/2 }, // Top-right
      { x: x + width - handleSize/2, y: y + height/2 - handleSize/2 }, // Right-center
      { x: x + width - handleSize/2, y: y + height - handleSize/2 }, // Bottom-right
      { x: x + width/2 - handleSize/2, y: y + height - handleSize/2 }, // Bottom-center
      { x: x - handleSize/2, y: y + height - handleSize/2 }, // Bottom-left
      { x: x - handleSize/2, y: y + height/2 - handleSize/2 } // Left-center
    ];
    
    handles.forEach(handle => {
      ctx.fillRect(handle.x, handle.y, handleSize, handleSize);
    });
  };

  // Función para dibujar controles de línea
  const drawLineControls = (ctx, line) => {
    const controlSize = 8;
    ctx.fillStyle = '#F59E0B';
    
    // Punto de inicio
    ctx.fillRect(line.startX - controlSize/2, line.startY - controlSize/2, controlSize, controlSize);
    // Punto final
    ctx.fillRect(line.endX - controlSize/2, line.endY - controlSize/2, controlSize, controlSize);
    // Punto medio
    const midX = (line.startX + line.endX) / 2;
    const midY = (line.startY + line.endY) / 2;
    ctx.fillRect(midX - controlSize/2, midY - controlSize/2, controlSize, controlSize);
  };

  // Funciones para drag & drop de texto
  const getCanvasCoordinates = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    // Manejar tanto mouse como touch events
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;
    
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  };

  const getElementAtPosition = (x, y) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Verificar área de recorte si está activa (máxima prioridad)
    if (cropMode && cropArea) {
      if (x >= cropArea.x && x <= cropArea.x + cropArea.width &&
          y >= cropArea.y && y <= cropArea.y + cropArea.height) {
        return { ...cropArea, elementType: 'crop' };
      }
    }
    
    // Verificar líneas y flechas (alta prioridad)
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      const distance = getDistanceToLine(x, y, line.startX, line.startY, line.endX, line.endY);
      if (distance <= (line.width || 2) + 5) { // Tolerancia de 5px
        return { ...line, elementType: 'line' };
      }
    }
    
    // Verificar formas geométricas
    for (let i = shapes.length - 1; i >= 0; i--) {
      const shape = shapes[i];
      
      if (shape.type === 'rectangle') {
        if (x >= shape.x && x <= shape.x + shape.width &&
            y >= shape.y && y <= shape.y + shape.height) {
          return { ...shape, elementType: 'shape' };
        }
      }
      else if (shape.type === 'circle') {
        const centerX = shape.x + shape.width / 2;
        const centerY = shape.y + shape.height / 2;
        const radius = Math.min(shape.width, shape.height) / 2;
        const distance = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
        if (distance <= radius) {
          return { ...shape, elementType: 'shape' };
        }
      }
      else if (shape.type === 'triangle') {
        // Verificación simple de triángulo usando área
        if (isPointInTriangle(x, y, 
            shape.x + shape.width/2, shape.y,
            shape.x, shape.y + shape.height,
            shape.x + shape.width, shape.y + shape.height)) {
          return { ...shape, elementType: 'shape' };
        }
      }
    }
    
    // Verificar fondos de texto
    for (let i = textBackgrounds.length - 1; i >= 0; i--) {
      const bg = textBackgrounds[i];
      if (x >= bg.x && x <= bg.x + bg.width &&
          y >= bg.y && y <= bg.y + bg.height) {
        return { ...bg, elementType: 'textBackground' };
      }
    }
    
    // Verificar elementos decorativos (emojis y stickers)
    for (let i = decorativeElements.length - 1; i >= 0; i--) {
      const element = decorativeElements[i];
      
      if (element.type === 'emoji') {
        const halfSize = element.size / 2;
        const emojiX = element.x - halfSize;
        const emojiY = element.y - halfSize;
        
        if (x >= emojiX && x <= emojiX + element.size &&
            y >= emojiY && y <= emojiY + element.size) {
          return { ...element, elementType: 'decorative' };
        }
      }
      
      else if (element.type === 'sticker' && element.loaded) {
        const halfWidth = element.width / 2;
        const halfHeight = element.height / 2;
        const stickerX = element.x - halfWidth;
        const stickerY = element.y - halfHeight;
        
        if (x >= stickerX && x <= stickerX + element.width &&
            y >= stickerY && y <= stickerY + element.height) {
          return { ...element, elementType: 'decorative' };
        }
      }
    }
    
    // Verificar elementos de texto (menor prioridad)
    for (let i = textElements.length - 1; i >= 0; i--) {
      const textEl = textElements[i];
      const bounds = getTextBounds(textEl, ctx);
      
      if (x >= bounds.x && x <= bounds.x + bounds.width &&
          y >= bounds.y && y <= bounds.y + bounds.height) {
        return { ...textEl, elementType: 'text' };
      }
    }
    
    return null;
  };

  // Función auxiliar para calcular distancia a una línea
  const getDistanceToLine = (px, py, x1, y1, x2, y2) => {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;
    
    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;
    if (lenSq !== 0) {
      param = dot / lenSq;
    }
    
    let xx, yy;
    if (param < 0) {
      xx = x1;
      yy = y1;
    } else if (param > 1) {
      xx = x2;
      yy = y2;
    } else {
      xx = x1 + param * C;
      yy = y1 + param * D;
    }
    
    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
  };

  // Función auxiliar para verificar si un punto está dentro de un triángulo
  const isPointInTriangle = (px, py, x1, y1, x2, y2, x3, y3) => {
    const denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
    const a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom;
    const b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom;
    const c = 1 - a - b;
    return a >= 0 && b >= 0 && c >= 0;
  };

  // Función para detectar si el click está en un handle de redimensionado
  const getResizeHandle = (x, y, textEl) => {
    if (!textEl || selectedTextId !== textEl.id) return null;
    
    const containerWidth = textEl.width || 200;
    const containerHeight = textEl.height || (textEl.lines?.length || 1) * (textEl.fontSize * 1.2);
    const containerX = textEl.x - containerWidth / 2;
    const containerY = textEl.y - containerHeight / 2;
    const handleSize = 8;
    const tolerance = 4;
    
    const handles = [
      { id: 'nw', x: containerX - handleSize/2, y: containerY - handleSize/2 },
      { id: 'ne', x: containerX + containerWidth - handleSize/2, y: containerY - handleSize/2 },
      { id: 'sw', x: containerX - handleSize/2, y: containerY + containerHeight - handleSize/2 },
      { id: 'se', x: containerX + containerWidth - handleSize/2, y: containerY + containerHeight - handleSize/2 }
    ];
    
    for (const handle of handles) {
      if (x >= handle.x - tolerance && x <= handle.x + handleSize + tolerance &&
          y >= handle.y - tolerance && y <= handle.y + handleSize + tolerance) {
        return handle.id;
      }
    }
    return null;
  };

  const handleCanvasMouseDown = (event) => {
    event.preventDefault();
    const coords = getCanvasCoordinates(event);
    
    // Primero verificar si es un handle de resize para texto seleccionado
    if (selectedTextId) {
      const textEl = textElements.find(t => t.id === selectedTextId);
      const handle = getResizeHandle(coords.x, coords.y, textEl);
      
      if (handle) {
        setIsResizing(true);
        setResizeHandle(handle);
        setResizeStartData({
          startX: coords.x,
          startY: coords.y,
          originalWidth: textEl.width || 200,
          originalHeight: textEl.height || (textEl.lines?.length || 1) * (textEl.fontSize * 1.2),
          originalX: textEl.x,
          originalY: textEl.y
        });
        return;
      }
    }
    
    const element = getElementAtPosition(coords.x, coords.y);
    
    // Verificar si se presionó Ctrl para selección múltiple
    const isCtrlPressed = event.ctrlKey || event.metaKey;
    
    if (element) {
      // Limpiar todas las selecciones primero
      setSelectedTextId(null);
      setSelectedElementId(null);
      setSelectedShape(null);
      setSelectedLine(null);
      setSelectedLayer(null);
      
      // Seleccionar elemento específico
      if (element.elementType === 'text') {
        setSelectedTextId(element.id);
      } else if (element.elementType === 'decorative' || element.elementType === 'textBackground') {
        setSelectedElementId(element.id);
      } else if (element.elementType === 'shape') {
        setSelectedShape(element.id);
      } else if (element.elementType === 'line') {
        setSelectedLine(element.id);
      }
      
      setSelectedElementType(element.elementType);
      setIsDragging(true);
      
      // Calcular offset basado en el tipo de elemento
      let offsetX, offsetY;
      if (element.elementType === 'line') {
        // Para líneas, usar el punto más cercano
        const distToStart = Math.sqrt((coords.x - element.startX)**2 + (coords.y - element.startY)**2);
        const distToEnd = Math.sqrt((coords.x - element.endX)**2 + (coords.y - element.endY)**2);
        if (distToStart < distToEnd) {
          offsetX = coords.x - element.startX;
          offsetY = coords.y - element.startY;
        } else {
          offsetX = coords.x - element.endX;
          offsetY = coords.y - element.endY;
        }
      } else {
        offsetX = coords.x - element.x;
        offsetY = coords.y - element.y;
      }
      
      setDragOffset({ x: offsetX, y: offsetY });
      
      // Manejar selección múltiple si Ctrl está presionado
      if (isCtrlPressed && !multiSelect) {
        setMultiSelect(true);
        setSelectedElements([element.id]);
      } else if (isCtrlPressed && multiSelect) {
        setSelectedElements(prev => 
          prev.includes(element.id) 
            ? prev.filter(id => id !== element.id)
            : [...prev, element.id]
        );
      }
    } else {
      // Clic en área vacía
      setSelectedTextId(null);
      setSelectedElementId(null);
      setSelectedShape(null);
      setSelectedLine(null);
      setSelectedLayer(null);
      setSelectedElementType(null);
      setMultiSelect(false);
      setSelectedElements([]);
    }
  };

  const handleCanvasMouseMove = (event) => {
    event.preventDefault();
    const coords = getCanvasCoordinates(event);
    
    // Manejar redimensionado de texto
    if (isResizing && resizeHandle && resizeStartData && selectedTextId) {
      const deltaX = coords.x - resizeStartData.startX;
      const deltaY = coords.y - resizeStartData.startY;
      
      let newWidth = resizeStartData.originalWidth;
      let newHeight = resizeStartData.originalHeight;
      let newX = resizeStartData.originalX;
      let newY = resizeStartData.originalY;
      
      // Calcular nuevas dimensiones basadas en el handle
      switch (resizeHandle) {
        case 'se': // Esquina inferior derecha
          newWidth = Math.max(100, resizeStartData.originalWidth + deltaX);
          newHeight = Math.max(30, resizeStartData.originalHeight + deltaY);
          break;
        case 'sw': // Esquina inferior izquierda
          newWidth = Math.max(100, resizeStartData.originalWidth - deltaX);
          newHeight = Math.max(30, resizeStartData.originalHeight + deltaY);
          newX = resizeStartData.originalX + deltaX / 2;
          break;
        case 'ne': // Esquina superior derecha
          newWidth = Math.max(100, resizeStartData.originalWidth + deltaX);
          newHeight = Math.max(30, resizeStartData.originalHeight - deltaY);
          newY = resizeStartData.originalY + deltaY / 2;
          break;
        case 'nw': // Esquina superior izquierda
          newWidth = Math.max(100, resizeStartData.originalWidth - deltaX);
          newHeight = Math.max(30, resizeStartData.originalHeight - deltaY);
          newX = resizeStartData.originalX + deltaX / 2;
          newY = resizeStartData.originalY + deltaY / 2;
          break;
      }
      
      // Actualizar elemento de texto
      setTextElements(prev => prev.map(t => 
        t.id === selectedTextId 
          ? { ...t, width: newWidth, height: newHeight, x: newX, y: newY }
          : t
      ));
      return;
    }
    
    if (isDragging) {
      const newX = coords.x - dragOffset.x;
      const newY = coords.y - dragOffset.y;
      const canvas = canvasRef.current;
      
      // Manejar arrastre de texto (simplificado para mejor fluidez)
      if (selectedElementType === 'text' && selectedTextId) {
        const textEl = textElements.find(t => t.id === selectedTextId);
        
        if (textEl) {
          // Usar dimensiones del contenedor para límites más simples
          const containerWidth = textEl.width || 200;
          const containerHeight = textEl.height || (textEl.fontSize * 1.2);
          
          const minX = containerWidth / 2 + 10;
          const maxX = canvas.width - containerWidth / 2 - 10;
          const minY = containerHeight / 2 + 10;
          const maxY = canvas.height - containerHeight / 2 - 10;
          
          const constrainedX = Math.max(minX, Math.min(maxX, newX));
          const constrainedY = Math.max(minY, Math.min(maxY, newY));
          
          setTextElements(prev => prev.map(t => 
            t.id === selectedTextId 
              ? { ...t, x: constrainedX, y: constrainedY }
              : t
          ));
        }
      }
      
      // Manejar arrastre de elementos decorativos (emojis y stickers)
      else if (selectedElementType === 'decorative' && selectedElementId) {
        const element = decorativeElements.find(el => el.id === selectedElementId);
        
        if (element) {
          let halfWidth, halfHeight;
          
          if (element.type === 'emoji') {
            const halfSize = element.size / 2;
            halfWidth = halfSize;
            halfHeight = halfSize;
          } else if (element.type === 'sticker') {
            halfWidth = element.width / 2;
            halfHeight = element.height / 2;
          }
          
          const minX = halfWidth;
          const maxX = canvas.width - halfWidth;
          const minY = halfHeight;
          const maxY = canvas.height - halfHeight;
          
          const constrainedX = Math.max(minX, Math.min(maxX, newX));
          const constrainedY = Math.max(minY, Math.min(maxY, newY));
          
          setDecorativeElements(prev => prev.map(el => 
            el.id === selectedElementId 
              ? { ...el, x: constrainedX, y: constrainedY }
              : el
          ));
        }
      }
      
      // Manejar arrastre de formas geométricas
      else if (selectedElementType === 'shape' && selectedShape) {
        const shape = shapes.find(s => s.id === selectedShape);
        
        if (shape) {
          const minX = 0;
          const maxX = canvas.width - shape.width;
          const minY = 0;
          const maxY = canvas.height - shape.height;
          
          const constrainedX = Math.max(minX, Math.min(maxX, newX));
          const constrainedY = Math.max(minY, Math.min(maxY, newY));
          
          setShapes(prev => prev.map(s => 
            s.id === selectedShape 
              ? { ...s, x: constrainedX, y: constrainedY }
              : s
          ));
        }
      }
      
      // Manejar arrastre de líneas
      else if (selectedElementType === 'line' && selectedLine) {
        const line = lines.find(l => l.id === selectedLine);
        
        if (line) {
          const deltaX = newX - line.startX;
          const deltaY = newY - line.startY;
          
          // Mover toda la línea manteniendo la forma
          const newStartX = Math.max(0, Math.min(canvas.width, line.startX + deltaX));
          const newStartY = Math.max(0, Math.min(canvas.height, line.startY + deltaY));
          const newEndX = Math.max(0, Math.min(canvas.width, line.endX + deltaX));
          const newEndY = Math.max(0, Math.min(canvas.height, line.endY + deltaY));
          
          setLines(prev => prev.map(l => 
            l.id === selectedLine 
              ? { ...l, startX: newStartX, startY: newStartY, endX: newEndX, endY: newEndY }
              : l
          ));
        }
      }
      
      // Manejar arrastre de fondos de texto
      else if (selectedElementType === 'textBackground' && selectedElementId) {
        const bg = textBackgrounds.find(b => b.id === selectedElementId);
        
        if (bg) {
          const minX = 0;
          const maxX = canvas.width - bg.width;
          const minY = 0;
          const maxY = canvas.height - bg.height;
          
          const constrainedX = Math.max(minX, Math.min(maxX, newX));
          const constrainedY = Math.max(minY, Math.min(maxY, newY));
          
          setTextBackgrounds(prev => prev.map(b => 
            b.id === selectedElementId 
              ? { ...b, x: constrainedX, y: constrainedY }
              : b
          ));
        }
      }
      
      // Manejar arrastre del área de recorte
      else if (selectedElementType === 'crop' && cropArea) {
        const minX = 0;
        const maxX = canvas.width - cropArea.width;
        const minY = 0;
        const maxY = canvas.height - cropArea.height;
        
        const constrainedX = Math.max(minX, Math.min(maxX, newX));
        const constrainedY = Math.max(minY, Math.min(maxY, newY));
        
        setCropArea(prev => ({
          ...prev,
          x: constrainedX,
          y: constrainedY
        }));
      }
    } else {
      // Cambiar cursor hover basado en el elemento
      const element = getElementAtPosition(coords.x, coords.y);
      
      // Reset all hover states
      setHoveredTextId(null);
      setHoveredElementId(null);
      
      if (element) {
        if (element.elementType === 'text') {
          setHoveredTextId(element.id);
        } else if (['decorative', 'shape', 'line', 'textBackground', 'crop'].includes(element.elementType)) {
          setHoveredElementId(element.id);
        }
      }
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
    setDragOffset({ x: 0, y: 0 });
    
    // Reset resize state
    if (isResizing) {
      setIsResizing(false);
      setResizeHandle(null);
      setResizeStartData(null);
    }
  };

  const addTextElement = () => {
    if (!textInput.trim()) return;
    
    // Separar el texto en líneas para soporte multilínea
    const lines = textInput.split('\n');
    
    const newTextEl = {
      id: Date.now(),
      text: textInput,
      lines: lines, // Nuevo: líneas separadas
      x: canvasRef.current.width / 2,
      y: canvasRef.current.height / 2,
      width: 200, // Nuevo: ancho del contenedor
      height: lines.length * (textStyle.fontSize * 1.2), // Nuevo: altura basada en líneas
      minWidth: 100, // Nuevo: ancho mínimo
      minHeight: textStyle.fontSize * 1.2, // Nuevo: altura mínima
      ...textStyle
    };
    
    setTextElements([...textElements, newTextEl]);
    setTextInput('');
  };

  const addEmoji = (emoji) => {
    const newElement = {
      id: Date.now(),
      type: 'emoji',
      content: emoji,
      x: canvasRef.current.width / 2,
      y: canvasRef.current.height / 2,
      size: 40
    };
    
    setDecorativeElements([...decorativeElements, newElement]);
  };

  // 🎯 Función para buscar stickers de Giphy con DEBUG
  const searchGiphyStickers = async (query = '', category = 'trending', limit = 20) => {
    console.log('🔍 Iniciando búsqueda Giphy:', { query, category, limit });
    
    setStickerLoading(true);
    setIsLoadingStickers(true);
    
    try {
      // Construir URL basada en categoría y query
      let endpoint;
      if (category === 'trending' && !query) {
        endpoint = `${GIPHY_BASE_URL}/trending?api_key=${GIPHY_API_KEY}&limit=${limit}&rating=g`;
      } else {
        const searchQuery = query || category;
        endpoint = `${GIPHY_BASE_URL}/search?api_key=${GIPHY_API_KEY}&q=${searchQuery}&limit=${limit}&rating=g`;
      }
      
      console.log('🌐 URL Giphy:', endpoint);
      
      const response = await fetch(endpoint);
      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📋 Giphy data:', data);
      
      if (data.data && Array.isArray(data.data)) {
        console.log('✅ Stickers encontrados:', data.data.length);
        
        const stickers = data.data.map(sticker => ({
          id: sticker.id,
          url: sticker.images.fixed_height_small?.url || sticker.images.original?.url,
          preview: sticker.images.preview_gif?.url || sticker.images.fixed_width_small?.url,
          title: sticker.title || 'Sticker',
          width: parseInt(sticker.images.fixed_height_small?.width || 100),
          height: parseInt(sticker.images.fixed_height_small?.height || 100),
          images: sticker.images // Guardar todas las imágenes disponibles
        }));
        
        console.log('🎨 Stickers procesados:', stickers.slice(0, 3)); // Solo mostrar primeros 3
        
        setCurrentStickers(stickers);
        setGiphyStickers(stickers);
      } else {
        console.log('❌ No data in response');
        setCurrentStickers([]);
        setGiphyStickers([]);
      }
    } catch (error) {
      console.error('❌ Error Giphy:', error);
      setCurrentStickers([]);
      setGiphyStickers([]);
    } finally {
      setStickerLoading(false);
      setIsLoadingStickers(false);
      console.log('🔄 Loading states reset');
    }
  };

  // 🎨 Función para agregar sticker al canvas
  const addSticker = async (stickerData) => {
    const newElement = {
      id: Date.now(),
      type: 'sticker',
      url: stickerData.url,
      title: stickerData.title,
      x: canvasRef.current.width / 2,
      y: canvasRef.current.height / 2,
      width: Math.min(stickerData.width, 100), // Tamaño máximo inicial
      height: Math.min(stickerData.height, 100),
      originalWidth: stickerData.width,
      originalHeight: stickerData.height,
      loaded: false,
      image: null
    };
    
    // Cargar la imagen del sticker
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = () => {
      newElement.image = img;
      newElement.loaded = true;
      // Actualizar el elemento en el array
      setDecorativeElements(prev => 
        prev.map(el => el.id === newElement.id ? newElement : el)
      );
    };
    img.src = stickerData.url;
    
    setDecorativeElements([...decorativeElements, newElement]);
  };

  // Funciones para agregar formas geométricas
  const addShape = (shapeType) => {
    const canvas = canvasRef.current;
    const newShape = {
      id: Date.now(),
      type: shapeType,
      x: canvas.width / 2 - 50,
      y: canvas.height / 2 - 50,
      width: 100,
      height: 100,
      fillColor: '#FF6B6B',
      strokeColor: '#000000',
      strokeWidth: 2,
      filled: true
    };
    
    setShapes([...shapes, newShape]);
    setSelectedShape(newShape.id);
    setSelectedElementType('shape');
  };

  // Función para agregar línea/flecha
  const addLine = (lineType = 'line') => {
    const canvas = canvasRef.current;
    const newLine = {
      id: Date.now(),
      type: lineType,
      startX: canvas.width / 2 - 50,
      startY: canvas.height / 2,
      endX: canvas.width / 2 + 50,
      endY: canvas.height / 2,
      color: '#000000',
      width: 3
    };
    
    setLines([...lines, newLine]);
    setSelectedLine(newLine.id);
    setSelectedElementType('line');
  };

  // Función para agregar fondo de texto
  const addTextBackground = (textId) => {
    const textEl = textElements.find(t => t.id === textId);
    if (!textEl) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const bounds = getTextBounds(textEl, ctx);
    
    const newBg = {
      id: Date.now(),
      textId: textId,
      x: bounds.x - 10,
      y: bounds.y - 10,
      width: bounds.width + 20,
      height: bounds.height + 20,
      color: 'rgba(0, 0, 0, 0.5)',
      shape: 'rectangle',
      radius: 10
    };
    
    setTextBackgrounds([...textBackgrounds, newBg]);
  };

  // Función para iniciar herramienta de recorte
  const startCropTool = () => {
    const canvas = canvasRef.current;
    const cropSize = Math.min(canvas.width, canvas.height) / 2;
    
    setCropArea({
      id: Date.now(),
      x: canvas.width / 2 - cropSize / 2,
      y: canvas.height / 2 - cropSize / 2,
      width: cropSize,
      height: cropSize
    });
    setCropMode(true);
  };

  // Función para aplicar recorte
  const applyCrop = () => {
    if (!cropArea || !image) return;
    
    const canvas = canvasRef.current;
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    
    tempCanvas.width = cropArea.width;
    tempCanvas.height = cropArea.height;
    
    // Calcular la relación entre el canvas y la imagen original
    const scaleX = image.naturalWidth / canvas.width;
    const scaleY = image.naturalHeight / canvas.height;
    
    // Recortar de la imagen original
    tempCtx.drawImage(
      image,
      cropArea.x * scaleX,
      cropArea.y * scaleY,
      cropArea.width * scaleX,
      cropArea.height * scaleY,
      0,
      0,
      cropArea.width,
      cropArea.height
    );
    
    // Crear nueva imagen recortada
    const croppedImg = new Image();
    croppedImg.onload = () => {
      setImage(croppedImg);
      setCropMode(false);
      setCropArea(null);
    };
    croppedImg.src = tempCanvas.toDataURL();
  };

  // Funciones de control de capas
  const moveElementUp = (elementType, elementId) => {
    switch (elementType) {
      case 'text':
        setTextElements(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index < prev.length - 1) {
            const newArray = [...prev];
            [newArray[index], newArray[index + 1]] = [newArray[index + 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
      case 'decorative':
        setDecorativeElements(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index < prev.length - 1) {
            const newArray = [...prev];
            [newArray[index], newArray[index + 1]] = [newArray[index + 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
      case 'shape':
        setShapes(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index < prev.length - 1) {
            const newArray = [...prev];
            [newArray[index], newArray[index + 1]] = [newArray[index + 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
    }
  };

  const moveElementDown = (elementType, elementId) => {
    switch (elementType) {
      case 'text':
        setTextElements(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index > 0) {
            const newArray = [...prev];
            [newArray[index], newArray[index - 1]] = [newArray[index - 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
      case 'decorative':
        setDecorativeElements(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index > 0) {
            const newArray = [...prev];
            [newArray[index], newArray[index - 1]] = [newArray[index - 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
      case 'shape':
        setShapes(prev => {
          const index = prev.findIndex(el => el.id === elementId);
          if (index > 0) {
            const newArray = [...prev];
            [newArray[index], newArray[index - 1]] = [newArray[index - 1], newArray[index]];
            return newArray;
          }
          return prev;
        });
        break;
    }
  };

  // Función para eliminar elemento
  const deleteElement = (elementType, elementId) => {
    switch (elementType) {
      case 'text':
        setTextElements(prev => prev.filter(el => el.id !== elementId));
        break;
      case 'decorative':
        setDecorativeElements(prev => prev.filter(el => el.id !== elementId));
        break;
      case 'shape':
        setShapes(prev => prev.filter(el => el.id !== elementId));
        break;
      case 'line':
        setLines(prev => prev.filter(el => el.id !== elementId));
        break;
      case 'textBackground':
        setTextBackgrounds(prev => prev.filter(el => el.id !== elementId));
        break;
    }
    
    // Limpiar selección
    setSelectedTextId(null);
    setSelectedElementId(null);
    setSelectedShape(null);
    setSelectedLine(null);
    setSelectedElementType(null);
  };


  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const resetFilters = () => {
    setFilters({
      brightness: 100,
      contrast: 100,
      saturation: 100,
      blur: 0,
      sepia: 0,
      grayscale: 0,
      hue: 0
    });
  };

  // 🎨 Renderizado limpio SIN elementos de UI para exportación
  const drawContentOnly = (ctx, img) => {
    console.log('🎨 Drawing content only...', { 
      hasContext: !!ctx, 
      hasImage: !!img,
      textCount: textElements.length,
      elementCount: decorativeElements.length
    });
    
    if (!ctx || !img) {
      console.error('❌ Missing context or image in drawContentOnly');
      return;
    }
    
    // Configurar tamaño del canvas manteniendo aspect ratio
    const maxSize = 600;
    const imgAspectRatio = img.naturalWidth / img.naturalHeight;
    
    let canvasWidth, canvasHeight;
    if (imgAspectRatio > 1) {
      canvasWidth = maxSize;
      canvasHeight = maxSize / imgAspectRatio;
    } else {
      canvasWidth = maxSize * imgAspectRatio;
      canvasHeight = maxSize;
    }
    
    console.log('🖼️ Setting canvas size:', { canvasWidth, canvasHeight });
    
    ctx.canvas.width = canvasWidth;
    ctx.canvas.height = canvasHeight;
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Aplicar filtros a la imagen
    ctx.filter = `
      brightness(${filters.brightness}%)
      contrast(${filters.contrast}%)
      saturate(${filters.saturation}%)
      hue-rotate(${filters.hue}deg)
      blur(${filters.blur}px)
      sepia(${filters.sepia}%)
    `;
    
    // Dibujar imagen base
    ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
    console.log('✅ Base image drawn');
    
    // Resetear filtros para elementos superpuestos
    ctx.filter = 'none';
    
    // Dibujar marco si está seleccionado
    if (selectedFrame !== 'none' && frameStyles[selectedFrame]) {
      const frame = frameStyles[selectedFrame];
      
      ctx.save();
      ctx.strokeStyle = frame.color;
      ctx.lineWidth = frame.width;
      ctx.setLineDash(frame.pattern);
      ctx.strokeRect(frame.width/2, frame.width/2, canvasWidth - frame.width, canvasHeight - frame.width);
      ctx.restore();
      console.log('✅ Frame drawn');
    }
    
    // Dibujar fondos de texto SIN bordes de selección (más atrás)
    textBackgrounds.forEach((bg, index) => {
      console.log(`🎨 Drawing background ${index + 1}:`, { shape: bg.shape, x: bg.x, y: bg.y });
      drawTextBackgroundContentOnly(ctx, bg);
    });
    
    // Dibujar formas geométricas SIN bordes de selección (detrás del texto)
    shapes.forEach((shape, index) => {
      console.log(`🔲 Drawing shape ${index + 1}:`, { type: shape.type, x: shape.x, y: shape.y });
      drawShapeContentOnly(ctx, shape);
    });
    
    // Dibujar líneas y flechas SIN bordes de selección (detrás del texto)
    lines.forEach((line, index) => {
      console.log(`↗️ Drawing line ${index + 1}:`, { type: line.type, startX: line.startX, startY: line.startY });
      drawLineContentOnly(ctx, line);
    });
    
    // Dibujar texto SIN bordes de selección (encima de formas)
    textElements.forEach((textEl, index) => {
      console.log(`✍️ Drawing text ${index + 1}:`, { text: textEl.text, x: textEl.x, y: textEl.y });
      drawTextContentOnly(ctx, textEl);
    });
    
    // Dibujar elementos decorativos SIN bordes de selección (al frente)
    decorativeElements.forEach((element, index) => {
      console.log(`🎭 Drawing element ${index + 1}:`, { type: element.type, content: element.content, x: element.x, y: element.y });
      drawDecorativeElementContentOnly(ctx, element);
    });
    
    console.log('🎨 Content drawing complete');
  };

  // 🎨 Dibujar texto multilínea sin elementos de UI (para guardado final)
  const drawTextContentOnly = (ctx, textEl) => {
    console.log('📝 Drawing multilíne text element:', textEl);
    
    ctx.save();
    ctx.font = `${textEl.fontWeight || 'normal'} ${textEl.fontSize}px ${textEl.fontFamily}`;
    ctx.fillStyle = textEl.color;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    const x = textEl.x;
    const y = textEl.y;
    const lines = textEl.lines || [textEl.text];
    const lineHeight = textEl.fontSize * 1.2;
    const containerWidth = textEl.width || 200;
    const maxWidth = containerWidth - 20;
    
    console.log('🎨 Text style applied:', {
      font: ctx.font,
      fillStyle: ctx.fillStyle,
      position: { x, y },
      lines: lines.length
    });
    
    // Aplicar efectos
    if (textEl.shadow) {
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      ctx.shadowBlur = 4;
      console.log('✅ Shadow applied');
    }
    
    // Procesar líneas con word wrapping (misma lógica que drawText)
    let renderedLines = [];
    
    lines.forEach(line => {
      if (!line.trim()) {
        renderedLines.push('');
        return;
      }
      
      // Estimación rápida para líneas cortas
      if (line.length < 20) {
        const metrics = ctx.measureText(line);
        if (metrics.width <= maxWidth) {
          renderedLines.push(line);
          return;
        }
      }
      
      const words = line.split(' ');
      let currentLine = '';
      
      for (let i = 0; i < words.length; i++) {
        const testLine = currentLine + (currentLine ? ' ' : '') + words[i];
        const metrics = ctx.measureText(testLine);
        
        if (metrics.width > maxWidth && currentLine) {
          renderedLines.push(currentLine);
          currentLine = words[i];
        } else {
          currentLine = testLine;
        }
      }
      
      if (currentLine) {
        renderedLines.push(currentLine);
      }
    });
    
    // Dibujar cada línea renderizada
    const startY = y - (renderedLines.length - 1) * lineHeight / 2;
    renderedLines.forEach((line, index) => {
      const lineY = startY + (index * lineHeight);
      
      // Contorno si está habilitado
      if (textEl.outline) {
        ctx.strokeStyle = textEl.outline === true ? '#000000' : textEl.outline;
        ctx.lineWidth = 3;
        ctx.strokeText(line, x, lineY);
        console.log('✅ Stroke applied to line:', line);
      }
      
      // Texto principal
      ctx.fillText(line, x, lineY);
    });
    
    console.log('✅ Multilíne text drawn:', renderedLines.length, 'lines');
    ctx.restore();
  };

  // 🎨 Dibujar elementos decorativos sin bordes de selección
  const drawDecorativeElementContentOnly = (ctx, element) => {
    console.log('🎭 Drawing decorative element:', { 
      type: element.type, 
      content: element.content, 
      x: element.x, 
      y: element.y 
    });
    
    if (element.type === 'emoji') {
      const size = element.size || 40;
      ctx.save();
      
      // Usar fuentes que soporten emojis para mejor renderizado
      ctx.font = `${size}px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", Arial, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      console.log('🎨 Emoji style applied:', {
        font: ctx.font,
        position: { x: element.x, y: element.y },
        content: element.content
      });
      
      // Centrar emoji correctamente
      ctx.fillText(element.content, element.x, element.y);
      console.log('✅ Emoji drawn:', element.content);
      ctx.restore();
    }
    
    // 🎨 Renderizar Giphy Stickers SIN bordes de selección
    else if (element.type === 'sticker' && element.loaded && element.image) {
      const halfWidth = element.width / 2;
      const halfHeight = element.height / 2;
      
      console.log('🎨 Sticker style applied:', {
        position: { x: element.x, y: element.y },
        size: { width: element.width, height: element.height }
      });
      
      // Solo el sticker, sin bordes de selección
      ctx.drawImage(
        element.image, 
        element.x - halfWidth, 
        element.y - halfHeight, 
        element.width, 
        element.height
      );
      console.log('✅ Sticker drawn');
    }
    else {
      console.warn('⚠️ Unknown element type or incomplete data:', element);
    }
  };

  // 🎨 Dibujar formas geométricas sin bordes de selección
  const drawShapeContentOnly = (ctx, shape) => {
    ctx.save();
    
    // Aplicar estilo
    ctx.fillStyle = shape.fillColor || '#FF6B6B';
    ctx.strokeStyle = shape.strokeColor || '#000000';
    ctx.lineWidth = shape.strokeWidth || 2;
    
    if (shape.type === 'rectangle') {
      if (shape.filled) {
        ctx.fillRect(shape.x, shape.y, shape.width, shape.height);
      }
      ctx.strokeRect(shape.x, shape.y, shape.width, shape.height);
    }
    
    else if (shape.type === 'circle') {
      ctx.beginPath();
      ctx.arc(shape.x + shape.width/2, shape.y + shape.height/2, Math.min(shape.width, shape.height)/2, 0, 2 * Math.PI);
      if (shape.filled) {
        ctx.fill();
      }
      ctx.stroke();
    }
    
    else if (shape.type === 'triangle') {
      ctx.beginPath();
      ctx.moveTo(shape.x + shape.width/2, shape.y);
      ctx.lineTo(shape.x, shape.y + shape.height);
      ctx.lineTo(shape.x + shape.width, shape.y + shape.height);
      ctx.closePath();
      if (shape.filled) {
        ctx.fill();
      }
      ctx.stroke();
    }
    
    ctx.restore();
  };

  // 🎨 Dibujar líneas sin bordes de selección
  const drawLineContentOnly = (ctx, line) => {
    ctx.save();
    ctx.strokeStyle = line.color || '#000000';
    ctx.lineWidth = line.width || 2;
    
    ctx.beginPath();
    ctx.moveTo(line.startX, line.startY);
    ctx.lineTo(line.endX, line.endY);
    ctx.stroke();
    
    // Dibujar flecha si es necesario
    if (line.type === 'arrow') {
      const angle = Math.atan2(line.endY - line.startY, line.endX - line.startX);
      const arrowLength = 15;
      const arrowAngle = Math.PI / 6;
      
      ctx.beginPath();
      ctx.moveTo(line.endX, line.endY);
      ctx.lineTo(
        line.endX - arrowLength * Math.cos(angle - arrowAngle),
        line.endY - arrowLength * Math.sin(angle - arrowAngle)
      );
      ctx.moveTo(line.endX, line.endY);
      ctx.lineTo(
        line.endX - arrowLength * Math.cos(angle + arrowAngle),
        line.endY - arrowLength * Math.sin(angle + arrowAngle)
      );
      ctx.stroke();
    }
    
    ctx.restore();
  };

  // 🎨 Dibujar fondos de texto sin bordes de selección
  const drawTextBackgroundContentOnly = (ctx, bg) => {
    ctx.save();
    ctx.fillStyle = bg.color || 'rgba(0, 0, 0, 0.5)';
    
    if (bg.shape === 'rectangle') {
      ctx.fillRect(bg.x, bg.y, bg.width, bg.height);
    } else if (bg.shape === 'rounded') {
      const radius = bg.radius || 10;
      ctx.beginPath();
      ctx.roundRect(bg.x, bg.y, bg.width, bg.height, radius);
      ctx.fill();
    } else if (bg.shape === 'circle') {
      ctx.beginPath();
      ctx.arc(bg.x + bg.width/2, bg.y + bg.height/2, Math.min(bg.width, bg.height)/2, 0, 2 * Math.PI);
      ctx.fill();
    }
    
    ctx.restore();
  };

  const saveImage = () => {
    console.log('🚀 Starting saveImage process...');
    
    if (!image) {
      console.error('❌ No image to save');
      return;
    }
    
    if (!textElements.length && !decorativeElements.length && !shapes.length && !lines.length && !textBackgrounds.length) {
      console.warn('⚠️ No elements to save - using original image');
      // Si no hay elementos, usar imagen original
      onSave(imageData);
      return;
    }
    
    try {
      // Crear canvas temporal limpio
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d');
      
      if (!tempCtx) {
        console.error('❌ Could not get canvas context');
        return;
      }
      
      console.log('📝 Elements to draw:', {
        textElements: textElements.map(t => ({ text: t.text, x: t.x, y: t.y })),
        decorativeElements: decorativeElements.map(d => ({ type: d.type, content: d.content, x: d.x, y: d.y })),
        shapes: shapes.map(s => ({ type: s.type, x: s.x, y: s.y })),
        lines: lines.map(l => ({ type: l.type, startX: l.startX, startY: l.startY })),
        textBackgrounds: textBackgrounds.map(b => ({ shape: b.shape, x: b.x, y: b.y }))
      });
      
      // Renderizar solo contenido final (sin elementos UI)
      drawContentOnly(tempCtx, image);
      
      console.log('🎯 Canvas after drawing:', {
        width: tempCanvas.width,
        height: tempCanvas.height,
        hasImageData: tempCanvas.toDataURL().length > 1000
      });
      
      // Verificar que el canvas tenga contenido
      const dataURL = tempCanvas.toDataURL();
      if (dataURL.length < 1000) {
        console.error('❌ Canvas appears empty');
        return;
      }
      
      tempCanvas.toBlob((blob) => {
        if (!blob) {
          console.error('❌ Failed to create blob from canvas');
          return;
        }
        
        console.log('✅ Successfully created edited image blob:', blob.size, 'bytes');
        
        const editedImageData = {
          ...imageData,
          file: new File([blob], imageData.name || 'edited-image.png', { type: 'image/png' }),
          preview: dataURL
        };
        
        console.log('💾 Calling onSave with edited data');
        onSave(editedImageData);
      }, 'image/png', 1.0); // Máxima calidad
    } catch (error) {
      console.error('❌ Error saving image:', error);
    }
  };

  //  BIBLIOTECA EXPANDIDA DE EMOJIS POR CATEGORÍAS
  const emojiCategories = {
    emotions: {
      name: '😊 Emociones',
      emojis: ['😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐']
    },
    hearts: {
      name: '❤️ Corazones',
      emojis: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '♥️', '💌', '💐', '🌹', '🌺', '🌸', '🌻']
    },
    people: {
      name: '👥 Personas',
      emojis: [
        // Personas claras
        '👶', '🧒', '👦', '👧', '🧑', '👱', '👨', '🧔', '👩', '🧓', '👴', '👵',
        // Personas morenas
        '👶🏽', '🧒🏽', '👦🏽', '👧🏽', '🧑🏽', '👨🏽', '🧔🏽', '👩🏽', '🧓🏽', '👴🏽', '👵🏽',
        // Personas negras
        '👶🏿', '🧒🏿', '👦🏿', '👧🏿', '🧑🏿', '👨🏿', '🧔🏿', '👩🏿', '🧓🏿', '👴🏿', '👵🏿',
        // Expresiones diversas
        '🙍', '🙍🏽', '🙍🏿', '🙎', '🙎🏽', '🙎🏿', '🙅', '🙅🏽', '🙅🏿', '💁', '💁🏽', '💁🏿'
      ]
    },
    animals: {
      name: '🐶 Animales',
      emojis: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒', '🐔', '🐧', '🐦', '🐤', '🐣', '🐥']
    },
    nature: {
      name: '🌿 Naturaleza',
      emojis: ['🌿', '🍀', '🎍', '🎋', '🍃', '🍂', '🍁', '🍄', '🌾', '💐', '🌷', '🌹', '🥀', '🌺', '🌸', '🌼', '🌻', '🌞', '🌝', '🌛', '🌜', '🌚', '🌕', '🌖', '🌗', '🌘']
    },
    gestures: {
      name: '👋 Gestos',
      emojis: ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '👊', '✊', '🤛', '🤜', '👏']
    },
    symbols: {
      name: '⭐ Símbolos',
      emojis: ['⭐', '🌟', '✨', '💫', '🌠', '☀️', '🌞', '🌝', '🌛', '🌜', '🌚', '🌕', '🌖', '🌗', '🌘', '🌑', '🌒', '🌓', '🌔', '🔥', '⚡', '💢', '💨', '💦', '❄️', '💎']
    },
    objects: {
      name: '📱 Objetos',
      emojis: ['📱', '💻', '🖥️', '🖨️', '⌨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '🧮', '🎥', '🎞️', '📹', '📷', '📸', '📻', '🎙️', '🎚️', '🎛️', '🧭', '⏱️', '⏲️', '⏰', '🕰️']
    },
    food: {
      name: '🍕 Comida',
      emojis: ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕']
    },
    activities: {
      name: '⚽ Actividades',
      emojis: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋']
    },
    business: {
      name: '💼 Negocios',
      emojis: ['💼', '📊', '📈', '📉', '🗂️', '📋', '📌', '📍', '📎', '🖇️', '📏', '📐', '✂️', '🗃️', '🗄️', '🗑️', '🔒', '🔓', '🔏', '🔐', '🔑', '🗝️', '🔨', '🪓', '⛏️', '⚒️']
    }
  };

  //  BIBLIOTECA EXPANDIDA DE FUENTES PROFESIONALES
  const fontCategories = {
    modern: {
      name: 'Moderna',
      fonts: [
        'Arial', 'Helvetica', 'Calibri', 'Segoe UI', 'Roboto', 'Open Sans', 
        'Lato', 'Source Sans Pro', 'Montserrat', 'Nunito', 'Poppins', 'Inter'
      ]
    },
    classic: {
      name: 'Clásica', 
      fonts: [
        'Times New Roman', 'Georgia', 'Garamond', 'Book Antiqua', 
        'Palatino', 'Baskerville', 'Minion Pro', 'Caslon'
      ]
    },
    creative: {
      name: 'Creativa',
      fonts: [
        'Impact', 'Bebas Neue', 'Oswald', 'Raleway', 'Playfair Display',
        'Dancing Script', 'Lobster', 'Pacifico', 'Quicksand', 'Comfortaa'
      ]
    },
    tech: {
      name: 'Técnica',
      fonts: [
        'Courier New', 'Consolas', 'Monaco', 'Source Code Pro', 
        'Fira Code', 'SF Mono', 'Inconsolata', 'Roboto Mono'
      ]
    },
    handwritten: {
      name: 'Manuscrita',
      fonts: [
        'Comic Sans MS', 'Brush Script MT', 'Lucida Handwriting',
        'Marker Felt', 'Chalkduster', 'Bradley Hand', 'Snell Roundhand'
      ]
    },
    display: {
      name: 'Decorativa',
      fonts: [
        'Verdana', 'Tahoma', 'Trebuchet MS', 'Century Gothic',
        'Franklin Gothic', 'Arial Black', 'Cooper Black', 'Stencil'
      ]
    }
  };

  //  PALETA DE COLORES EXPANDIDA CON GRADIENTES
  const colorPalettes = {
    basic: {
      name: 'Básicos',
      colors: ['#FFFFFF', '#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
    },
    social: {
      name: 'Redes Sociales',
      colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    },
    business: {
      name: 'Profesional',
      colors: ['#2C3E50', '#34495E', '#3498DB', '#E74C3C', '#F39C12', '#27AE60', '#8E44AD', '#95A5A6']
    },
    vibrant: {
      name: 'Vibrante',
      colors: ['#FF1744', '#FF9100', '#FFEA00', '#00E676', '#00BCD4', '#3F51B5', '#9C27B0', '#E91E63']
    },
    pastel: {
      name: 'Pastel',
      colors: ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#DDBAFF', '#FFBADD', '#C5E3FF']
    },
    neon: {
      name: 'Neón',
      colors: ['#FF073A', '#39FF14', '#FF0099', '#00FFFF', '#FFFF00', '#FF6600', '#9933FF', '#FF3366']
    },
    earth: {
      name: 'Tierra',
      colors: ['#8B4513', '#D2691E', '#CD853F', '#DEB887', '#F4A460', '#D2B48C', '#BC8F8F', '#A0522D']
    },
    ocean: {
      name: 'Océano',
      colors: ['#006994', '#1E90FF', '#00CED1', '#20B2AA', '#48D1CC', '#87CEEB', '#B0E0E6', '#AFEEEE']
    }
  };

  const availableFonts = Object.values(fontCategories).flatMap(category => category.fonts);

  // Estilos CSS para scroll personalizado
  const scrollbarStyles = `
    /* Webkit Scrollbar */
    .editor-scroll::-webkit-scrollbar {
      width: 8px;
    }
    .editor-scroll::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    .editor-scroll::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      transition: background 0.3s ease;
    }
    .editor-scroll::-webkit-scrollbar-thumb:hover {
      background: #a1a1a1;
    }
    /* Firefox Scrollbar */
    .editor-scroll {
      scrollbar-width: thin;
      scrollbar-color: #c1c1c1 #f1f1f1;
    }
  `;

  return (
    <>
      <style>{scrollbarStyles}</style>
      <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
      <div className="bg-white rounded-xl max-w-6xl w-full h-full max-h-[95vh] flex overflow-hidden shadow-2xl">
        {/* Panel de herramientas - SCROLL FIJO */}
        <div className="w-80 bg-gray-50 flex flex-col h-full">
          {/* Header fijo */}
          <div className="flex justify-between items-center p-4 border-b border-gray-200 bg-gray-50 flex-shrink-0">
            <h3 className="text-lg font-semibold text-gray-900"> Editor de Imagen</h3>
            <button
              onClick={onCancel}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
              title="Cerrar editor"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs fijos */}
          <div className="p-4 pb-0 bg-gray-50 flex-shrink-0">
            <div className="flex mb-4 space-x-1">
              {[
                { id: 'filters', label: 'Filtros', icon: Filter },
                { id: 'text', label: 'Texto', icon: Type },
                { id: 'decorations', label: 'Decorar', icon: Smile },
                { id: 'shapes', label: 'Formas', icon: Square },
                { id: 'lines', label: 'Líneas', icon: ArrowRight },
                { id: 'crop', label: 'Recorte', icon: Crop },
                { id: 'layers', label: 'Capas', icon: Layers },
                { id: 'frames', label: 'Marcos', icon: ImageIcon }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center gap-1 p-2 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === tab.id 
                      ? 'bg-purple-500 text-white shadow-md' 
                      : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Contenido scrollable */}
          <div className="flex-1 overflow-y-auto px-4" style={{ 
            scrollbarWidth: 'thin',
            scrollbarColor: '#CBD5E0 #F7FAFC'
          }}>
            {/* Contenido de tabs */}
            <div className="space-y-4 py-2">
              {activeTab === 'filters' && (
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-gray-800">Ajustar Filtros</h4>
                    <button
                      onClick={resetFilters}
                      className="text-xs text-purple-600 hover:text-purple-800"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {Object.entries(filters).map(([key, value]) => (
                    <div key={key} className="mb-3">
                      <label className="block text-xs font-medium text-gray-700 mb-1 capitalize">
                        {key === 'hue' ? 'Matiz' : key === 'brightness' ? 'Brillo' : 
                         key === 'contrast' ? 'Contraste' : key === 'saturation' ? 'Saturación' :
                         key === 'blur' ? 'Desenfoque' : key === 'sepia' ? 'Sepia' : 'Escala de grises'}
                      </label>
                      <input
                        type="range"
                        min={key === 'hue' ? -180 : 0}
                        max={key === 'brightness' || key === 'contrast' || key === 'saturation' ? 200 : 
                             key === 'blur' ? 10 : key === 'hue' ? 180 : 100}
                        value={value}
                        onChange={(e) => handleFilterChange(key, parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <div className="text-xs text-gray-500 text-center mt-1">
                        {value}{key === 'blur' ? 'px' : key === 'hue' ? '°' : '%'}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'text' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">Agregar Texto</h4>
                  
                  <div className="space-y-3">
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Escribe tu texto aquí...&#10;(Usa Enter para múltiples líneas)"
                      className="w-full p-2 border border-gray-300 rounded-lg text-sm resize-none"
                      rows={3}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                          // Ctrl+Enter o Cmd+Enter para agregar texto rápidamente
                          e.preventDefault();
                          if (textInput.trim()) {
                            addTextElement();
                          }
                        }
                      }}
                    />
                    
                    {/* Selector de fuentes por categorías */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-2"> Fuentes por Categoría</label>
                      {Object.entries(fontCategories).map(([category, { name, fonts }]) => (
                        <details key={category} className="mb-2">
                          <summary className="text-xs font-medium text-purple-600 cursor-pointer hover:text-purple-800 mb-1 flex items-center gap-1">
                            <span>{name}</span> 
                            <span className="text-gray-400">({fonts.length})</span>
                          </summary>
                          <div className="grid grid-cols-1 gap-1 ml-2 max-h-32 overflow-y-auto">
                            {fonts.map(font => (
                              <button
                                key={font}
                                onClick={() => setTextStyle(prev => ({...prev, fontFamily: font}))}
                                className={`text-xs p-2 rounded border text-left transition-colors ${
                                  textStyle.fontFamily === font
                                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                                    : 'border-gray-200 hover:border-purple-300 text-gray-600'
                                }`}
                                style={{ fontFamily: font }}
                              >
                                {font}
                              </button>
                            ))}
                          </div>
                        </details>
                      ))}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Tamaño</label>
                        <input
                          type="range"
                          min="12"
                          max="72"
                          value={textStyle.fontSize}
                          onChange={(e) => setTextStyle(prev => ({...prev, fontSize: parseInt(e.target.value)}))}
                          className="w-full"
                        />
                        <div className="text-xs text-gray-500 text-center">{textStyle.fontSize}px</div>
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Estilo</label>
                        <div className="flex gap-1">
                          <button
                            onClick={() => setTextStyle(prev => ({...prev, fontWeight: prev.fontWeight === 'bold' ? 'normal' : 'bold'}))}
                            className={`flex-1 p-1 rounded text-xs font-bold transition-colors ${
                              textStyle.fontWeight === 'bold' ? 'bg-purple-500 text-white' : 'bg-gray-200 text-gray-600'
                            }`}
                          >
                            B
                          </button>
                          <button
                            onClick={() => setTextStyle(prev => ({...prev, fontStyle: prev.fontStyle === 'italic' ? 'normal' : 'italic'}))}
                            className={`flex-1 p-1 rounded text-xs italic transition-colors ${
                              textStyle.fontStyle === 'italic' ? 'bg-purple-500 text-white' : 'bg-gray-200 text-gray-600'
                            }`}
                          >
                            I
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    {/* Paletas de colores expandidas */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-2"> Paletas de Colores</label>
                      <div className="flex gap-2 mb-2">
                        <input
                          type="color"
                          value={textStyle.color}
                          onChange={(e) => setTextStyle(prev => ({...prev, color: e.target.value}))}
                          className="w-8 h-8 rounded border border-gray-300"
                        />
                        <span className="text-xs text-gray-600 flex items-center">Selector libre</span>
                      </div>
                      
                      {Object.entries(colorPalettes).map(([category, { name, colors }]) => (
                        <details key={category} className="mb-2">
                          <summary className="text-xs font-medium text-purple-600 cursor-pointer hover:text-purple-800 mb-1">
                            {name} ({colors.length} colores)
                          </summary>
                          <div className="grid grid-cols-8 gap-1 ml-2">
                            {colors.map(color => (
                              <button
                                key={color}
                                onClick={() => setTextStyle(prev => ({...prev, color}))}
                                className={`w-6 h-6 rounded border-2 transition-all hover:scale-110 ${
                                  textStyle.color === color ? 'border-purple-500' : 'border-gray-300'
                                }`}
                                style={{ backgroundColor: color }}
                                title={color}
                              />
                            ))}
                          </div>
                        </details>
                      ))}
                    </div>
                    
                    <div className="flex gap-2">
                      <label className="flex items-center text-xs">
                        <input
                          type="checkbox"
                          checked={textStyle.shadow}
                          onChange={(e) => setTextStyle(prev => ({...prev, shadow: e.target.checked}))}
                          className="mr-1"
                        />
                        Sombra
                      </label>
                      <label className="flex items-center text-xs">
                        <input
                          type="checkbox"
                          checked={textStyle.outline}
                          onChange={(e) => setTextStyle(prev => ({...prev, outline: e.target.checked}))}
                          className="mr-1"
                        />
                        Contorno
                      </label>
                    </div>
                    
                    <button
                      onClick={addTextElement}
                      disabled={!textInput.trim()}
                      className="w-full bg-purple-500 text-white p-2 rounded-lg text-sm font-medium hover:bg-purple-600 disabled:opacity-50"
                    >
                      <Plus className="w-4 h-4 inline mr-1" />
                      Agregar Texto
                    </button>
                  </div>
                  
                  {textElements.length > 0 && (
                    <div className="mt-4">
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Textos agregados:</h5>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {textElements.map((textEl) => (
                          <div key={textEl.id} className="flex items-center justify-between bg-gray-100 p-2 rounded">
                            <span className="text-xs truncate flex-1">{textEl.text}</span>
                            <button
                              onClick={() => setTextElements(prev => prev.filter(t => t.id !== textEl.id))}
                              className="text-red-500 hover:text-red-700 ml-2"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'decorations' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3"> Elementos Decorativos</h4>
                  
                  {/* Emojis organizados por categorías */}
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-3">Biblioteca de Emojis ({Object.values(emojiCategories).reduce((acc, cat) => acc + cat.emojis.length, 0)} emojis)</h5>
                    
                    {Object.entries(emojiCategories).map(([category, { name, emojis }]) => (
                      <details key={category} className="mb-3">
                        <summary className="text-xs font-medium text-purple-600 cursor-pointer hover:text-purple-800 mb-2 flex items-center gap-2">
                          <span>{name}</span>
                          <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs">{emojis.length}</span>
                        </summary>
                        <div className="grid grid-cols-6 gap-2 ml-2 max-h-40 overflow-y-auto bg-gray-50 p-2 rounded-lg">
                          {emojis.map((emoji) => (
                            <button
                              key={emoji}
                              onClick={() => addEmoji(emoji)}
                              className="text-2xl p-2 hover:bg-white hover:shadow-sm rounded-lg transition-all hover:scale-110 active:scale-95"
                              title={`Agregar ${emoji}`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>

                  {/* Giphy Stickers */}
                  <div className="mt-6 border-t pt-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-3">Giphy Stickers</h5>
                    
                    {/* Search Categories */}
                    <div className="mb-3">
                      <div className="flex gap-2 mb-2">
                        {['trending', 'emoji', 'reaction', 'cute'].map((category) => (
                          <button
                            key={category}
                            onClick={() => {
                              console.log('🎯 Clic en categoría:', category);
                              setStickerCategory(category);
                              setCurrentStickers([]);
                              setStickerLoading(true);
                              searchGiphyStickers('', category);
                            }}
                            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                              stickerCategory === category 
                                ? 'bg-green-500 text-white border-green-500' 
                                : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                            }`}
                          >
                            {category.charAt(0).toUpperCase() + category.slice(1)}
                          </button>
                        ))}
                      </div>
                      
                      <input
                        type="text"
                        placeholder="Buscar stickers..."
                        value={stickerSearchQuery}
                        onChange={(e) => setStickerSearchQuery(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            console.log('🔍 Búsqueda con Enter:', e.target.value, stickerCategory);
                            setCurrentStickers([]);
                            setStickerLoading(true);
                            searchGiphyStickers(e.target.value, stickerCategory);
                          }
                        }}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      />
                    </div>

                    {/* Stickers Grid */}
                    <div className="max-h-48 overflow-y-auto">
                      {stickerLoading ? (
                        <div className="flex justify-center items-center py-8">
                          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500"></div>
                          <span className="ml-2 text-sm text-gray-600">Cargando stickers...</span>
                        </div>
                      ) : currentStickers.length > 0 ? (
                        <div className="grid grid-cols-3 gap-2">
                          {currentStickers.map((sticker, index) => (
                            <button
                              key={`${sticker.id}-${index}`}
                              onClick={() => addSticker(sticker)}
                              className="aspect-square border border-gray-200 rounded-lg overflow-hidden hover:border-green-400 hover:shadow-md transition-all transform hover:scale-105 active:scale-95 bg-gray-50"
                              title={sticker.title || 'Giphy Sticker'}
                            >
                              <img
                                src={sticker.images.preview_gif?.url || sticker.images.fixed_width_small?.url}
                                alt={sticker.title || 'Sticker'}
                                className="w-full h-full object-cover"
                                loading="lazy"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                }}
                              />
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <p className="text-sm">No hay stickers para mostrar</p>
                          <p className="text-xs mt-1">Selecciona una categoría o busca stickers</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {decorativeElements.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Elementos agregados:</h5>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {decorativeElements.map((element) => (
                          <div key={element.id} className="flex items-center justify-between bg-gray-100 p-2 rounded">
                            <span className="text-lg">{element.content}</span>
                            <button
                              onClick={() => setDecorativeElements(prev => prev.filter(e => e.id !== element.id))}
                              className="text-red-500 hover:text-red-700 ml-2"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'shapes' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">🔲 Formas Geométricas</h4>
                  
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <button
                      onClick={() => addShape('rectangle')}
                      className="flex flex-col items-center gap-1 p-3 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
                    >
                      <Square className="w-6 h-6 text-orange-600" />
                      <span className="text-xs text-orange-700">Rectángulo</span>
                    </button>
                    <button
                      onClick={() => addShape('circle')}
                      className="flex flex-col items-center gap-1 p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      <Circle className="w-6 h-6 text-blue-600" />
                      <span className="text-xs text-blue-700">Círculo</span>
                    </button>
                    <button
                      onClick={() => addShape('triangle')}
                      className="flex flex-col items-center gap-1 p-3 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                    >
                      <Triangle className="w-6 h-6 text-green-600" />
                      <span className="text-xs text-green-700">Triángulo</span>
                    </button>
                  </div>

                  {/* Controles para forma seleccionada */}
                  {selectedShape && (
                    <div className="mb-4 p-3 bg-orange-50 rounded-lg border">
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Editar Forma Seleccionada</h5>
                      <div className="space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="text-xs text-gray-600">Tamaño</label>
                            <input
                              type="range"
                              min="20"
                              max="200"
                              value={shapes.find(s => s.id === selectedShape)?.width || 100}
                              onChange={(e) => {
                                const newSize = parseInt(e.target.value);
                                setShapes(prev => prev.map(s => 
                                  s.id === selectedShape 
                                    ? { ...s, width: newSize, height: newSize }
                                    : s
                                ));
                              }}
                              className="w-full"
                            />
                            <div className="text-xs text-gray-500 text-center">
                              {shapes.find(s => s.id === selectedShape)?.width || 100}px
                            </div>
                          </div>
                          <div>
                            <label className="text-xs text-gray-600">Borde</label>
                            <input
                              type="range"
                              min="1"
                              max="10"
                              value={shapes.find(s => s.id === selectedShape)?.strokeWidth || 2}
                              onChange={(e) => {
                                setShapes(prev => prev.map(s => 
                                  s.id === selectedShape 
                                    ? { ...s, strokeWidth: parseInt(e.target.value) }
                                    : s
                                ));
                              }}
                              className="w-full"
                            />
                            <div className="text-xs text-gray-500 text-center">
                              {shapes.find(s => s.id === selectedShape)?.strokeWidth || 2}px
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="text-xs text-gray-600">Color Relleno</label>
                            <input
                              type="color"
                              value={shapes.find(s => s.id === selectedShape)?.fillColor || '#FF6B6B'}
                              onChange={(e) => {
                                setShapes(prev => prev.map(s => 
                                  s.id === selectedShape 
                                    ? { ...s, fillColor: e.target.value }
                                    : s
                                ));
                              }}
                              className="w-full h-8 rounded border"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-gray-600">Color Borde</label>
                            <input
                              type="color"
                              value={shapes.find(s => s.id === selectedShape)?.strokeColor || '#000000'}
                              onChange={(e) => {
                                setShapes(prev => prev.map(s => 
                                  s.id === selectedShape 
                                    ? { ...s, strokeColor: e.target.value }
                                    : s
                                ));
                              }}
                              className="w-full h-8 rounded border"
                            />
                          </div>
                        </div>
                        
                        <label className="flex items-center text-xs">
                          <input
                            type="checkbox"
                            checked={shapes.find(s => s.id === selectedShape)?.filled || true}
                            onChange={(e) => {
                              setShapes(prev => prev.map(s => 
                                s.id === selectedShape 
                                  ? { ...s, filled: e.target.checked }
                                  : s
                              ));
                            }}
                            className="mr-1"
                          />
                          Relleno sólido
                        </label>
                      </div>
                    </div>
                  )}
                  
                  {shapes.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Formas agregadas:</h5>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {shapes.map((shape) => (
                          <div key={shape.id} className={`flex items-center justify-between p-2 rounded border-2 ${
                            selectedShape === shape.id ? 'border-orange-500 bg-orange-50' : 'border-gray-200 bg-gray-100'
                          }`}>
                            <button
                              onClick={() => setSelectedShape(shape.id)}
                              className="text-xs flex-1 text-left"
                            >
                              {shape.type} ({shape.width}x{shape.height})
                            </button>
                            <div className="flex gap-1">
                              <button
                                onClick={() => moveElementUp('shape', shape.id)}
                                className="text-blue-500 hover:text-blue-700"
                                title="Subir"
                              >
                                <ChevronUp className="w-3 h-3" />
                              </button>
                              <button
                                onClick={() => moveElementDown('shape', shape.id)}
                                className="text-blue-500 hover:text-blue-700"
                                title="Bajar"
                              >
                                <ChevronDown className="w-3 h-3" />
                              </button>
                              <button
                                onClick={() => deleteElement('shape', shape.id)}
                                className="text-red-500 hover:text-red-700"
                                title="Eliminar"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'lines' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">↗️ Líneas y Flechas</h4>
                  
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    <button
                      onClick={() => addLine('line')}
                      className="flex flex-col items-center gap-1 p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="w-6 h-1 bg-gray-600"></div>
                      <span className="text-xs text-gray-700">Línea</span>
                    </button>
                    <button
                      onClick={() => addLine('arrow')}
                      className="flex flex-col items-center gap-1 p-3 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors"
                    >
                      <ArrowRight className="w-6 h-6 text-yellow-600" />
                      <span className="text-xs text-yellow-700">Flecha</span>
                    </button>
                  </div>
                  
                  {lines.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Líneas agregadas:</h5>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {lines.map((line) => (
                          <div key={line.id} className="flex items-center justify-between bg-gray-100 p-2 rounded">
                            <span className="text-xs">{line.type} (grosor: {line.width}px)</span>
                            <button
                              onClick={() => deleteElement('line', line.id)}
                              className="text-red-500 hover:text-red-700"
                              title="Eliminar"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}


              {activeTab === 'crop' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">✂️ Herramienta de Recorte</h4>
                  
                  <div className="space-y-3">
                    <button
                      onClick={startCropTool}
                      disabled={cropMode}
                      className="w-full flex items-center justify-center gap-2 p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Crop className="w-4 h-4" />
                      {cropMode ? 'Modo Recorte Activo' : 'Iniciar Recorte'}
                    </button>
                    
                    {cropMode && (
                      <div className="space-y-2">
                        <div className="text-xs text-gray-600 bg-green-50 p-2 rounded">
                          Arrastra el área de recorte y redimensiona con las manijas
                        </div>
                        
                        <div className="flex gap-2">
                          <button
                            onClick={applyCrop}
                            className="flex-1 bg-green-500 text-white p-2 rounded text-sm hover:bg-green-600"
                          >
                            Aplicar Recorte
                          </button>
                          <button
                            onClick={() => {
                              setCropMode(false);
                              setCropArea(null);
                            }}
                            className="flex-1 bg-gray-500 text-white p-2 rounded text-sm hover:bg-gray-600"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'layers' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">📚 Control de Capas</h4>
                  
                  <div className="space-y-2">
                    {/* Mostrar todos los elementos con controles de capa */}
                    {textElements.length > 0 && (
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Textos</h6>
                        {textElements.map((text, index) => (
                          <div key={text.id} className="flex items-center justify-between bg-blue-50 p-2 rounded text-xs">
                            <span className="truncate">{text.text}</span>
                            <div className="flex gap-1">
                              <button onClick={() => moveElementUp('text', text.id)} className="text-blue-600">
                                <ChevronUp className="w-3 h-3" />
                              </button>
                              <button onClick={() => moveElementDown('text', text.id)} className="text-blue-600">
                                <ChevronDown className="w-3 h-3" />
                              </button>
                              <button onClick={() => deleteElement('text', text.id)} className="text-red-600">
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {decorativeElements.length > 0 && (
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Elementos Decorativos</h6>
                        {decorativeElements.map((element) => (
                          <div key={element.id} className="flex items-center justify-between bg-purple-50 p-2 rounded text-xs">
                            <span>{element.type === 'emoji' ? element.content : 'Sticker'}</span>
                            <div className="flex gap-1">
                              <button onClick={() => moveElementUp('decorative', element.id)} className="text-purple-600">
                                <ChevronUp className="w-3 h-3" />
                              </button>
                              <button onClick={() => moveElementDown('decorative', element.id)} className="text-purple-600">
                                <ChevronDown className="w-3 h-3" />
                              </button>
                              <button onClick={() => deleteElement('decorative', element.id)} className="text-red-600">
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {shapes.length > 0 && (
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Formas</h6>
                        {shapes.map((shape) => (
                          <div key={shape.id} className="flex items-center justify-between bg-orange-50 p-2 rounded text-xs">
                            <span>{shape.type}</span>
                            <div className="flex gap-1">
                              <button onClick={() => moveElementUp('shape', shape.id)} className="text-orange-600">
                                <ChevronUp className="w-3 h-3" />
                              </button>
                              <button onClick={() => moveElementDown('shape', shape.id)} className="text-orange-600">
                                <ChevronDown className="w-3 h-3" />
                              </button>
                              <button onClick={() => deleteElement('shape', shape.id)} className="text-red-600">
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'frames' && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">🖼️ Marcos y Bordes Profesionales</h4>
                  <p className="text-xs text-gray-600 mb-4">{Object.keys(frameStyles).length} marcos únicos disponibles</p>
                  
                  <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto">
                    {Object.entries(frameStyles).map(([frameId, frame]) => (
                      <button
                        key={frameId}
                        onClick={() => setSelectedFrame(frameId)}
                        className={`p-3 rounded-lg border-2 text-left transition-all hover:shadow-md ${
                          selectedFrame === frameId
                            ? 'border-purple-500 bg-purple-50 text-purple-700 shadow-md'
                            : 'border-gray-200 hover:border-purple-300 text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{frame.preview}</span>
                          <div>
                            <div className="font-medium text-sm">{frame.name}</div>
                            {frame.description && (
                              <div className="text-xs text-gray-500 mt-1">{frame.description}</div>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {selectedFrame !== 'none' && (
                    <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">{frameStyles[selectedFrame].preview}</span>
                        <div>
                          <div className="font-medium text-sm text-purple-800">
                            Marco seleccionado: {frameStyles[selectedFrame].name}
                          </div>
                          <div className="text-xs text-purple-600">
                            {frameStyles[selectedFrame].description}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedFrame('none')}
                        className="text-xs text-purple-600 hover:text-purple-800 underline"
                      >
                        Quitar marco
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Botones de acción FIJOS en la parte inferior */}
          <div className="flex gap-2 p-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
               Cancelar
            </button>
            <button
              onClick={saveImage}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all font-bold shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <Download className="w-4 h-4 inline mr-2" />
               Guardar Imagen
            </button>
          </div>
        </div>
          
          {/* Canvas de preview */}
          <div className="flex-1 flex items-center justify-center bg-gray-100 p-8">
            <div className="bg-white p-4 rounded-lg shadow-lg">
              <canvas
                ref={canvasRef}
                className="max-w-full max-h-full rounded-lg shadow-sm border border-gray-200"
                style={{ 
                  maxWidth: '600px', 
                  maxHeight: '600px',
                  width: 'auto',
                  height: 'auto',
                  objectFit: 'contain',
                  cursor: (hoveredTextId || hoveredElementId) ? 'move' : (isDragging ? 'grabbing' : (cropMode ? 'crosshair' : 'grab'))
                }}
                onMouseDown={handleCanvasMouseDown}
                onMouseMove={handleCanvasMouseMove}
                onMouseUp={handleCanvasMouseUp}
                onMouseLeave={handleCanvasMouseUp}
                onTouchStart={handleCanvasMouseDown}
                onTouchMove={handleCanvasMouseMove}
                onTouchEnd={handleCanvasMouseUp}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ImageEditor;