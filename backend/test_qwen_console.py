"""
Test que replica EXACTAMENTE lo que hace la consola de Alibaba Cloud
Este script prueba la API de Qwen directamente
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.qwen_service import qwen_service

def test_like_console():
    """Test la API de Qwen replicando el comportamiento de la consola"""

    print()
    print("="*80)
    print("TESTING QWEN API - Console Replication Mode")
    print("="*80)
    print()

    # Verificar que el servicio esté disponible
    if not qwen_service.available:
        print("ERROR: Qwen service not available!")
        print("Check your DASHSCOPE_API_KEY in backend/.env")
        print()
        return

    print("OK - Qwen Service Available")
    print(f"  API Key: {qwen_service.api_key[:15]}...{qwen_service.api_key[-4:]}")
    print(f"  Base URL: {qwen_service.base_url}")
    print(f"  Endpoint: {qwen_service.endpoint}")
    print(f"  Model: {qwen_service.model}")
    print()

    # Buscar imagen de prueba
    test_images = [
        "test_images/lamp.jpg",
        "test_images/product.jpg",
        "test_images/sample.jpg",
        "../uploads/lamp_test.jpg",
        "uploads/lamp_test.jpg"
    ]

    test_image = None
    for img_path in test_images:
        if Path(img_path).exists():
            test_image = img_path
            break

    if not test_image:
        print("WARNING: No test image found!")
        print("Please place a test image in one of these locations:")
        for img_path in test_images:
            print(f"  - {img_path}")
        print()
        print("For now, testing service configuration only...")
        print()

        # Mostrar configuración
        print("="*80)
        print("SERVICE CONFIGURATION:")
        print("="*80)
        print(f"Model: {qwen_service.model}")
        print(f"Endpoint: {qwen_service.endpoint}")
        print(f"Full URL: {qwen_service.base_url}{qwen_service.endpoint}")
        print()
        print("This configuration matches the Alibaba Cloud console")
        print("="*80)
        return

    # Crear directorio de salida
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Configurar rutas
    test_name = Path(test_image).stem
    output_image = output_dir / f"{test_name}_qwen_console.jpg"

    print(f"Input:  {test_image}")
    print(f"        Size: {Path(test_image).stat().st_size / 1024:.1f} KB")
    print(f"Output: {output_image}")
    print()

    # Usar el MISMO prompt que en la consola de Alibaba
    positive_prompt = """frame
- Remove ALL shadows, reflections, and background elements
- Preserve product transparency if it's glass or translucent
- Maintain original product colors"""

    negative_prompt = ""

    print("="*80)
    print("PROCESSING WITH QWEN API")
    print("="*80)
    print()
    print(f"Positive Prompt:")
    print(f"  {positive_prompt}")
    print()
    print(f"Negative Prompt: {negative_prompt if negative_prompt else '(empty)'}")
    print()
    print("Starting API call...")
    print()

    # Procesar imagen
    result = qwen_service.remove_background(
        input_path=test_image,
        output_path=str(output_image),
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt
    )

    print()
    print("="*80)
    print("RESULT")
    print("="*80)

    if result['success']:
        print()
        print("SUCCESS!")
        print(f"  Output saved to: {output_image}")
        print(f"  File size: {result.get('file_size', 0) / 1024:.1f} KB")
        print(f"  Method: {result.get('method', 'unknown')}")
        print()
        print("Compare this result with the console result!")
        print()
    else:
        print()
        print("FAILED!")
        print(f"  Error: {result.get('error')}")
        print()
        if "fallback_to_basic" in result and result["fallback_to_basic"]:
            print("  This would normally fallback to Basic processing in production")
        print()

    print("="*80)
    print()


def test_api_config():
    """Test solo la configuración de la API"""

    print()
    print("="*80)
    print("QWEN API CONFIGURATION TEST")
    print("="*80)
    print()

    from services.qwen_service import health_check

    health = health_check()

    print("Service Status:")
    print(f"  Status: {health['status']}")
    print(f"  Available: {health['available']}")
    print(f"  API Key Configured: {health['api_key_configured']}")
    print(f"  Model: {health['model']}")
    print(f"  Endpoint: {health['endpoint']}")
    print()

    if health['available']:
        print("OK - Qwen service is ready to use")
    else:
        print("ERROR - Qwen service not available")
        print("  Check DASHSCOPE_API_KEY in backend/.env")

    print()
    print("="*80)
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Qwen API (Console Mode)")
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Test configuration only (no image processing)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to test image (optional)"
    )

    args = parser.parse_args()

    if args.config_only:
        test_api_config()
    else:
        test_like_console()
