#!/usr/bin/env python3
"""
Sistema de Logs Avanzado para Masterpost.io
Logging avanzado con exportación de resúmenes y middleware HTTP
"""

import logging
import json
import time
import traceback
import psutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import wraps
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AdvancedLogger:
    """Sistema de logging avanzado con capacidades de exportación"""

    def __init__(self, log_dir: str = "logs_advanced"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # ID único de sesión
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now(timezone.utc)

        # Contadores
        self.request_count = 0
        self.error_count = 0
        self.api_calls = {}

        # Archivos de log
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.main_log = self.log_dir / f"masterpost_{timestamp}_{self.session_id}.log"
        self.error_log = self.log_dir / f"errors_{timestamp}_{self.session_id}.log"
        self.metrics_log = self.log_dir / f"metrics_{timestamp}_{self.session_id}.json"

        # Configurar loggers
        self._setup_loggers()

        # Log inicial
        self.log_info("🚀 Sistema de logs avanzado iniciado", {
            "session_id": self.session_id,
            "log_dir": str(self.log_dir),
            "timestamp": self.start_time.isoformat()
        })

    def _setup_loggers(self):
        """Configurar loggers principales"""

        # Logger principal
        self.main_logger = logging.getLogger(f"masterpost_main_{self.session_id}")
        self.main_logger.setLevel(logging.INFO)

        # Handler para archivo principal
        main_handler = logging.FileHandler(self.main_log, encoding='utf-8')
        main_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        main_handler.setFormatter(main_formatter)
        self.main_logger.addHandler(main_handler)

        # Logger de errores
        self.error_logger = logging.getLogger(f"masterpost_error_{self.session_id}")
        self.error_logger.setLevel(logging.ERROR)

        # Handler para errores
        error_handler = logging.FileHandler(self.error_log, encoding='utf-8')
        error_formatter = logging.Formatter(
            '%(asctime)s | ERROR | %(message)s\n%(exc_info)s\n' + '='*80 + '\n'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)

    def log_info(self, message: str, data: Optional[Dict] = None):
        """Log de información con datos opcionales"""
        log_entry = {
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": self.session_id
        }
        if data:
            log_entry.update(data)

        formatted_msg = f"{message}"
        if data:
            formatted_msg += f" | Data: {json.dumps(data, default=str)}"

        self.main_logger.info(formatted_msg)

    def log_error(self, message: str, error: Exception, context: Optional[Dict] = None):
        """Log de errores con stack trace completo"""
        self.error_count += 1

        error_data = {
            "message": message,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": self.session_id,
            "error_count": self.error_count,
            "traceback": traceback.format_exc()
        }

        if context:
            error_data["context"] = context

        # Log al archivo de errores
        self.error_logger.error(f"{message}: {error}", exc_info=True)

        # Log también al principal
        self.log_info(f"❌ ERROR: {message}", {
            "error_type": type(error).__name__,
            "error_message": str(error)
        })

    def log_http_request(self, method: str, url: str, status_code: int,
                        response_time: float, client_ip: str = "unknown",
                        response_content: Optional[str] = None,
                        response_headers: Optional[Dict] = None):
        """Log de peticiones HTTP con contenido de respuesta"""
        self.request_count += 1

        log_data = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "client_ip": client_ip,
            "request_number": self.request_count
        }

        # Analizar contenido de respuesta si está disponible
        if response_content is not None:
            content_analysis = self._analyze_response_content(response_content)
            log_data.update(content_analysis)

        # Agregar headers de respuesta
        if response_headers:
            log_data["response_headers"] = response_headers

        self.log_info(f"🌐 {method} {url} → {status_code}", log_data)

    def log_api_call(self, api_name: str, success: bool, response_time: float,
                    details: Optional[Dict] = None):
        """Log de llamadas a APIs externas"""
        if api_name not in self.api_calls:
            self.api_calls[api_name] = {"total": 0, "success": 0, "errors": 0}

        self.api_calls[api_name]["total"] += 1
        if success:
            self.api_calls[api_name]["success"] += 1
        else:
            self.api_calls[api_name]["errors"] += 1

        status = "✅" if success else "❌"
        self.log_info(f"{status} API Call: {api_name}", {
            "api": api_name,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "total_calls": self.api_calls[api_name]["total"],
            "details": details
        })

    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": f"Could not get system metrics: {str(e)}"}

    def export_summary(self) -> str:
        """Exportar resumen completo de logs"""
        try:
            summary_file = self.log_dir / f"summary_{self.session_id}_{int(time.time())}.txt"

            # Métricas actuales
            uptime = datetime.now(timezone.utc) - self.start_time
            system_metrics = self.get_system_metrics()

            summary_content = f"""
MASTERPOST.IO - RESUMEN DE LOGS
===============================
Sesión ID: {self.session_id}
Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
Tiempo activo: {str(uptime).split('.')[0]}

ESTADÍSTICAS HTTP
-----------------
Total peticiones: {self.request_count}
Errores totales: {self.error_count}
Tasa de error: {(self.error_count/max(self.request_count,1)*100):.2f}%

LLAMADAS API EXTERNAS
--------------------
"""

            for api_name, stats in self.api_calls.items():
                success_rate = (stats["success"] / max(stats["total"], 1)) * 100
                summary_content += f"{api_name}: {stats['total']} llamadas, {success_rate:.1f}% éxito\n"

            if not self.api_calls:
                summary_content += "No hay llamadas API registradas\n"

            summary_content += f"""
MÉTRICAS DEL SISTEMA
-------------------
CPU: {system_metrics.get('cpu_percent', 'N/A')}%
Memoria: {system_metrics.get('memory_percent', 'N/A')}% usada
Memoria libre: {system_metrics.get('memory_available_gb', 'N/A')} GB
Disco: {system_metrics.get('disk_percent', 'N/A')}% usado
Disco libre: {system_metrics.get('disk_free_gb', 'N/A')} GB

ARCHIVOS DE LOG
---------------
Principal: {self.main_log.name}
Errores: {self.error_log.name}
Métricas: {self.metrics_log.name}

UBICACIÓN: {self.log_dir}

===============================
Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            self.log_info("📄 Resumen de logs exportado", {
                "summary_file": str(summary_file),
                "total_requests": self.request_count,
                "total_errors": self.error_count
            })

            return str(summary_file)

        except Exception as e:
            self.log_error("Error exportando resumen", e)
            raise

    def _analyze_response_content(self, content: str) -> Dict[str, Any]:
        """Analizar contenido de respuesta para detectar tipo y problemas"""
        analysis = {
            "content_length": len(content),
            "content_preview": content[:500] if content else "",
            "content_type_detected": "unknown"
        }

        if not content:
            analysis["content_type_detected"] = "empty"
            analysis["content_issue"] = "Response is empty"
            return analysis

        # Detectar si es JSON válido
        try:
            parsed_json = json.loads(content)
            analysis["content_type_detected"] = "json"
            analysis["json_valid"] = True

            # Analizar estructura JSON
            if isinstance(parsed_json, dict):
                analysis["json_keys"] = list(parsed_json.keys())[:10]  # Primeras 10 claves
                if "error" in parsed_json:
                    analysis["contains_error"] = True
                if "success" in parsed_json:
                    analysis["success_value"] = parsed_json["success"]
            elif isinstance(parsed_json, list):
                analysis["json_type"] = "array"
                analysis["json_array_length"] = len(parsed_json)

        except json.JSONDecodeError as e:
            analysis["json_valid"] = False
            analysis["json_error"] = str(e)

            # Detectar si parece datos binarios corruptos
            if any(ord(c) < 32 and c not in '\n\r\t' for c in content[:100]):
                analysis["content_type_detected"] = "binary_corrupt"
                analysis["content_issue"] = "Contains binary/control characters"
            elif content.startswith('<?xml'):
                analysis["content_type_detected"] = "xml"
            elif content.startswith('<html'):
                analysis["content_type_detected"] = "html"
            else:
                analysis["content_type_detected"] = "text"

        return analysis


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging automático de peticiones HTTP con captura de contenido"""

    def __init__(self, app, logger: AdvancedLogger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Información de la petición
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)

        try:
            response = await call_next(request)
            response_time = time.time() - start_time

            # Capturar contenido de respuesta para análisis
            response_content = None
            response_headers = dict(response.headers)

            # Solo capturar contenido para endpoints críticos
            critical_endpoints = ["/api/v1/process", "/api/v1/upload", "/api/test", "/api/logs"]
            is_critical = any(endpoint in url for endpoint in critical_endpoints)

            if is_critical:
                try:
                    # Intentar leer el contenido de la respuesta
                    if hasattr(response, '_content'):
                        response_content = response._content.decode('utf-8')
                    elif hasattr(response, 'body'):
                        response_content = response.body.decode('utf-8')
                except Exception as content_error:
                    response_content = f"ERROR_READING_CONTENT: {str(content_error)}"

            # Log de la petición exitosa con contenido
            self.logger.log_http_request(
                method=method,
                url=url,
                status_code=response.status_code,
                response_time=response_time,
                client_ip=client_ip,
                response_content=response_content,
                response_headers=response_headers
            )

            return response

        except Exception as e:
            response_time = time.time() - start_time

            # Log del error
            self.logger.log_error(f"Error en petición {method} {url}", e, {
                "method": method,
                "url": url,
                "response_time": response_time,
                "client_ip": client_ip
            })

            # Log HTTP con código de error
            self.logger.log_http_request(
                method=method,
                url=url,
                status_code=500,
                response_time=response_time,
                client_ip=client_ip,
                response_content=f"EXCEPTION: {str(e)}"
            )

            raise


def log_errors(logger: AdvancedLogger):
    """Decorador para logging automático de errores en endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.log_error(f"Error en endpoint {func.__name__}", e, {
                    "function": func.__name__,
                    "args": str(args)[:200],  # Limitar tamaño del log
                    "kwargs": str(kwargs)[:200]
                })
                raise
        return wrapper
    return decorator


# Función auxiliar para formatear logs
def format_log_data(data: Any) -> str:
    """Formatear datos para logging legible"""
    if isinstance(data, dict):
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    return str(data)


# Ejemplo de uso
if __name__ == "__main__":
    # Test del sistema de logging
    logger = AdvancedLogger()

    logger.log_info("Test del sistema de logging", {"test": True})

    try:
        raise ValueError("Error de prueba")
    except Exception as e:
        logger.log_error("Error de prueba", e, {"test_context": "demo"})

    logger.log_api_call("test_api", True, 0.5, {"response": "ok"})
    logger.log_http_request("GET", "/test", 200, 0.1, "127.0.0.1")

    print("✅ Test completado. Revisar archivos en logs_advanced/")
    summary = logger.export_summary()
    print(f"📄 Resumen exportado: {summary}")