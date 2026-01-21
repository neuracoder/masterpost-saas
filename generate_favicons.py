"""
Generate favicon PNG files from public/logo-masterpost.png
Ensures the result is square by adding transparent padding if needed.
Requires: pip install pillow
"""

try:
    from PIL import Image
    import os

    source_path = 'public/logo-masterpost.png'
    
    if not os.path.exists(source_path):
        print(f"❌ Error: {source_path} not found.")
        exit(1)

    print(f"Loading {source_path}...")
    img = Image.open(source_path)
    
    # Ensure image is in RGBA
    img = img.convert("RGBA")
    
    # Make it square
    width, height = img.size
    max_dim = max(width, height)
    
    # Create a new square transparent background
    square_img = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
    
    # Center the original image
    offset_x = (max_dim - width) // 2
    offset_y = (max_dim - height) // 2
    square_img.paste(img, (offset_x, offset_y), img)
    
    print(f"Original size: {width}x{height}. Squared to: {max_dim}x{max_dim}")

    # Save different sizes
    sizes = {
        'favicon-48x48.png': 48,
        'favicon-96x96.png': 96,
        'favicon-144x144.png': 144,
        'android-chrome-512x512.png': 512,
        'android-chrome-192x192.png': 192,
        'apple-touch-icon.png': 180,
        'favicon-32x32.png': 32,
        'favicon-16x16.png': 16,
    }

    for filename, size in sizes.items():
        resized = square_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'public/{filename}')
        print(f'✓ Generated {filename} ({size}x{size})')

    # Generate .ico file with multiple sizes
    ico_img_16 = square_img.resize((16, 16), Image.Resampling.LANCZOS)
    ico_img_32 = square_img.resize((32, 32), Image.Resampling.LANCZOS)
    ico_img_48 = square_img.resize((48, 48), Image.Resampling.LANCZOS)
    
    # Save as ICO containing 16, 32, 48
    ico_img_48.save('public/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print('✓ Generated favicon.ico (16x16, 32x32, 48x48)')

    print('\n✅ All favicons generated successfully!')

except ImportError:
    print('❌ Error: Pillow not confirmed installed.')
    print('Run: pip install pillow')
except Exception as e:
    print(f'❌ Error: {e}')
