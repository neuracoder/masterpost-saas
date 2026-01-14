"""
Test script for Qwen optimized prompts
Tests all three pipelines (Amazon, eBay, Instagram) with the same image
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.qwen_service import PIPELINE_PROMPTS, qwen_service, remove_background_premium_sync

def test_prompts():
    """Test the three optimized prompts with a sample image"""

    print("\n" + "="*80)
    print("TESTING QWEN OPTIMIZED PROMPTS")
    print("="*80)

    # Check if Qwen service is available
    if not qwen_service.available:
        print("\nERROR: Qwen service not available!")
        print("   Check your DASHSCOPE_API_KEY in backend/.env")
        return

    print(f"\nOK Qwen Service Available")
    print(f"   API Key: {qwen_service.api_key[:8]}...{qwen_service.api_key[-4:]}")
    print(f"   Base URL: {qwen_service.base_url}")
    print(f"   Model: {qwen_service.model}")

    # Look for test images
    test_image_paths = [
        "test_images/bicycle.jpg",
        "test_images/product.jpg",
        "test_images/sample.jpg",
        "../test_images/bicycle.jpg",
        "../uploads/test.jpg"
    ]

    test_image = None
    for path in test_image_paths:
        if Path(path).exists():
            test_image = path
            break

    if not test_image:
        print("\n  WARNING: No test image found!")
        print("   Please place a test image in one of these locations:")
        for path in test_image_paths:
            print(f"   - {path}")
        print("\n   You can use any product image (JPG/PNG)")
        print("   For now, showing prompt configurations only...")
        print("\n" + "="*80)

        # Show prompts even without test image
        for pipeline in ["amazon", "ebay", "instagram"]:
            print(f"\n{'='*80}")
            print(f" {pipeline.upper()} PIPELINE PROMPT")
            print(f"{'='*80}")

            prompt_config = PIPELINE_PROMPTS[pipeline]
            print(f"\n Main Prompt ({len(prompt_config['main_prompt'])} characters):")
            print("-" * 80)
            print(prompt_config["main_prompt"])
            print("-" * 80)

            print(f"\n Negative Prompt ({len(prompt_config['negative_prompt'])} characters):")
            print("-" * 80)
            print(prompt_config["negative_prompt"])
            print("-" * 80)

        return

    print(f"\n Test Image Found: {test_image}")
    print(f"   Size: {Path(test_image).stat().st_size / 1024:.1f} KB")

    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    print(f"\n Output Directory: {output_dir.absolute()}")

    pipelines = ["amazon", "ebay", "instagram"]

    for pipeline in pipelines:
        print(f"\n{'='*80}")
        print(f" Testing {pipeline.upper()} Pipeline")
        print(f"{'='*80}")

        # Show prompt being used
        prompt_config = PIPELINE_PROMPTS[pipeline]
        print(f"\n Main Prompt ({len(prompt_config['main_prompt'])} characters):")
        print(f"   {prompt_config['main_prompt'][:150]}...")

        print(f"\n Negative Prompt:")
        print(f"   {prompt_config['negative_prompt'][:100]}...")

        # Set output path
        test_name = Path(test_image).stem
        output = output_dir / f"{test_name}_{pipeline}_qwen.jpg"

        print(f"\n⏳ Processing with Qwen API...")
        print(f"   Input:  {test_image}")
        print(f"   Output: {output}")

        # Process image
        result = remove_background_premium_sync(
            input_path=test_image,
            output_path=str(output),
            pipeline=pipeline
        )

        # Check result
        if result.get('success'):
            file_size = Path(output).stat().st_size / 1024
            print(f"\n Success!")
            print(f"   Output: {output}")
            print(f"   File size: {file_size:.1f} KB")
            print(f"   Method: {result.get('method', 'unknown')}")
        else:
            print(f"\n Failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if result.get('fallback_to_basic'):
                print(f"   Note: This would normally fallback to Basic processing")

    print(f"\n{'='*80}")
    print(" Testing Complete!")
    print(f"{'='*80}")

    # Summary
    successful_outputs = []
    for pipeline in pipelines:
        test_name = Path(test_image).stem if test_image else "test"
        output = output_dir / f"{test_name}_{pipeline}_qwen.jpg"
        if output.exists():
            successful_outputs.append(str(output))

    if successful_outputs:
        print("\n Compare the outputs:")
        for output in successful_outputs:
            print(f"    {output}")
        print("\nYou can now visually compare the quality differences between:")
        print("   • Amazon: Maximum precision, 85% coverage, ultra-clean edges")
        print("   • eBay:   Detail preservation, zoom-optimized, 80-85% coverage")
        print("   • Instagram: Vibrant colors, mobile-first, 75-80% coverage")
    else:
        print("\n  No outputs generated. Check the error messages above.")

    print(f"\n{'='*80}\n")

def show_prompt_comparison():
    """Show side-by-side comparison of all prompts"""
    print("\n" + "="*80)
    print("PROMPT COMPARISON - ALL PIPELINES")
    print("="*80)

    print("\n{:<15} {:<25} {:<25} {:<25}".format(
        "Aspect", "AMAZON", "EBAY", "INSTAGRAM"
    ))
    print("-" * 80)

    aspects = {
        "Coverage": ["85%", "80-85%", "75-80%"],
        "Focus": ["Precision", "Detail", "Vibrancy"],
        "Edges": ["Ultra-clean", "Ultra-sharp", "Sharp"],
        "Quality": ["E-commerce", "High-res zoom", "Social media"],
        "Optimization": ["Marketplace", "Auction detail", "Mobile-first"]
    }

    for aspect, values in aspects.items():
        print("{:<15} {:<25} {:<25} {:<25}".format(
            aspect, values[0], values[1], values[2]
        ))

    print("\n" + "="*80)

    for pipeline in ["amazon", "ebay", "instagram"]:
        config = PIPELINE_PROMPTS[pipeline]
        print(f"\n{pipeline.upper()}:")
        print(f"  Prompt length: {len(config['main_prompt'])} chars")
        print(f"  Negative prompt length: {len(config['negative_prompt'])} chars")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Qwen optimized prompts")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Show prompt comparison table"
    )
    parser.add_argument(
        "--test-image",
        type=str,
        help="Path to test image (optional)"
    )

    args = parser.parse_args()

    if args.compare:
        show_prompt_comparison()
    else:
        test_prompts()
