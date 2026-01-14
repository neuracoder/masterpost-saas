# Instrucciones para Cambiar entre Entornos

## Usando la Interfaz Gráfica

1. Asegúrate de tener Python instalado en tu sistema
2. Abre una terminal en la carpeta raíz del proyecto
3. Ejecuta el script del selector de entorno:
   ```powershell
   python environment_switcher.py
   ```
4. En la ventana que aparece, simplemente haz clic en:
   - Botón "LOCAL" para configurar el entorno de desarrollo local
   - Botón "PRODUCCIÓN" para configurar el entorno de producción
5. Después de cambiar el entorno, asegúrate de:
   - Reiniciar el servidor de desarrollo si está en ejecución
   - Reiniciar el frontend de Next.js si está en ejecución

## Notas Importantes

- La herramienta creará automáticamente un backup del archivo `.env` actual antes de hacer cualquier cambio
- El backup se guardará como `.env.backup`
- Si ocurre algún error, se mostrará un mensaje explicativo
- Asegúrate de tener los archivos `.env.development` y `.env.production` en la carpeta raíz del proyecto

## Requisitos

- Python 3.6 o superior
- tkinter (viene incluido con la mayoría de las instalaciones de Python)