"use client"

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, ArrowLeft, Paintbrush2, Eraser, User, CreditCard } from 'lucide-react';
import Link from 'next/link';
import ImageUploadEditor from '@/components/ImageUploadEditor';
import EditorCanvas from '@/components/EditorCanvas';

interface ImageData {
  localUrl: string;
  serverPath: string;
  filename: string;
  jobId: string;
}

export default function ManualEditorPage() {
  const [currentImage, setCurrentImage] = useState<ImageData | null>(null);
  const [editedImageUrl, setEditedImageUrl] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>('Inicializado');

  const handleImageSelected = (imageData: ImageData) => {
    console.log('🔍 handleImageSelected called with:', imageData);
    console.log('🔍 imageData structure:', {
      hasLocalUrl: !!imageData?.localUrl,
      hasFilename: !!imageData?.filename,
      hasJobId: !!imageData?.jobId,
      localUrlType: typeof imageData?.localUrl,
      localUrlValue: imageData?.localUrl
    });

    setDebugInfo(`Imagen seleccionada: ${imageData.filename}`);
    setCurrentImage(imageData);
    setIsEditing(false);
    setEditedImageUrl(null);

    console.log('✅ Estado actualizado, currentImage ahora es:', imageData);
  };

  const handleStartEditing = () => {
    setIsEditing(true);
  };

  const handleImageEdited = (downloadUrl: string) => {
    setEditedImageUrl(downloadUrl);
    setIsEditing(false);
  };

  const handleNewImage = () => {
    setCurrentImage(null);
    setEditedImageUrl(null);
    setIsEditing(false);
  };

  const handleDownloadEdited = () => {
    if (editedImageUrl) {
      const link = document.createElement('a');
      link.href = editedImageUrl;
      link.download = `edited_${currentImage?.filename || 'image.png'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/app" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
              <Upload className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Masterpost.io</span>
          </Link>

          <div className="flex items-center space-x-4">
            <Link href="/app">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver al Procesador
              </Button>
            </Link>
            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">
              <CreditCard className="w-3 h-3 mr-1" />
              485 credits remaining
            </Badge>
            <Button variant="ghost" size="sm">
              <User className="w-4 h-4 mr-2" />
              Account
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Page Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mr-4">
              <Paintbrush2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Editor Manual de Fondo</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Sube una imagen y edítala manualmente para perfeccionar la eliminación de fondo con precision
          </p>
          <div className="flex items-center justify-center mt-4 space-x-4">
            <Badge variant="outline" className="text-purple-700 border-purple-200">
              <Eraser className="w-3 h-3 mr-1" />
              Herramientas de Borrado
            </Badge>
            <Badge variant="outline" className="text-purple-700 border-purple-200">
              <Paintbrush2 className="w-3 h-3 mr-1" />
              Pincel de Restauración
            </Badge>
          </div>
        </div>

        {/* Debug Info */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm font-mono text-blue-800">
            🐛 Debug: {debugInfo}
          </div>
          <div className="text-xs text-blue-600 mt-2">
            📊 Estado: isEditing={isEditing.toString()}, editedImageUrl={editedImageUrl ? 'exists' : 'null'}, hasCurrentImage={!!currentImage ? 'SÍ' : 'NO'}
          </div>
          {currentImage && (
            <div className="text-xs text-blue-500 mt-1">
              🔗 currentImage.localUrl: {currentImage.localUrl}<br/>
              📝 currentImage.filename: {currentImage.filename}
            </div>
          )}
        </div>

        {/* Main Content */}
        {!currentImage ? (
          /* Upload Section */
          <div className="max-w-2xl mx-auto">
            <Card className="border-2 border-dashed border-purple-200 bg-purple-50/30">
              <CardHeader className="text-center">
                <CardTitle className="text-purple-900 flex items-center justify-center">
                  <Upload className="w-5 h-5 mr-2" />
                  Selecciona una Imagen para Editar
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ImageUploadEditor onImageSelected={handleImageSelected} />
              </CardContent>
            </Card>

            {/* Instructions */}
            <div className="mt-8 grid md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2">1. Sube tu Imagen</h3>
                  <p className="text-sm text-gray-600">
                    Selecciona una imagen con fondo que necesite edición manual
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Paintbrush2 className="w-6 h-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-2">2. Edita Manualmente</h3>
                  <p className="text-sm text-gray-600">
                    Usa las herramientas de borrado y restauración para perfeccionar
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6 text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2">3. Descarga Resultado</h3>
                  <p className="text-sm text-gray-600">
                    Guarda tu imagen editada con fondo perfectamente removido
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          /* Editor Section */
          <div className="space-y-6">
            {/* Image Info Header */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Paintbrush2 className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Editando: {currentImage.filename}</h3>
                      <p className="text-sm text-gray-500">
                        {isEditing ? 'Modo edición activo' : editedImageUrl ? 'Imagen editada lista' : 'Lista para editar'}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    {editedImageUrl && !isEditing && (
                      <Button
                        onClick={handleDownloadEdited}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        Descargar Editada
                      </Button>
                    )}
                    <Button
                      onClick={handleNewImage}
                      variant="outline"
                    >
                      Nueva Imagen
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Editor Interface */}
            {!isEditing && !editedImageUrl ? (
              /* Preview and Start Editing */
              <Card>
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center space-y-6">
                    <div className="max-w-md">
                      <img
                        src={currentImage.localUrl}
                        alt={currentImage.filename}
                        className="w-full h-auto border-2 border-gray-200 rounded-lg shadow-lg"
                      />
                    </div>
                    <Button
                      onClick={handleStartEditing}
                      size="lg"
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      <Paintbrush2 className="w-5 h-5 mr-2" />
                      Comenzar Edición Manual
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : isEditing ? (
              /* Active Editor */
              <EditorCanvas
                imageData={currentImage}
                onImageEdited={handleImageEdited}
                onCancel={() => setIsEditing(false)}
              />
            ) : (
              /* Results */
              <Card>
                <CardHeader>
                  <CardTitle className="text-green-900">✅ Edición Completada</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-2">Imagen Original</h4>
                      <img
                        src={currentImage.localUrl}
                        alt="Original"
                        className="w-full h-auto border-2 border-gray-200 rounded-lg"
                      />
                    </div>
                    {editedImageUrl && (
                      <div>
                        <h4 className="font-medium mb-2">Imagen Editada</h4>
                        <img
                          src={editedImageUrl}
                          alt="Editada"
                          className="w-full h-auto border-2 border-green-200 rounded-lg"
                        />
                      </div>
                    )}
                  </div>
                  <div className="mt-6 flex justify-center space-x-4">
                    <Button
                      onClick={handleDownloadEdited}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      Descargar Imagen Editada
                    </Button>
                    <Button
                      onClick={() => setIsEditing(true)}
                      variant="outline"
                    >
                      Continuar Editando
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}