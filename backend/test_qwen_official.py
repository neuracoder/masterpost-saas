"""
Test oficial basado en la documentación de Alibaba Cloud Model Studio
https://help.aliyun.com/zh/model-studio/developer-reference/qwen-image-edit-api
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.qwen_service import qwen_service, health_check

def test_health():
    """Test service configuration"""
    print()
    print("="*80)
    print("QWEN IMAGE EDIT - Health Check")
    print("="*80)
    print()

    health = health_check()

    print("Service Configuration:")
    print(f"  Status: {health['status']}")
    print(f"  Available: {health['available']}")
    print(f"  API Key Configured: {health['api_key_configured']}")
    print(f"  Model: {health['model']}")
    print(f"  Base URL: {health['base_url']}")
    print()

    if health['available']:
        print("OK - Qwen service is ready")
    else:
        print("ERROR - Qwen service not available")
        print("  Check DASHSCOPE_API_KEY in backend/.env")

    print("="*80)
    print()

def test_qwen():
    """Test Qwen Image Edit API with real image"""
    print()
    print("="*80)
    print("QWEN IMAGE EDIT - Official Documentation Test")
    print("="*80)
    print()

    # Check service
    if not qwen_service.available:
        print("ERROR: Qwen service not available!")
        print("Check your DASHSCOPE_API_KEY in backend/.env")
        print()
        return

    # Test images
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
        print("For testing without image, run:")
        print("  python test_qwen_official.py --health")
        print()
        return

    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Configure paths
    test_name = Path(test_image).stem
    output_image = output_dir / f"{test_name}_qwen_official.jpg"

    print(f"Input:  {test_image}")
    print(f"        Size: {Path(test_image).stat().st_size / 1024:.1f} KB")
    print(f"Output: {output_image}")
    print()

    # Use official prompt format
    prompt = """Remove the background completely from this product image.
Replace the background with pure white (RGB 255, 255, 255).
Keep the main product with all details preserved.
Remove ALL shadows, reflections, and background elements.
Maintain original product colors."""

    print("Prompt:")
    for line in prompt.split('\n'):
        print(f"  {line}")
    print()

    print("Starting API call...")
    print()

    # Process image
    result = qwen_service.remove_background(
        input_path=test_image,
        output_path=str(output_image),
        prompt=prompt
    )

    print()
    print("="*80)
    print("RESULT")
    print("="*80)
    print()

    if result['success']:
        print("SUCCESS!")
        print(f"  Output: {output_image}")
        print(f"  File size: {result.get('file_size', 0) / 1024:.1f} KB")
        print(f"  Method: {result.get('method', 'unknown')}")
        print(f"  Request ID: {result.get('request_id', 'N/A')}")
        print()
        print("Image has been saved successfully!")
        print("The processed image URL is valid for 24 hours.")
        print()
    else:
        print("FAILED!")
        print(f"  Error: {result.get('error')}")
        print()
        if result.get('fallback_to_basic'):
            print("  This would normally fallback to Basic processing in production")
        print()

    print("="*80)
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Qwen Image Edit API (Official Implementation)"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run health check only"
    )

    args = parser.parse_args()

    if args.health:
        test_health()
    else:
        test_qwen()
