"""
Masterpost.io Logging System
Complete logging configuration for debugging image processing
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure comprehensive logging system"""

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler for detailed logs - DISABLED TO PREVENT LOOP
    # file_handler = logging.FileHandler(logs_dir / 'app.log', encoding='utf-8')
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(detailed_formatter)

    # File handler for errors only - DISABLED TO PREVENT LOOP
    # error_handler = logging.FileHandler(logs_dir / 'errors.log', encoding='utf-8')
    # error_handler.setLevel(logging.ERROR)
    # error_handler.setFormatter(detailed_formatter)

    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Reduced from DEBUG to prevent spam
    console_handler.setFormatter(simple_formatter)

    # Add handlers - ONLY CONSOLE TO PREVENT LOOP
    # root_logger.addHandler(file_handler)  # DISABLED
    # root_logger.addHandler(error_handler)  # DISABLED
    root_logger.addHandler(console_handler)

    # Create specialized loggers with detailed configuration
    processing_logger = logging.getLogger('processing')
    processing_logger.setLevel(logging.DEBUG)

    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.DEBUG)

    qwen_logger = logging.getLogger('qwen')
    qwen_logger.setLevel(logging.DEBUG)

    # Log initial setup
    root_logger.info("🚀 SISTEMA DE LOGGING CONFIGURADO")
    root_logger.info(f"   📁 Directorio logs: {logs_dir.absolute()}")
    root_logger.info(f"   📄 Archivo principal: app.log")
    root_logger.info(f"   🔥 Archivo errores: errors.log")
    root_logger.info(f"   🎯 Nivel consola: DEBUG")
    root_logger.info(f"   🎯 Nivel archivo: DEBUG")

    return {
        'main': root_logger,
        'processing': processing_logger,
        'api': api_logger,
        'qwen': qwen_logger
    }

def log_request_start(endpoint: str, params: dict = None):
    """Log the start of a request"""
    logger = logging.getLogger('api')
    separator = "=" * 60
    logger.info(f"\n{separator}")
    logger.info(f"🚀 INICIO REQUEST: {endpoint}")
    if params:
        logger.info(f"📝 Parámetros: {params}")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info(f"{separator}")

def log_request_end(endpoint: str, success: bool = True, error: str = None):
    """Log the end of a request"""
    logger = logging.getLogger('api')
    separator = "=" * 60
    status = "✅ ÉXITO" if success else "❌ ERROR"
    logger.info(f"\n{separator}")
    logger.info(f"{status} - FIN REQUEST: {endpoint}")
    if error:
        logger.error(f"💥 Error: {error}")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info(f"{separator}\n")

def log_file_info(filename: str, size: int, file_type: str = None):
    """Log information about a file being processed"""
    logger = logging.getLogger('processing')
    size_mb = size / (1024 * 1024)
    logger.info(f"📁 Archivo: {filename}")
    logger.info(f"   📏 Tamaño: {size:,} bytes ({size_mb:.2f} MB)")
    if file_type:
        logger.info(f"   🎨 Tipo: {file_type}")

def log_qwen_api_call(url: str, payload_size: int, has_api_key: bool):
    """Log Qwen API call details"""
    logger = logging.getLogger('qwen')
    logger.info(f"🔮 LLAMADA QWEN API")
    logger.info(f"   🌐 URL: {url}")
    logger.info(f"   📦 Payload: {payload_size} bytes")
    logger.info(f"   🔑 API Key: {'✅ Configurada' if has_api_key else '❌ NO configurada'}")

def log_qwen_response(status_code: int, response_time: float, success: bool):
    """Log Qwen API response"""
    logger = logging.getLogger('qwen')
    status = "✅ ÉXITO" if success else "❌ ERROR"
    logger.info(f"📡 RESPUESTA QWEN API - {status}")
    logger.info(f"   📊 Status Code: {status_code}")
    logger.info(f"   ⏱️ Tiempo: {response_time:.2f}s")

def log_processing_step(step: str, details: str = None):
    """Log a processing step"""
    logger = logging.getLogger('processing')
    logger.info(f"⚙️ PROCESAMIENTO: {step}")
    if details:
        logger.info(f"   📋 Detalles: {details}")

def log_zip_creation(file_count: int, total_size: int, zip_path: str):
    """Log ZIP file creation"""
    logger = logging.getLogger('processing')
    size_mb = total_size / (1024 * 1024)
    logger.info(f"📦 CREANDO ZIP")
    logger.info(f"   📁 Archivos: {file_count}")
    logger.info(f"   📏 Tamaño total: {total_size:,} bytes ({size_mb:.2f} MB)")
    logger.info(f"   💾 Ubicación: {zip_path}")

# Initialize logging when module is imported - REMOVED TO PREVENT LOOP
# loggers = setup_logging()  # Call manually from server.py only