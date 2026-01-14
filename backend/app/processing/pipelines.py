from PIL import Image
from typing import Dict, Any, Tuple
from pathlib import Path

from .image_processor import ImageProcessor

class BasePipeline:
    def __init__(self, processor: ImageProcessor):
        self.processor = processor
        self.name = "base"
        self.description = "Base pipeline"

    def process(self, image: Image.Image, settings: Dict[str, Any] = None) -> Image.Image:
        raise NotImplementedError("Subclasses must implement process method")

    def get_pipeline_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_size": getattr(self, 'target_size', None),
            "features": getattr(self, 'features', [])
        }

class AmazonPipeline(BasePipeline):
    def __init__(self, processor: ImageProcessor):
        super().__init__(processor)
        self.name = "Amazon Compliant"
        self.description = "White background, 1000x1000px, 85% product coverage"
        self.target_size = (1000, 1000)
        self.features = [
            "White background removal",
            "Square format",
            "Product centering",
            "Quality optimization"
        ]

    def process(self, image: Image.Image, settings: Dict[str, Any] = None) -> Image.Image:
        # Simple local processing: resize to 1000x1000 with white background
        # Image should already have background removed by rembg in processing service

        # Resize image maintaining aspect ratio
        image.thumbnail((1000, 1000), Image.Resampling.LANCZOS)

        # Create white background
        white_bg = Image.new('RGB', (1000, 1000), (255, 255, 255))

        # Center image on white background
        x = (1000 - image.width) // 2
        y = (1000 - image.height) // 2
        white_bg.paste(image, (x, y), image if image.mode == 'RGBA' else None)

        return white_bg

    def _optimize_product_coverage(self, image: Image.Image) -> Image.Image:
        # Crop to focus on the main subject (simple center crop with margin)
        width, height = image.size
        margin = min(width, height) * 0.05  # 5% margin

        left = int(margin)
        top = int(margin)
        right = int(width - margin)
        bottom = int(height - margin)

        return image.crop((left, top, right, bottom))

class InstagramPipeline(BasePipeline):
    def __init__(self, processor: ImageProcessor):
        super().__init__(processor)
        self.name = "Instagram Ready"
        self.description = "1080x1080px square format with color enhancement"
        self.target_size = (1080, 1080)
        self.features = [
            "Square crop",
            "Color boost",
            "Contrast enhancement",
            "Social media optimization"
        ]

    def process(self, image: Image.Image, settings: Dict[str, Any] = None) -> Image.Image:
        # Simple local processing: resize to 1080x1080 with white background

        # Resize image maintaining aspect ratio
        image.thumbnail((1080, 1080), Image.Resampling.LANCZOS)

        # Create white background
        white_bg = Image.new('RGB', (1080, 1080), (255, 255, 255))

        # Center image on white background
        x = (1080 - image.width) // 2
        y = (1080 - image.height) // 2
        white_bg.paste(image, (x, y), image if image.mode == 'RGBA' else None)

        return white_bg

    def _square_crop(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        size = min(width, height)

        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size

        return image.crop((left, top, right, bottom))

    def _apply_vignette(self, image: Image.Image) -> Image.Image:
        # Create a subtle vignette effect
        from PIL import ImageDraw
        import numpy as np

        width, height = image.size

        # Create mask for vignette
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)

        # Create radial gradient
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2

        for i in range(max_radius):
            alpha = int(255 * (1 - (i / max_radius) * 0.3))  # Subtle effect
            draw.ellipse([
                center_x - i, center_y - i,
                center_x + i, center_y + i
            ], fill=alpha)

        # Apply mask
        vignette = Image.new('RGB', image.size, (0, 0, 0))
        result = Image.composite(image, vignette, mask)

        return result

class EbayPipeline(BasePipeline):
    def __init__(self, processor: ImageProcessor):
        super().__init__(processor)
        self.name = "eBay Optimized"
        self.description = "1600x1600px high resolution for detailed product view"
        self.target_size = (1600, 1600)
        self.features = [
            "High resolution",
            "Detail enhancement",
            "Multiple angle support",
            "Zoom optimization"
        ]

    def process(self, image: Image.Image, settings: Dict[str, Any] = None) -> Image.Image:
        # Simple local processing: resize to 1600x1600 with white background

        # Resize image maintaining aspect ratio
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)

        # Create white background
        white_bg = Image.new('RGB', (1600, 1600), (255, 255, 255))

        # Center image on white background
        x = (1600 - image.width) // 2
        y = (1600 - image.height) // 2
        white_bg.paste(image, (x, y), image if image.mode == 'RGBA' else None)

        return white_bg

    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        # Apply subtle blur and then sharpen to reduce noise while maintaining detail
        from PIL import ImageFilter

        # Very light blur to reduce noise
        blurred = image.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Blend original with blurred (80% original, 20% blurred)
        from PIL import Image as PILImage
        result = PILImage.blend(image, blurred, alpha=0.2)

        # Apply unsharp mask to restore sharpness
        enhancer = self.processor.enhance_colors(result, {'sharpness': 1.1})

        return result

class PipelineFactory:
    _pipelines = {
        'amazon': AmazonPipeline,
        'instagram': InstagramPipeline,
        'ebay': EbayPipeline
    }

    @classmethod
    def create_pipeline(cls, pipeline_type: str, processor: ImageProcessor) -> BasePipeline:
        if pipeline_type not in cls._pipelines:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}. Available: {list(cls._pipelines.keys())}")

        return cls._pipelines[pipeline_type](processor)

    @classmethod
    def get_available_pipelines(cls) -> Dict[str, Dict[str, Any]]:
        processor = ImageProcessor()  # Temporary processor for info
        pipelines_info = {}

        for name, pipeline_class in cls._pipelines.items():
            pipeline = pipeline_class(processor)
            pipelines_info[name] = pipeline.get_pipeline_info()

        return pipelines_info

    @classmethod
    def register_pipeline(cls, name: str, pipeline_class: type):
        """Register a custom pipeline"""
        if not issubclass(pipeline_class, BasePipeline):
            raise ValueError("Pipeline class must inherit from BasePipeline")

        cls._pipelines[name] = pipeline_class