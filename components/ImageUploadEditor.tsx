"use client"

import React, { useCallback, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Upload, ImageIcon, FileImage, AlertCircle } from 'lucide-react';

interface ImageData {
  localUrl: string;
  serverPath: string;
  filename: string;
  jobId: string;
}

interface ImageUploadEditorProps {
  onImageSelected: (imageData: ImageData) => void;
}

const ImageUploadEditor: React.FC<ImageUploadEditorProps> = ({ onImageSelected }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const validateFile = (file: File): boolean => {
    // Check file type
    if (!file.type.startsWith('image/')) {
      setError('Por favor selecciona un archivo de imagen válido');
      return false;
    }

    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError('El archivo es demasiado grande. Máximo 50MB permitido');
      return false;
    }

    return true;
  };

  const handleFileSelect = useCallback(async (files: FileList) => {
    if (files.length === 0) return;

    const file = files[0];
    console.log('📁 Archivo seleccionado:', file.name, file.type, file.size);
    setError(null);

    if (!validateFile(file)) {
      console.log('❌ Validación fallida');
      return;
    }

    console.log('📤 Iniciando upload...');
    setIsUploading(true);

    try {
      // Create local URL for immediate preview
      const localUrl = URL.createObjectURL(file);
      console.log('🖼️ URL local creada:', localUrl);

      // Upload to server
      const formData = new FormData();
      formData.append('file', file);

      console.log('📤 Enviando a servidor...');
      const response = await fetch('/api/v1/manual-editor/upload-single', {
        method: 'POST',
        body: formData
      });

      console.log('📥 Respuesta del servidor:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error en respuesta:', errorText);
        throw new Error(`Error al subir la imagen: ${response.status}`);
      }

      const result = await response.json();
      console.log('🚀 Resultado del upload:', result);

      // ESTRUCTURA DE DATOS CORRECTA PARA EL CANVAS
      const imageData = {
        localUrl: localUrl,          // URL blob local para canvas
        serverPath: result.file_path, // Ruta en servidor
        filename: file.name,         // Nombre original del archivo
        jobId: result.job_id || result.session_id, // ID de sesión
        sessionId: result.job_id || result.session_id, // Compatibilidad
        originalFile: file           // Archivo original por si acaso
      };

      console.log('📊 Enviando datos al componente padre:', imageData);
      console.log('🔍 Verificando estructura:', {
        hasLocalUrl: !!imageData.localUrl,
        hasFilename: !!imageData.filename,
        hasSessionId: !!imageData.sessionId,
        localUrlType: typeof imageData.localUrl,
        localUrlValue: imageData.localUrl
      });
      onImageSelected(imageData);
      console.log('🏁 Upload completamente terminado');

    } catch (error) {
      console.error('❌ Error uploading image:', error);
      setError(`Error al subir la imagen: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      console.log('🏁 Upload terminado');
      setIsUploading(false);
    }
  }, [onImageSelected]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  }, [handleFileSelect]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  }, [handleFileSelect]);

  const openFileDialog = () => {
    const input = document.getElementById('editor-file-input') as HTMLInputElement;
    if (input) {
      input.click();
    }
  };

  return (
    <div className="w-full">
      {/* Upload Zone */}
      <div
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${dragActive
            ? 'border-purple-400 bg-purple-50'
            : 'border-gray-300 hover:border-purple-300 hover:bg-purple-50/30'
          }
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          id="editor-file-input"
          type="file"
          accept="image/*"
          onChange={handleInputChange}
          className="hidden"
          disabled={isUploading}
        />

        <div className="flex flex-col items-center space-y-4">
          {isUploading ? (
            <>
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                <div className="animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full"></div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-purple-900">Subiendo imagen...</h3>
                <p className="text-purple-600">Por favor espera un momento</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                <ImageIcon className="w-8 h-8 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Arrastra tu imagen aquí o haz click para seleccionar
                </h3>
                <p className="text-gray-600 mt-2">
                  Acepta archivos JPG, PNG, WEBP hasta 50MB
                </p>
              </div>
              <Button
                type="button"
                className="bg-purple-600 hover:bg-purple-700"
                disabled={isUploading}
              >
                <Upload className="w-4 h-4 mr-2" />
                Seleccionar Imagen
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="mt-4 border-red-200 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-2 text-red-700">
              <AlertCircle className="w-4 h-4" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Tips */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-blue-200 bg-blue-50/30">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileImage className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <h4 className="font-medium text-blue-900">Formatos Soportados</h4>
                <p className="text-xs text-blue-700">JPG, PNG, WEBP</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-200 bg-green-50/30">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <Badge className="w-4 h-4 bg-green-600" />
              </div>
              <div>
                <h4 className="font-medium text-green-900">Tamaño Máximo</h4>
                <p className="text-xs text-green-700">Hasta 50MB por imagen</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-purple-200 bg-purple-50/30">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Upload className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium text-purple-900">Mejores Resultados</h4>
                <p className="text-xs text-purple-700">Imágenes de alta calidad</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ImageUploadEditor;