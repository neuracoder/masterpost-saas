#!/usr/bin/env python3
import subprocess
import threading
import time
import sys
import os
import signal
from pathlib import Path
from datetime import datetime

class MasterpostLauncher:
    def __init__(self):
        self.frontend_process = None
        self.backend_process = None
        self.running = True
        self.npm_path = "npm"
        self.errors = []
        self.log_file = Path("launcher.log")

    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"

        # Print to console
        if level == "ERROR":
            print(f"\033[91m{message}\033[0m")  # Red color
        elif level == "WARN":
            print(f"\033[93m{message}\033[0m")  # Yellow color
        elif level == "SUCCESS":
            print(f"\033[92m{message}\033[0m")  # Green color
        else:
            print(message)

        # Append to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except:
            pass

    def print_banner(self):
        print("+--------------------------------------------------------------+")
        print("|                    > MASTERPOST.IO LAUNCHER                  |")
        print("|                                                              |")
        print("|  Frontend (Next.js):  http://localhost:3000*                 |")
        print("|  Backend (FastAPI):   http://localhost:8002                  |")
        print("|                                                              |")
        print("|  * Puerto puede cambiar si 3000 está ocupado                 |")
        print("|  Ctrl+C para detener ambos servicios                         |")
        print("+--------------------------------------------------------------+")

    def check_correct_directory(self):
        """Verify we're running from the correct directory"""
        current_dir = Path.cwd()

        # Check if we have the expected files
        has_package_json = Path("package.json").exists()
        has_backend = Path("backend").exists()
        has_app = Path("app").exists()
        has_launcher = Path("dual_launcher.py").exists()

        if not has_package_json:
            self.log("\n" + "="*60, "ERROR")
            self.log("ERROR - Directorio incorrecto detectado", "ERROR")
            self.log("="*60, "ERROR")
            self.log(f"Directorio actual: {current_dir}", "ERROR")
            self.log("", "ERROR")
            self.log("Este script debe ejecutarse desde el directorio del proyecto:", "ERROR")
            self.log("  Masterpost-SaaS/", "ERROR")
            self.log("", "ERROR")

            # Try to find the correct directory
            if (current_dir / "Masterpost-SaaS" / "package.json").exists():
                self.log("SOLUCIÓN ENCONTRADA:", "WARN")
                self.log("", "WARN")
                self.log("  cd Masterpost-SaaS", "WARN")
                self.log("  python dual_launcher.py", "WARN")
                self.log("", "WARN")
            else:
                self.log("SOLUCIÓN:", "WARN")
                self.log("  1. Abre terminal en el directorio Masterpost-SaaS/", "WARN")
                self.log("  2. Ejecuta: python dual_launcher.py", "WARN")
                self.log("", "WARN")

            self.log("Archivos esperados en el directorio actual:", "ERROR")
            self.log(f"  ✗ package.json - {'Encontrado' if has_package_json else 'NO ENCONTRADO'}", "ERROR")
            self.log(f"  ✗ backend/ - {'Encontrado' if has_backend else 'NO ENCONTRADO'}", "ERROR")
            self.log(f"  ✗ app/ - {'Encontrado' if has_app else 'NO ENCONTRADO'}", "ERROR")
            self.log("="*60, "ERROR")
            return False

        return True

    def check_dependencies(self):
        self.log("\nVerificando dependencias...")

        # Check npm
        try:
            result = subprocess.run(
                [self.npm_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                timeout=10
            )
            self.log(f"OK - npm v{result.stdout.strip()} encontrado", "SUCCESS")
        except subprocess.TimeoutExpired:
            self.log("ERROR - npm no responde (timeout)", "ERROR")
            self.log("INFO - Verifica que npm esté instalado correctamente", "WARN")
            return False
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            self.log(f"ERROR - npm no encontrado: {e}", "ERROR")
            self.log("INFO - Instala Node.js desde https://nodejs.org/", "WARN")
            return False

        # Check Python packages
        try:
            import fastapi, uvicorn, rembg, PIL
            self.log("OK - FastAPI y Uvicorn disponibles", "SUCCESS")
            self.log("OK - rembg y PIL disponibles", "SUCCESS")
        except ImportError as e:
            missing_pkg = str(e).split("'")[1] if "'" in str(e) else "unknown"
            self.log(f"ERROR - Paquete Python faltante: {missing_pkg}", "ERROR")
            self.log("INFO - Ejecuta: pip install fastapi uvicorn rembg pillow", "WARN")
            return False

        # Check for package.json
        if not Path("package.json").exists():
            self.log("ERROR - package.json no encontrado en directorio raíz", "ERROR")
            return False

        # Check node_modules
        if not Path("node_modules").exists():
            self.log("WARN - node_modules no encontrado. Instalando dependencias...", "WARN")
            try:
                self.log("INFO - Ejecutando npm install (esto puede tardar)...", "INFO")
                result = subprocess.run(
                    [self.npm_path, 'install'],
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=True,
                    timeout=300  # 5 minutes timeout
                )
                self.log("OK - Dependencias npm instaladas", "SUCCESS")

                # Log npm output if there were warnings
                if result.stderr:
                    self.log("NPM Warnings:", "WARN")
                    for line in result.stderr.split('\n')[:10]:  # First 10 lines
                        if line.strip():
                            self.log(f"  {line}", "WARN")
            except subprocess.TimeoutExpired:
                self.log("ERROR - npm install timeout (>5 minutos)", "ERROR")
                self.log("INFO - Intenta manualmente: npm install", "WARN")
                return False
            except subprocess.CalledProcessError as e:
                self.log(f"ERROR - Fallo al instalar dependencias npm", "ERROR")
                self.log(f"Código de error: {e.returncode}", "ERROR")
                if e.stderr:
                    self.log("Detalles del error:", "ERROR")
                    for line in e.stderr.split('\n')[:20]:  # First 20 lines
                        if line.strip():
                            self.log(f"  {line}", "ERROR")
                return False
        else:
            self.log("OK - node_modules encontrado", "SUCCESS")

        # Check backend directory
        if not Path("backend").exists():
            self.log("ERROR - Directorio backend/ no encontrado", "ERROR")
            return False

        if not Path("backend/server.py").exists():
            self.log("ERROR - backend/server.py no encontrado", "ERROR")
            return False

        self.log("OK - Directorio backend verificado", "SUCCESS")
        return True

    def start_frontend(self):
        self.log("\nIniciando Frontend (Next.js)...")
        try:
            self.frontend_process = subprocess.Popen(
                [self.npm_path, 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True
            )

            # Monitor both stdout and stderr
            def read_output(pipe, prefix):
                for line in iter(pipe.readline, ''):
                    if not self.running:
                        break
                    line = line.strip()
                    if line:
                        # Check for errors
                        if "error" in line.lower() or "failed" in line.lower():
                            self.log(f"[{prefix}] {line}", "ERROR")
                        else:
                            print(f"[{prefix}] {line}")

                        # Check if frontend is ready
                        if "Local:" in line and "localhost:" in line:
                            import re
                            port_match = re.search(r'localhost:(\d+)', line)
                            if port_match:
                                port = port_match.group(1)
                                self.log(f"OK - Frontend listo en http://localhost:{port}", "SUCCESS")

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(target=read_output, args=(self.frontend_process.stdout, "FRONTEND"), daemon=True)
            stderr_thread = threading.Thread(target=read_output, args=(self.frontend_process.stderr, "FRONTEND-ERR"), daemon=True)

            stdout_thread.start()
            stderr_thread.start()

        except Exception as e:
            self.log(f"ERROR - Al iniciar frontend: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")

    def start_backend(self):
        self.log("\nIniciando Backend (FastAPI)...")
        try:
            backend_dir = Path("backend")
            if not backend_dir.exists():
                self.log("ERROR - Directorio backend no encontrado", "ERROR")
                return

            server_file = backend_dir / "server.py"
            if not server_file.exists():
                self.log("ERROR - Archivo server.py no encontrado en directorio backend", "ERROR")
                return

            self.backend_process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Monitor both stdout and stderr
            def read_output(pipe, prefix):
                for line in iter(pipe.readline, ''):
                    if not self.running:
                        break
                    line = line.strip()
                    if line:
                        # Check for errors
                        if "error" in line.lower() or "exception" in line.lower() or "traceback" in line.lower():
                            self.log(f"[{prefix}] {line}", "ERROR")
                        else:
                            print(f"[{prefix}] {line}")

                        # Check if backend is ready
                        if "Uvicorn running on" in line:
                            self.log("OK - Backend listo en http://localhost:8002", "SUCCESS")

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(target=read_output, args=(self.backend_process.stdout, "BACKEND"), daemon=True)
            stderr_thread = threading.Thread(target=read_output, args=(self.backend_process.stderr, "BACKEND-ERR"), daemon=True)

            stdout_thread.start()
            stderr_thread.start()

        except Exception as e:
            self.log(f"ERROR - Al iniciar backend: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")

    def cleanup(self):
        self.log("\nDeteniendo servicios...")
        self.running = False

        if self.frontend_process:
            try:
                if sys.platform == "win32":
                    subprocess.run(
                        f"taskkill /F /PID {self.frontend_process.pid} /T",
                        check=True,
                        shell=True,
                        capture_output=True,
                        timeout=5
                    )
                else:
                    self.frontend_process.terminate()
                    self.frontend_process.wait(timeout=5)
                self.log("OK - Frontend detenido", "SUCCESS")
            except Exception as e:
                self.log(f"WARN - Error al detener frontend: {e}", "WARN")
                try:
                    self.frontend_process.kill()
                except:
                    pass

        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.log("OK - Backend detenido", "SUCCESS")
            except Exception as e:
                self.log(f"WARN - Error al detener backend: {e}", "WARN")
                try:
                    self.backend_process.kill()
                except:
                    pass

    def run(self):
        self.print_banner()
        self.log(f"\nLogs guardados en: {self.log_file.absolute()}", "INFO")

        # Check if we're in the correct directory
        if not self.check_correct_directory():
            self.log("\nERROR - Ejecuta el script desde el directorio correcto", "ERROR")
            return

        # Check dependencies
        if not self.check_dependencies():
            self.log("\nERROR - Faltan dependencias. Revisa los errores arriba.", "ERROR")
            return

        def signal_handler(signum, frame):
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Start both services
            frontend_thread = threading.Thread(target=self.start_frontend, daemon=True)
            backend_thread = threading.Thread(target=self.start_backend, daemon=True)

            frontend_thread.start()
            time.sleep(2)  # Give frontend a head start
            backend_thread.start()

            self.log("\nAmbos servicios iniciando...", "INFO")
            self.log("Frontend: http://localhost:3000", "INFO")
            self.log("Backend:  http://localhost:8002", "INFO")
            self.log("\nPresiona Ctrl+C para detener ambos servicios\n", "INFO")

            # Monitor processes
            while self.running:
                time.sleep(1)

                if self.frontend_process and self.frontend_process.poll() is not None:
                    exit_code = self.frontend_process.returncode
                    self.log(f"ERROR - Frontend se cerró inesperadamente (código: {exit_code})", "ERROR")
                    self.log("INFO - Revisa los logs arriba para más detalles", "WARN")
                    break

                if self.backend_process and self.backend_process.poll() is not None:
                    exit_code = self.backend_process.returncode
                    self.log(f"ERROR - Backend se cerró inesperadamente (código: {exit_code})", "ERROR")
                    self.log("INFO - Revisa los logs arriba para más detalles", "WARN")
                    break

        except KeyboardInterrupt:
            self.log("\nCtrl+C detectado, cerrando servicios...", "INFO")
        except Exception as e:
            self.log(f"\nERROR inesperado: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
        finally:
            self.cleanup()
            self.log(f"\nLogs completos en: {self.log_file.absolute()}", "INFO")

if __name__ == "__main__":
    launcher = MasterpostLauncher()
    launcher.run()
