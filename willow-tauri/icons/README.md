# Willow Desktop Icons

This directory should contain the application icons in various formats:

## Required Icons

- `32x32.png` - Small icon for system tray
- `128x128.png` - Standard icon
- `128x128@2x.png` - High-DPI icon
- `icon.icns` - macOS icon bundle
- `icon.ico` - Windows icon
- `icon.png` - Linux/general purpose icon

## Creating Icons

You can create these icons from a high-resolution source image (512x512 or higher) using:

### Online Tools

- [ICO Convert](https://icoconvert.com/) - Convert to .ico format
- [CloudConvert](https://cloudconvert.com/) - Multi-format conversion
- [App Icon Generator](https://appicon.co/) - Generate all required sizes

### Command Line (ImageMagick)

```bash
# Install ImageMagick first
# Convert source.png to different sizes
convert source.png -resize 32x32 32x32.png
convert source.png -resize 128x128 128x128.png
convert source.png -resize 256x256 128x128@2x.png
convert source.png -resize 512x512 icon.png

# For Windows ICO (multiple sizes in one file)
convert source.png -resize 16x16 -resize 32x32 -resize 48x48 -resize 64x64 icon.ico

# For macOS ICNS (requires additional tools)
# Use `iconutil` on macOS or online converters
```

## Temporary Placeholder

For now, you can use a placeholder or copy icons from the main Willow project.
The application will use default system icons if these files are not found.

## Icon Design Guidelines

- Use the Willow tree emoji 🌲 or a stylized tree icon
- Green color scheme to match Willow branding
- Simple, recognizable design at small sizes
- Consistent with the application's visual identity
