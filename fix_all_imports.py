"""
Script para arreglar TODOS los imports en backend/app/
Convierte imports absolutos a relativos automáticamente

EJECUTAR:
    cd /ruta/a/Masterpost-SaaS
    python fix_all_imports.py

Luego:
    git add backend/app/
    git commit -m "Fix: All imports to relative"
    git push origin main
"""

import os
import re
from pathlib import Path


def fix_imports_in_file(filepath, app_root):
    """Arregla imports en un archivo específico"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo {filepath}: {e}")
        return False
    
    original = content
    
    # Calcular profundidad relativa a backend/app/
    try:
        rel_path = filepath.relative_to(app_root)
        depth = len(rel_path.parts) - 1  # -1 porque no contamos el archivo
    except:
        depth = 0
    
    # Determinar prefijo
    if depth == 0:
        # En app/main.py
        prefix = "."
    else:
        # En subdirectorios
        prefix = ".."
    
    # === PATRONES DE REEMPLAZO ===
    
    # 1. from app.X import Y → from .X import Y (o ..X)
    content = re.sub(r'\bfrom app\.(\w+)', f'from {prefix}.\\1', content)
    
    # 2. from processing.X import Y → from .X import Y
    # (cuando está DENTRO de backend/app/processing/)
    if 'processing' in str(filepath):
        content = re.sub(r'\bfrom processing\.', 'from .', content)
    
    # 3. from services.X import Y → from .X import Y  
    # (cuando está DENTRO de backend/app/services/)
    if 'services' in str(filepath):
        content = re.sub(r'\bfrom services\.', 'from .', content)
    
    # 4. import app.X → import .X
    content = re.sub(r'\bimport app\.', f'import {prefix}.', content)
    
    # Guardar si hubo cambios
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mostrar qué cambió
        changes = []
        if 'from app.' in original and 'from app.' not in content:
            changes.append(f"from app. → from {prefix}.")
        if 'from processing.' in original and 'from processing.' not in content:
            changes.append("from processing. → from .")
        if 'from services.' in original and 'from services.' not in content:
            changes.append("from services. → from .")
        
        # Fix para Windows - usar resolve() para rutas absolutas
        try:
            display_path = filepath.relative_to(Path.cwd().resolve())
        except ValueError:
            display_path = filepath.name
        
        print(f"✅ {display_path}")
        for change in changes:
            print(f"   {change}")
        return True
    else:
        return False


def ensure_init_files(app_root):
    """Crea archivos __init__.py donde falten"""
    
    created = []
    dirs_to_check = [
        app_root,
        app_root / 'routers',
        app_root / 'services', 
        app_root / 'core',
        app_root / 'auth',
        app_root / 'models',
        app_root / 'database',
        app_root / 'processing',
    ]
    
    for dir_path in dirs_to_check:
        if dir_path.exists() and dir_path.is_dir():
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                created.append(init_file)
    
    return created


def main():
    print("=" * 70)
    print("🔧 FIX ALL IMPORTS - Masterpost.io")
    print("=" * 70)
    print()
    
    # Verificar ubicación
    app_root = Path('backend/app')
    if not app_root.exists():
        print("❌ ERROR: backend/app/ no encontrado")
        print("   Ejecuta desde la raíz del proyecto")
        return 1
    
    print(f"📁 Procesando: {app_root.absolute()}")
    print()
    
    # PASO 1: Crear __init__.py
    print("-" * 70)
    print("PASO 1: Verificar __init__.py")
    print("-" * 70)
    created = ensure_init_files(app_root)
    if created:
        for f in created:
            try:
                display = f.relative_to(Path.cwd().resolve())
            except ValueError:
                display = f.name
            print(f"✅ Creado: {display}")
    else:
        print("✅ Todos los __init__.py existen")
    print()
    
    # PASO 2: Arreglar imports
    print("-" * 70)
    print("PASO 2: Arreglar imports")
    print("-" * 70)
    print()
    
    fixed_count = 0
    total_count = 0
    
    # Buscar todos los .py
    for py_file in app_root.rglob('*.py'):
        # Ignorar __pycache__
        if '__pycache__' in str(py_file):
            continue
        
        # Ignorar __init__.py
        if py_file.name == '__init__.py':
            continue
        
        total_count += 1
        if fix_imports_in_file(py_file, app_root):
            fixed_count += 1
    
    print()
    print("=" * 70)
    print("✅ COMPLETADO")
    print("=" * 70)
    print(f"   Archivos procesados:  {total_count}")
    print(f"   Archivos modificados: {fixed_count}")
    print(f"   __init__.py creados:  {len(created)}")
    print("=" * 70)
    print()
    
    if fixed_count > 0:
        print("📋 SIGUIENTE PASO:")
        print()
        print("   git add backend/app/")
        print("   git commit -m 'Fix: Convert all imports to relative'")
        print("   git push origin main")
        print()
        print("Railway redeplegará automáticamente.")
    else:
        print("ℹ️  No se encontraron imports para arreglar")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
