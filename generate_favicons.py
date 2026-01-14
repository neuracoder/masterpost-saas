"""
Generate favicon PNG files from SVG
Requires: pip install cairosvg pillow
"""

try:
    from cairosvg import svg2png
    from PIL import Image
    import io

    # SVG content
    svg_content = """<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
      <!-- Green background with rounded corners -->
      <rect width="512" height="512" rx="102" fill="#10b981"/>
      <!-- Yellow border -->
      <rect x="16" y="16" width="480" height="480" rx="90" fill="none" stroke="#fbbf24" stroke-width="32"/>
      <!-- White M letter -->
      <text x="256" y="370" font-family="Arial, sans-serif" font-size="320" font-weight="bold" fill="white" text-anchor="middle">M</text>
    </svg>"""

    # Generate base 512x512 PNG
    png_data = svg2png(bytestring=svg_content.encode('utf-8'))
    base_img = Image.open(io.BytesIO(png_data))

    # Save different sizes
    sizes = {
        'android-chrome-512x512.png': 512,
        'android-chrome-192x192.png': 192,
        'apple-touch-icon.png': 180,
        'favicon-32x32.png': 32,
        'favicon-16x16.png': 16,
    }

    for filename, size in sizes.items():
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'public/{filename}')
        print(f'✓ Generated {filename} ({size}x{size})')

    # Generate .ico file with multiple sizes
    ico_img = base_img.resize((32, 32), Image.Resampling.LANCZOS)
    ico_img.save('public/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32)])
    print('✓ Generated favicon.ico (16x16, 32x32)')

    print('\n✅ All favicons generated successfully!')
    print('📁 Files saved in public/ directory')

except ImportError:
    print('❌ Error: Required packages not installed')
    print('Run: pip install cairosvg pillow')
    print('\n📝 Alternative: Manual PNG creation needed')
    print('Use an online SVG to PNG converter:')
    print('1. Open public/favicon.svg in browser')
    print('2. Use https://cloudconvert.com/svg-to-png')
    print('3. Convert to sizes: 16, 32, 180, 192, 512')
    print('4. Save as specified filenames in public/')
