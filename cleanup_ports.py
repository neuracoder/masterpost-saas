#!/usr/bin/env python3
"""
Cleanup Ports Script - Libera los puertos 3000 y 8002
"""
import subprocess
import sys
from pathlib import Path

def print_banner():
    print("+" + "="*60 + "+")
    print("|" + " "*15 + "PORT CLEANUP UTILITY" + " "*25 + "|")
    print("|" + " "*10 + "Liberando puertos 3000 y 8002" + " "*20 + "|")
    print("+" + "="*60 + "+")
    print()

def find_process_on_port(port):
    """Find process ID using a specific port"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    # Last part is the PID
                    pid = parts[-1]
                    return pid
        return None
    except Exception as e:
        print(f"Error buscando proceso en puerto {port}: {e}")
        return None

def kill_process(pid):
    """Kill process by PID"""
    try:
        result = subprocess.run(
            f'taskkill /F /PID {pid}',
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error matando proceso {pid}: {e}")
        return False

def get_process_name(pid):
    """Get process name from PID"""
    try:
        result = subprocess.run(
            f'tasklist /FI "PID eq {pid}" /FO CSV /NH',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            # Parse CSV output: "python.exe","12345","Console","1","123,456 K"
            name = result.stdout.split(',')[0].strip('"')
            return name
        return "Unknown"
    except:
        return "Unknown"

def cleanup_port(port, name):
    """Clean up a specific port"""
    print(f"\n[{name}] Verificando puerto {port}...")

    pid = find_process_on_port(port)

    if pid:
        process_name = get_process_name(pid)
        print(f"  ⚠️  Puerto {port} ocupado por proceso: {process_name} (PID: {pid})")

        response = input(f"  ¿Matar proceso {process_name} (PID: {pid})? [S/n]: ").strip().lower()

        if response == '' or response == 's' or response == 'y':
            print(f"  🔫 Matando proceso {pid}...")
            if kill_process(pid):
                print(f"  ✅ Proceso {pid} eliminado exitosamente")
                return True
            else:
                print(f"  ❌ Error al matar proceso {pid}")
                return False
        else:
            print(f"  ⏭️  Saltando puerto {port}")
            return False
    else:
        print(f"  ✅ Puerto {port} libre")
        return True

def main():
    print_banner()

    # Check if running on Windows
    if sys.platform != "win32":
        print("❌ Este script solo funciona en Windows")
        print("En Linux/Mac usa: lsof -ti:8002 | xargs kill -9")
        return

    # Cleanup ports
    ports = [
        (3000, "Frontend"),
        (8002, "Backend")
    ]

    results = []
    for port, name in ports:
        results.append(cleanup_port(port, name))

    # Summary
    print("\n" + "="*62)
    print("RESUMEN:")
    print("="*62)

    for (port, name), success in zip(ports, results):
        status = "✅ Libre" if success else "❌ Ocupado"
        print(f"  Puerto {port} ({name}): {status}")

    print("="*62)

    if all(results):
        print("\n✅ Todos los puertos están libres!")
        print("🚀 Ahora puedes ejecutar: python dual_launcher.py")
    else:
        print("\n⚠️  Algunos puertos siguen ocupados")
        print("💡 Intenta cerrar las aplicaciones manualmente o reinicia el sistema")

    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelado por usuario")
        sys.exit(0)
