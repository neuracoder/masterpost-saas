"use client"

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import {
  X,
  Undo2,
  Redo2,
  RotateCcw,
  Download,
  Eraser,
  PaintBucket,
  ZoomIn,
  ZoomOut,
  Move,
  Save,
  Eye,
  EyeOff
} from 'lucide-react';

const ImageEditor = ({ imageUrl, onSave, onClose }) => {
  // State management
  const [sessionId, setSessionId] = useState(null);
  const [tool, setTool] = useState('erase'); // 'erase' | 'restore'
  const [brushSize, setBrushSize] = useState(15);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [previewUrl, setPreviewUrl] = useState('');
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);
  const [coordinates, setCoordinates] = useState([]);

  // Refs
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const imageRef = useRef(null);

  // Initialize editor session
  useEffect(() => {
    if (imageUrl) {
      initializeEditor();
    }
  }, [imageUrl]);

  const initializeEditor = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('/api/v1/editor/init', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_path: imageUrl
        })
      });

      if (!response.ok) {
        throw new Error('Failed to initialize editor');
      }

      const data = await response.json();

      setSessionId(data.session_id);
      setPreviewUrl(data.preview_url + `?t=${Date.now()}`);
      setImageSize({ width: data.width, height: data.height });
      setCanUndo(data.can_undo);
      setCanRedo(data.can_redo);

    } catch (err) {
      console.error('Editor initialization error:', err);
      setError('Failed to initialize image editor');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle mouse events for drawing
  const getMousePos = useCallback((e) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = imageSize.width / rect.width;
    const scaleY = imageSize.height / rect.height;

    return {
      x: Math.round((e.clientX - rect.left) * scaleX),
      y: Math.round((e.clientY - rect.top) * scaleY)
    };
  }, [imageSize]);

  const startDrawing = useCallback((e) => {
    if (tool === 'pan') {
      setIsPanning(true);
      return;
    }

    setIsDrawing(true);
    const pos = getMousePos(e);
    setCoordinates([pos]);
  }, [tool, getMousePos]);

  const draw = useCallback((e) => {
    if (isPanning) {
      // Handle panning
      return;
    }

    if (!isDrawing) return;

    const pos = getMousePos(e);
    setCoordinates(prev => [...prev, pos]);
  }, [isDrawing, isPanning, getMousePos]);

  const stopDrawing = useCallback(async () => {
    if (isPanning) {
      setIsPanning(false);
      return;
    }

    if (!isDrawing || coordinates.length === 0) return;

    setIsDrawing(false);

    try {
      const response = await fetch('/api/v1/editor/brush-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action: tool,
          coordinates: coordinates,
          brush_size: brushSize
        })
      });

      if (!response.ok) {
        throw new Error('Failed to apply brush action');
      }

      const data = await response.json();
      setPreviewUrl(data.preview_url + `?t=${Date.now()}`);
      setCanUndo(data.can_undo);
      setCanRedo(data.can_redo);

    } catch (err) {
      console.error('Brush action error:', err);
      setError('Failed to apply brush action');
    }

    setCoordinates([]);
  }, [isDrawing, isPanning, coordinates, sessionId, tool, brushSize]);

  // Undo/Redo actions
  const handleUndo = async () => {
    if (!sessionId || !canUndo) return;

    try {
      const response = await fetch('/api/v1/editor/undo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to undo');
      }

      const data = await response.json();
      setPreviewUrl(data.preview_url + `?t=${Date.now()}`);
      setCanUndo(data.can_undo);
      setCanRedo(data.can_redo);

    } catch (err) {
      console.error('Undo error:', err);
      setError('Failed to undo action');
    }
  };

  const handleRedo = async () => {
    if (!sessionId || !canRedo) return;

    try {
      const response = await fetch('/api/v1/editor/redo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to redo');
      }

      const data = await response.json();
      setPreviewUrl(data.preview_url + `?t=${Date.now()}`);
      setCanUndo(data.can_undo);
      setCanRedo(data.can_redo);

    } catch (err) {
      console.error('Redo error:', err);
      setError('Failed to redo action');
    }
  };

  const handleReset = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch('/api/v1/editor/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to reset');
      }

      const data = await response.json();
      setPreviewUrl(data.preview_url + `?t=${Date.now()}`);
      setCanUndo(data.can_undo);
      setCanRedo(data.can_redo);

    } catch (err) {
      console.error('Reset error:', err);
      setError('Failed to reset image');
    }
  };

  const handleSave = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch('/api/v1/editor/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save');
      }

      const data = await response.json();

      // Call onSave callback with the saved image URL
      if (onSave) {
        onSave(data.download_url);
      }

      // Clean up session
      await cleanupSession();

      // Close editor
      onClose();

    } catch (err) {
      console.error('Save error:', err);
      setError('Failed to save edited image');
    }
  };

  const cleanupSession = async () => {
    if (!sessionId) return;

    try {
      await fetch(`/api/v1/editor/session/${sessionId}`, {
        method: 'DELETE'
      });
    } catch (err) {
      console.error('Cleanup error:', err);
    }
  };

  const handleClose = async () => {
    await cleanupSession();
    onClose();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sessionId) {
        cleanupSession();
      }
    };
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center">
        <Card className="w-80">
          <CardContent className="p-6 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p>Loading image editor...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <h3 className="text-lg font-semibold text-red-600 mb-4">Error</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={handleClose} className="bg-gray-500 hover:bg-gray-600">
              Close
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex">
      {/* Sidebar */}
      <div className="w-80 bg-white shadow-xl overflow-y-auto">
        <CardHeader className="border-b">
          <CardTitle className="flex items-center justify-between">
            <span>Image Editor</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardTitle>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Tools */}
          <div>
            <h3 className="font-semibold mb-3">Tools</h3>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={tool === 'erase' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTool('erase')}
                className={tool === 'erase' ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
              >
                <Eraser className="w-4 h-4 mr-2" />
                Erase
              </Button>
              <Button
                variant={tool === 'restore' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTool('restore')}
                className={tool === 'restore' ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
              >
                <PaintBucket className="w-4 h-4 mr-2" />
                Restore
              </Button>
            </div>
          </div>

          {/* Brush Size */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Brush Size</span>
              <Badge variant="outline">{brushSize}px</Badge>
            </div>
            <Slider
              value={[brushSize]}
              onValueChange={(value) => setBrushSize(value[0])}
              min={5}
              max={50}
              step={1}
              className="w-full"
            />
          </div>

          {/* Actions */}
          <div>
            <h3 className="font-semibold mb-3">Actions</h3>
            <div className="space-y-2">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleUndo}
                  disabled={!canUndo}
                  className="flex-1"
                >
                  <Undo2 className="w-4 h-4 mr-2" />
                  Undo
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRedo}
                  disabled={!canRedo}
                  className="flex-1"
                >
                  <Redo2 className="w-4 h-4 mr-2" />
                  Redo
                </Button>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="w-full"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset to Original
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowOriginal(!showOriginal)}
                className="w-full"
              >
                {showOriginal ? (
                  <><EyeOff className="w-4 h-4 mr-2" />Hide Original</>
                ) : (
                  <><Eye className="w-4 h-4 mr-2" />Show Original</>
                )}
              </Button>
            </div>
          </div>

          {/* Zoom Controls */}
          <div>
            <h3 className="font-semibold mb-3">Zoom</h3>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setZoom(Math.max(0.1, zoom - 0.1))}
              >
                <ZoomOut className="w-4 h-4" />
              </Button>
              <span className="text-sm flex-1 text-center">
                {Math.round(zoom * 100)}%
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setZoom(Math.min(3, zoom + 0.1))}
              >
                <ZoomIn className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>

        {/* Footer Actions */}
        <div className="p-6 border-t space-y-2">
          <Button
            onClick={handleSave}
            className="w-full bg-emerald-600 hover:bg-emerald-700"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
          <Button
            variant="outline"
            onClick={handleClose}
            className="w-full"
          >
            Cancel
          </Button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 relative overflow-hidden bg-gray-100">
        <div
          ref={containerRef}
          className="w-full h-full flex items-center justify-center"
          style={{
            cursor: tool === 'erase' ? 'crosshair' : tool === 'restore' ? 'copy' : 'grab'
          }}
        >
          {previewUrl && (
            <div
              className="relative"
              style={{
                transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)`
              }}
            >
              <canvas
                ref={canvasRef}
                className="border border-gray-300 shadow-lg"
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                style={{
                  maxWidth: '80vw',
                  maxHeight: '80vh',
                  display: showOriginal ? 'none' : 'block'
                }}
              />

              {/* Preview Image */}
              <img
                ref={imageRef}
                src={showOriginal ? imageUrl : previewUrl}
                alt="Edit preview"
                className="border border-gray-300 shadow-lg"
                style={{
                  maxWidth: '80vw',
                  maxHeight: '80vh',
                  display: showOriginal ? 'block' : 'none'
                }}
                onLoad={() => {
                  if (canvasRef.current && imageRef.current) {
                    const canvas = canvasRef.current;
                    const img = imageRef.current;
                    canvas.width = img.clientWidth;
                    canvas.height = img.clientHeight;
                  }
                }}
              />

              {/* Canvas overlay for drawing preview */}
              {!showOriginal && previewUrl && (
                <img
                  src={previewUrl}
                  alt="Edit preview"
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    width: '100%',
                    height: '100%'
                  }}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageEditor;