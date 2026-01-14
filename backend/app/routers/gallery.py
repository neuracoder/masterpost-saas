"""
Gallery API for Landing Page Showcase
Serves before/after images for the showcase slider
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict, Any

router = APIRouter()

# Gallery images configuration
GALLERY_IMAGES = {
    "bicicleta": {
        "original": "img_original/bicicleta.jpg",
        "processed": "img_procesada/bicicleta.jpg",
        "title": "Complex Vintage Bicycle",
        "description": "Multiple angles & spokes",
        "processing_time": "6 seconds",
        "tier": "Premium",
        "category": "complex"
    },
    "lampara": {
        "original": "img_original/lampara.jpg",
        "processed": "img_procesada/lampara.jpg",
        "title": "Glass & Metal Lamp",
        "description": "Transparent glass",
        "processing_time": "5 seconds",
        "tier": "Premium",
        "category": "glass"
    },
    "joyeria": {
        "original": "img_original/joyeria.jpg",
        "processed": "img_procesada/joyeria.jpg",
        "title": "Jewelry with Reflections",
        "description": "Fine details & shine",
        "processing_time": "4 seconds",
        "tier": "Premium",
        "category": "jewelry"
    },
    "botella": {
        "original": "img_original/botella.jpg",
        "processed": "img_procesada/botella.jpg",
        "title": "Glass Bottle",
        "description": "Transparency & reflections",
        "processing_time": "5 seconds",
        "tier": "Premium",
        "category": "glass"
    },
    "zapato": {
        "original": "img_original/zapato.jpg",
        "processed": "img_procesada/zapato.jpg",
        "title": "Leather Shoe",
        "description": "Textures & details",
        "processing_time": "4 seconds",
        "tier": "Premium",
        "category": "fashion"
    },
    "peluche": {
        "original": "img_original/peluche.jpg",
        "processed": "img_procesada/peluche.jpg",
        "title": "Plush Toy",
        "description": "Fuzzy edges",
        "processing_time": "5 seconds",
        "tier": "Premium",
        "category": "toys"
    }
}

@router.get("/gallery/{item_name}/original")
async def get_original_image(item_name: str):
    """
    Get original image for gallery item

    Args:
        item_name: Name of the gallery item (e.g., 'bicicleta')

    Returns:
        Image file
    """
    if item_name not in GALLERY_IMAGES:
        raise HTTPException(status_code=404, detail=f"Gallery item '{item_name}' not found")

    image_path = Path(GALLERY_IMAGES[item_name]["original"])

    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Image file not found: {image_path}. Please add images to backend/img_original/"
        )

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/gallery/{item_name}/processed")
async def get_processed_image(item_name: str):
    """
    Get processed image for gallery item

    Args:
        item_name: Name of the gallery item (e.g., 'bicicleta')

    Returns:
        Image file
    """
    if item_name not in GALLERY_IMAGES:
        raise HTTPException(status_code=404, detail=f"Gallery item '{item_name}' not found")

    image_path = Path(GALLERY_IMAGES[item_name]["processed"])

    if not image_path.exists():
        # Fallback: return original if processed doesn't exist
        original_path = Path(GALLERY_IMAGES[item_name]["original"])
        if original_path.exists():
            return FileResponse(
                original_path,
                media_type="image/jpeg",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*",
                    "X-Image-Status": "processing"  # Signal that this is a fallback
                }
            )
        raise HTTPException(
            status_code=404,
            detail=f"Image file not found: {image_path}. Please add images to backend/img_procesada/"
        )

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/gallery/all")
async def get_all_gallery_items() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get metadata for all gallery items

    Returns:
        Dictionary with list of all gallery items with their metadata
    """
    items = []

    for item_id, data in GALLERY_IMAGES.items():
        # Check if images exist
        original_exists = Path(data["original"]).exists()
        processed_exists = Path(data["processed"]).exists()

        items.append({
            "id": item_id,
            "title": data["title"],
            "description": data["description"],
            "processing_time": data["processing_time"],
            "tier": data["tier"],
            "category": data["category"],
            "original_url": f"/api/v1/gallery/{item_id}/original",
            "processed_url": f"/api/v1/gallery/{item_id}/processed",
            "original_exists": original_exists,
            "processed_exists": processed_exists,
            "status": "ready" if (original_exists and processed_exists) else "pending"
        })

    return {
        "items": items,
        "total": len(items),
        "ready": sum(1 for item in items if item["status"] == "ready")
    }

@router.get("/gallery/{item_name}/info")
async def get_gallery_item_info(item_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific gallery item

    Args:
        item_name: Name of the gallery item

    Returns:
        Dictionary with item details
    """
    if item_name not in GALLERY_IMAGES:
        raise HTTPException(status_code=404, detail=f"Gallery item '{item_name}' not found")

    data = GALLERY_IMAGES[item_name]
    original_exists = Path(data["original"]).exists()
    processed_exists = Path(data["processed"]).exists()

    return {
        "id": item_name,
        "title": data["title"],
        "description": data["description"],
        "processing_time": data["processing_time"],
        "tier": data["tier"],
        "category": data["category"],
        "original_url": f"/api/v1/gallery/{item_name}/original",
        "processed_url": f"/api/v1/gallery/{item_name}/processed",
        "original_exists": original_exists,
        "processed_exists": processed_exists,
        "status": "ready" if (original_exists and processed_exists) else "pending"
    }
