"""Image compression module for converting high-resolution images to target formats."""

from typing import Optional, Tuple
from pathlib import Path
import os

try:
    from PIL import Image
except ImportError:
    Image = None


class ImageCompressor:
    """Compress and resize images to target resolutions.
    
    Supports conversion from 4K and other high-resolution formats to standard
    resolutions like 1080p, 720p, or custom dimensions.
    
    Attributes:
        source_path: Path to the source image file.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        quality: JPEG/PNG quality (1-100), defaults to 85.
    """
    
    # Common resolution presets
    PRESETS: dict[str, Tuple[int, int]] = {
        '4K': (3840, 2160),
        '1440p': (2560, 1440),
        '1080p': (1920, 1080),
        '720p': (1280, 720),
        '480p': (854, 480),
        '360p': (640, 360),
    }
    
    def __init__(
        self,
        source_path: str,
        target_width: int = 1920,
        target_height: int = 1080,
        quality: int = 85
    ) -> None:
        """Initialize the image compressor.
        
        Args:
            source_path: Path to source image file.
            target_width: Target width in pixels. Defaults to 1920 (1080p).
            target_height: Target height in pixels. Defaults to 1080 (1080p).
            quality: Output quality (1-100). Defaults to 85.
            
        Raises:
            ImportError: If PIL/Pillow is not installed.
            FileNotFoundError: If source image doesn't exist.
        """
        if Image is None:
            raise ImportError(
                "PIL/Pillow is required. Install with: uv pip install Pillow"
            )
        
        self.source_path: str = source_path
        self.target_width: int = target_width
        self.target_height: int = target_height
        self.quality: int = max(1, min(100, quality))
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Image not found: {source_path}")
    
    @classmethod
    def from_preset(
        cls,
        source_path: str,
        preset: str = '1080p',
        quality: int = 85
    ) -> 'ImageCompressor':
        """Create compressor using resolution preset.
        
        Args:
            source_path: Path to source image file.
            preset: Resolution preset ('4K', '1080p', '720p', etc.).
            quality: Output quality (1-100).
            
        Returns:
            ImageCompressor instance with preset dimensions.
            
        Raises:
            ValueError: If preset is not recognized.
        """
        if preset not in cls.PRESETS:
            available: str = ', '.join(cls.PRESETS.keys())
            raise ValueError(
                f"Unknown preset '{preset}'. Available: {available}"
            )
        
        width, height = cls.PRESETS[preset]
        return cls(source_path, width, height, quality)
    
    def get_source_info(self) -> dict[str, any]:
        """Get source image information.
        
        Returns:
            Dictionary with image dimensions and format.
        """
        with Image.open(self.source_path) as img:
            width, height = img.size
            return {
                'width': width,
                'height': height,
                'format': img.format,
                'size_mb': os.path.getsize(self.source_path) / (1024 * 1024)
            }
    
    def _calculate_dimensions(
        self,
        maintain_aspect: bool = True
    ) -> Tuple[int, int]:
        """Calculate target dimensions maintaining aspect ratio.
        
        Args:
            maintain_aspect: If True, maintain source aspect ratio.
            
        Returns:
            Tuple of (width, height) for target image.
        """
        if not maintain_aspect:
            return (self.target_width, self.target_height)
        
        with Image.open(self.source_path) as img:
            src_width, src_height = img.size
            src_aspect: float = src_width / src_height
            target_aspect: float = self.target_width / self.target_height
            
            if src_aspect > target_aspect:
                # Source is wider, fit to width
                new_width: int = self.target_width
                new_height: int = int(new_width / src_aspect)
            else:
                # Source is taller, fit to height
                new_height: int = self.target_height
                new_width: int = int(new_height * src_aspect)
            
            return (new_width, new_height)
    
    def compress(
        self,
        output_path: str,
        maintain_aspect: bool = True,
        format: Optional[str] = None
    ) -> dict[str, any]:
        """Compress and resize image.
        
        Args:
            output_path: Path for output compressed image.
            maintain_aspect: If True, maintain source aspect ratio.
            format: Output format ('JPEG', 'PNG', 'WEBP'). Auto-detect if None.
            
        Returns:
            Dictionary with compression statistics.
            
        Raises:
            ValueError: If output format is invalid.
        """
        source_info: dict[str, any] = self.get_source_info()
        
        with Image.open(self.source_path) as img:
            # Convert RGBA to RGB if saving as JPEG
            if img.mode == 'RGBA' and (format == 'JPEG' or 'jpeg' in output_path.lower()):
                rgb_img: Image.Image = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            # Calculate and resize
            new_width, new_height = self._calculate_dimensions(maintain_aspect)
            resized: Image.Image = img.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # Determine output format
            output_format: str = format or self._detect_format(output_path)
            
            # Save with compression
            save_kwargs: dict[str, any] = {'optimize': True}
            if output_format.upper() in ['JPEG', 'JPG']:
                save_kwargs['quality'] = self.quality
            
            resized.save(output_path, format=output_format, **save_kwargs)
        
        output_size_mb: float = os.path.getsize(output_path) / (1024 * 1024)
        compression_ratio: float = source_info['size_mb'] / output_size_mb if output_size_mb > 0 else 0
        
        return {
            'source_resolution': f"{source_info['width']}x{source_info['height']}",
            'target_resolution': f"{new_width}x{new_height}",
            'source_size_mb': round(source_info['size_mb'], 2),
            'output_size_mb': round(output_size_mb, 2),
            'compression_ratio': round(compression_ratio, 2),
            'output_path': output_path,
            'output_format': output_format
        }
    
    @staticmethod
    def _detect_format(file_path: str) -> str:
        """Detect image format from file extension.
        
        Args:
            file_path: Path to image file.
            
        Returns:
            Image format string (JPEG, PNG, WEBP, etc.).
            
        Raises:
            ValueError: If format cannot be detected.
        """
        ext: str = Path(file_path).suffix.lower()
        format_map: dict[str, str] = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.webp': 'WEBP',
            '.gif': 'GIF',
            '.bmp': 'BMP',
        }
        
        if ext not in format_map:
            raise ValueError(
                f"Unsupported format: {ext}. "
                f"Supported: {', '.join(format_map.keys())}"
            )
        
        return format_map[ext]
    
    def compress_batch(
        self,
        output_dir: str,
        output_format: str = 'jpg',
        maintain_aspect: bool = True
    ) -> list[dict[str, any]]:
        """Process and compress to multiple resolutions.
        
        Args:
            output_dir: Directory to save compressed versions.
            output_format: Output file format ('jpg', 'png', 'webp').
            maintain_aspect: If True, maintain source aspect ratio.
            
        Returns:
            List of compression results for each resolution.
        """
        os.makedirs(output_dir, exist_ok=True)
        results: list[dict[str, any]] = []
        
        for preset_name in ['1080p', '720p', '480p']:
            compressor: ImageCompressor = self.from_preset(
                self.source_path,
                preset_name,
                self.quality
            )
            
            output_file: str = os.path.join(
                output_dir,
                f"image_{preset_name}.{output_format}"
            )
            
            result: dict[str, any] = compressor.compress(
                output_file,
                maintain_aspect,
                output_format.upper()
            )
            results.append(result)
        
        return results


def compress_image(
    source: str,
    output: str,
    target_resolution: str = '1080p',
    quality: int = 85,
    maintain_aspect: bool = True
) -> dict[str, any]:
    """Quick compression function.
    
    Args:
        source: Source image path.
        output: Output image path.
        target_resolution: Target resolution preset ('1080p', '720p', etc.).
        quality: Output quality (1-100).
        maintain_aspect: If True, maintain source aspect ratio.
        
    Returns:
        Compression statistics dictionary.
        
    Example:
        >>> result = compress_image(
        ...     'large_image.png',
        ...     'compressed.jpg',
        ...     '1080p',
        ...     quality=85
        ... )
        >>> print(f"Reduced from {result['source_size_mb']}MB to {result['output_size_mb']}MB")
    """
    compressor: ImageCompressor = ImageCompressor.from_preset(
        source,
        target_resolution,
        quality
    )
    return compressor.compress(output, maintain_aspect)
