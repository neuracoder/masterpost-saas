"use client"

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import {
  Eraser,
  Paintbrush2,
  Undo2,
  Redo2,
  RotateCcw,
  Settings,
  Palette
} from 'lucide-react';

interface EditorToolbarProps {
  tool: 'erase' | 'restore';
  setTool: (tool: 'erase' | 'restore') => void;
  brushSize: number;
  setBrushSize: (size: number) => void;
  onUndo: () => void;
  onRedo: () => void;
  onReset: () => void;
  canUndo: boolean;
  canRedo: boolean;
  hasChanges: boolean;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({
  tool,
  setTool,
  brushSize,
  setBrushSize,
  onUndo,
  onRedo,
  onReset,
  canUndo,
  canRedo,
  hasChanges
}) => {
  return (
    <div className="space-y-4">
      {/* Tools Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <Settings className="w-4 h-4 mr-2" />
            Herramientas
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2">
            <Button
              variant={tool === 'erase' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTool('erase')}
              className={`flex items-center justify-start w-full ${
                tool === 'erase'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'hover:bg-red-50 hover:text-red-700 hover:border-red-200'
              }`}
            >
              <Eraser className="w-4 h-4 mr-2" />
              Borrar Fondo
            </Button>

            <Button
              variant={tool === 'restore' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTool('restore')}
              className={`flex items-center justify-start w-full ${
                tool === 'restore'
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200'
              }`}
            >
              <Paintbrush2 className="w-4 h-4 mr-2" />
              Pincel Normal
            </Button>
          </div>

          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
            <strong>Borrar Fondo:</strong> Elimina partes de la imagen (fondo)<br />
            <strong>Pincel Normal:</strong> Pinta con color para restaurar
          </div>
        </CardContent>
      </Card>

      {/* Brush Size Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center justify-between">
            <div className="flex items-center">
              <Palette className="w-4 h-4 mr-2" />
              Tamaño del Pincel
            </div>
            <Badge variant="outline" className="text-xs">
              {brushSize}px
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Slider
            value={[brushSize]}
            onValueChange={(value) => setBrushSize(value[0])}
            min={5}
            max={100}
            step={1}
            className="w-full"
          />

          <div className="flex justify-between text-xs text-gray-500">
            <span>5px</span>
            <span>Precisión</span>
            <span>100px</span>
          </div>

          {/* Brush size presets */}
          <div className="grid grid-cols-3 gap-2">
            {[10, 25, 50].map((size) => (
              <Button
                key={size}
                variant="outline"
                size="sm"
                onClick={() => setBrushSize(size)}
                className={`text-xs ${brushSize === size ? 'bg-purple-50 border-purple-200' : ''}`}
              >
                {size}px
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <RotateCcw className="w-4 h-4 mr-2" />
            Acciones
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onUndo}
              disabled={!canUndo}
              className="flex items-center justify-center"
            >
              <Undo2 className="w-4 h-4 mr-1" />
              Deshacer
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={onRedo}
              disabled={!canRedo}
              className="flex items-center justify-center"
            >
              <Redo2 className="w-4 h-4 mr-1" />
              Rehacer
            </Button>
          </div>

          <Separator />

          <Button
            variant="outline"
            size="sm"
            onClick={onReset}
            disabled={!hasChanges}
            className="w-full flex items-center justify-center hover:bg-yellow-50 hover:border-yellow-200"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reiniciar Imagen
          </Button>

          {hasChanges && (
            <div className="text-xs text-orange-600 bg-orange-50 p-2 rounded border border-orange-200">
              ⚠️ Tienes cambios sin guardar
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card className="bg-purple-50/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-purple-900">💡 Consejos</CardTitle>
        </CardHeader>
        <CardContent className="text-xs text-purple-800 space-y-2">
          <div className="flex items-start space-x-2">
            <span className="font-semibold">🧽</span>
            <span>Usa <strong>Borrar Fondo</strong> para eliminar partes no deseadas del fondo</span>
          </div>

          <div className="flex items-start space-x-2">
            <span className="font-semibold">🖌️</span>
            <span>Usa <strong>Pincel Normal</strong> para restaurar partes del producto</span>
          </div>

          <div className="flex items-start space-x-2">
            <span className="font-semibold">🎯</span>
            <span>Reduce el tamaño del pincel para trabajo de precisión</span>
          </div>

          <div className="flex items-start space-x-2">
            <span className="font-semibold">↩️</span>
            <span>Usa Deshacer/Rehacer si cometes un error</span>
          </div>
        </CardContent>
      </Card>

      {/* Current Tool Status */}
      <Card className="border-2 border-dashed border-gray-200">
        <CardContent className="pt-4">
          <div className="text-center">
            <div className={`w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center ${
              tool === 'erase'
                ? 'bg-red-100'
                : 'bg-blue-100'
            }`}>
              {tool === 'erase' ? (
                <Eraser className="w-6 h-6 text-red-600" />
              ) : (
                <Paintbrush2 className="w-6 h-6 text-blue-600" />
              )}
            </div>
            <div className="text-sm font-medium">
              {tool === 'erase' ? 'Borrar Fondo' : 'Pincel Normal'}
            </div>
            <div className="text-xs text-gray-500">
              Tamaño: {brushSize}px
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EditorToolbar;