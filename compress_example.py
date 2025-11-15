"""Example usage of the image compressor module."""

from typing import Dict, Any
from image_compressor import ImageCompressor, compress_image


def main() -> None:
    """Demonstrate image compression with various options."""
    
    print("=" * 60)
    print("Image Compressor - Example Usage")
    print("=" * 60)
    
    # Example 1: Quick compression to 1080p
    print("\n1️⃣  Quick compression to 1080p:")
    print("-" * 60)
    
    # Note: Replace with actual image path
    source_image: str = "cpu_usage_report.png"
    output_image: str = "cpu_usage_report_1080p.png"
    
    try:
        result: Dict[str, Any] = compress_image(
            source=source_image,
            output=output_image,
            target_resolution='1080p',
            quality=85,
            maintain_aspect=True
        )
        
        print(f"✓ Compression complete!")
        print(f"  Source:    {result['source_resolution']} ({result['source_size_mb']}MB)")
        print(f"  Target:    {result['target_resolution']} ({result['output_size_mb']}MB)")
        print(f"  Ratio:     {result['compression_ratio']}x smaller")
        print(f"  Format:    {result['output_format']}")
        print(f"  Output:    {result['output_path']}")
    except FileNotFoundError as e:
        print(f"⚠ {e}")
    
    # Example 2: Using presets
    print("\n\n2️⃣  Available resolution presets:")
    print("-" * 60)
    
    for preset, (width, height) in ImageCompressor.PRESETS.items():
        print(f"  {preset:8} → {width}x{height}")
    
    # Example 3: Batch compression
    print("\n\n3️⃣  Batch compression to multiple resolutions:")
    print("-" * 60)
    
    try:
        compressor: ImageCompressor = ImageCompressor.from_preset(
            source_image,
            '1080p',
            quality=85
        )
        
        results: list[Dict[str, Any]] = compressor.compress_batch(
            output_dir='compressed_images',
            output_format='jpg',
            maintain_aspect=True
        )
        
        print(f"✓ Generated {len(results)} compressed versions:")
        for result in results:
            print(f"\n  {result['target_resolution']}:")
            print(f"    Size: {result['source_size_mb']}MB → {result['output_size_mb']}MB")
            print(f"    File: {result['output_path']}")
    except FileNotFoundError as e:
        print(f"⚠ {e}")
    
    # Example 4: Get image info
    print("\n\n4️⃣  Source image information:")
    print("-" * 60)
    
    try:
        compressor: ImageCompressor = ImageCompressor(source_image)
        info: Dict[str, Any] = compressor.get_source_info()
        
        print(f"  Resolution: {info['width']}x{info['height']}")
        print(f"  Format:     {info['format']}")
        print(f"  Size:       {info['size_mb']:.2f}MB")
    except FileNotFoundError as e:
        print(f"⚠ {e}")
    
    print("\n" + "=" * 60)
    print("For more information, see the README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
