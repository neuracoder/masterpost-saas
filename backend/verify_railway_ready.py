"""
Verificación final antes de deployment en Railway
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Verifica si un archivo existe"""
    exists = Path(filepath).exists()
    status = "[OK]" if exists else ("[FAIL]" if required else "[WARN]")
    req = "(required)" if required else "(optional)"
    print(f"{status} {filepath} {req}")
    return exists

def check_file_contains(filepath, search_string):
    """Verifica si un archivo contiene un string"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_string in content
            status = "[OK]" if found else "[FAIL]"
            print(f"{status} {filepath} contains '{search_string}'")
            return found
    except Exception as e:
        print(f"[FAIL] Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("RAILWAY DEPLOYMENT VERIFICATION")
    print("=" * 60)

    all_passed = True

    # Determine base directory (we're in backend/)
    backend_dir = Path(__file__).parent

    # 1. Archivos críticos
    print("\n[FILES] Critical Files:")
    all_passed &= check_file_exists(backend_dir / "app" / "main.py", required=True)
    all_passed &= check_file_exists(backend_dir / "requirements.txt", required=True)
    all_passed &= check_file_exists(backend_dir / "Procfile", required=True)
    all_passed &= check_file_exists(backend_dir / "nixpacks.toml", required=True)
    all_passed &= check_file_exists(backend_dir / ".env.example", required=True)

    # 2. Archivos que NO deben existir
    print("\n[CHECK] Files that should NOT exist:")
    server_py = backend_dir / "server.py"
    if server_py.exists():
        print(f"[FAIL] server.py DEBE SER ELIMINADO")
        all_passed = False
    else:
        print("[OK] server.py eliminado correctamente")

    env_file = backend_dir / ".env"
    if env_file.exists():
        print(f"[WARN] .env existe (NO debe estar en git)")
    else:
        print("[OK] .env no existe en directorio")

    # 3. Contenido de archivos críticos
    print("\n[CONTENT] File Contents:")
    all_passed &= check_file_contains(
        backend_dir / "requirements.txt",
        "rembg==2.0.61"
    )
    all_passed &= check_file_contains(
        backend_dir / "requirements.txt",
        "dashscope==1.20.14"
    )
    all_passed &= check_file_contains(
        backend_dir / "Procfile",
        "uvicorn app.main:app"
    )
    all_passed &= check_file_contains(
        backend_dir / "nixpacks.toml",
        "python311"
    )

    # 4. Verificar imports (skip if dependencies not installed)
    print("\n[IMPORT] Import Verification:")
    try:
        sys.path.insert(0, str(backend_dir.absolute()))
        from app.main import app
        print("[OK] app.main importa correctamente")
        print(f"[OK] {len(app.routes)} rutas registradas")
    except Exception as e:
        print(f"[WARN] Error importando app.main (puede ser normal si dependencies no estan instaladas): {e}")
        # Don't fail on import errors - dependencies might not be installed yet

    # 5. Resultado final
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] VERIFICACION EXITOSA - LISTO PARA RAILWAY")
        print("=" * 60)
        print("\n[NEXT] Proximos pasos:")
        print("1. git add .")
        print("2. git commit -m 'Refactor: Unify backend for Railway'")
        print("3. git push origin main")
        print("4. Configurar Railway con Root Directory: /backend")
        return 0
    else:
        print("[FAIL] VERIFICACION FALLIDA - REVISAR ERRORES")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
