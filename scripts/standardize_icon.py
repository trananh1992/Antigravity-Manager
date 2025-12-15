import os
import subprocess
from PIL import Image, ImageDraw

def create_squircle_mask(size, radius_ratio=0.2):
    """
    Creates a squircle (continuous curvature rounded rect) mask.
    For simplicity, we uses a standard rounded rectangle which is close enough for most cases,
    or we can draw a superellipse. Here we use a high-quality rounded rect.
    """
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    # Draw a rounded rectangle
    # radius usually ~18-22% for macOS icons
    radius = int(min(w, h) * radius_ratio)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    return mask

def process_icon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    icons_dir = os.path.join(project_root, 'src-tauri', 'icons')
    source_icon_path = os.path.join(icons_dir, 'icon.png')
    
    if not os.path.exists(source_icon_path):
        print(f"Error: Source icon not found at {source_icon_path}")
        return

    print("Processing icon...")
    original = Image.open(source_icon_path).convert('RGBA')
    
    # macOS standard: Canvas 1024x1024. Actual icon content ~824x824 (approx 80%) to leave room for shadows/padding.
    CANVAS_SIZE = 1024
    CONTENT_SIZE = 824 
    
    # Resize original to CONTENT_SIZE
    # Use LANCZOS for high quality downsampling
    resized_content = original.resize((CONTENT_SIZE, CONTENT_SIZE), Image.Resampling.LANCZOS)
    
    # Create mask
    mask = create_squircle_mask((CONTENT_SIZE, CONTENT_SIZE))
    
    # Apply mask
    resized_content.putalpha(mask)
    
    # Create final canvas
    final_icon = Image.new('RGBA', (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    
    # Paste centered
    offset = ((CANVAS_SIZE - CONTENT_SIZE) // 2, (CANVAS_SIZE - CONTENT_SIZE) // 2)
    final_icon.paste(resized_content, offset, resized_content)
    
    # Save master icon
    master_icon_path = os.path.join(icons_dir, 'icon_master_squircle.png')
    final_icon.save(master_icon_path)
    print(f"Saved master icon to {master_icon_path}")

    # Generate .iconset for macOS
    iconset_dir = os.path.join(icons_dir, 'icon.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    sizes = [16, 32, 128, 256, 512]
    for size in sizes:
        # standard size
        img = final_icon.resize((size, size), Image.Resampling.LANCZOS)
        img.save(os.path.join(iconset_dir, f'icon_{size}x{size}.png'))
        
        # @2x size
        img_2x = final_icon.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
        img_2x.save(os.path.join(iconset_dir, f'icon_{size}x{size}@2x.png'))

    # Generate icns using iconutil
    print("Generating .icns...")
    try:
        subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', os.path.join(icons_dir, 'icon.icns')], check=True)
        print("Generated icon.icns")
    except subprocess.CalledProcessError:
        print("Error: Failed to run iconutil. Are you on macOS?")
    except FileNotFoundError:
        print("Error: iconutil not found.")

    # Generate .ico for Windows (sizes: 16, 32, 48, 64, 128, 256)
    print("Generating .ico...")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    final_icon.save(os.path.join(icons_dir, 'icon.ico'), format='ICO', sizes=ico_sizes)
    print("Generated icon.ico")

    # Generate standard pngs for Tauri
    # Tauri usually looks for 32x32.png, 128x128.png, 128x128@2x.png, icon.png
    print("Generating standard PNGs...")
    final_icon.save(os.path.join(icons_dir, 'icon.png')) # Overwrite main png
    
    final_icon.resize((32, 32), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, '32x32.png'))
    final_icon.resize((128, 128), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, '128x128.png'))
    final_icon.resize((256, 256), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, '128x128@2x.png')) # Tauri often uses this name for 256
    
    # Generate tray icon
    print("Generating tray icon...")
    # Standard macOS menu bar icon size is usually 22x22 pts.
    # We generate a standard one.
    # Note: User requested "unified rounded corners", so we use the squircle version.
    # We'll generate 22x22. 
    tray_size = 22
    tray_icon = final_icon.resize((tray_size, tray_size), Image.Resampling.LANCZOS)
    tray_icon.save(os.path.join(icons_dir, 'tray-icon.png'))
    
    # Also generate a large one just in case user wants to swap, but code uses 'tray-icon.png'
    # tray_icon_2x = final_icon.resize((44, 44), Image.Resampling.LANCZOS)
    # tray_icon_2x.save(os.path.join(icons_dir, 'tray-icon@2x.png'))

    # Cleanup iconset dir
    # import shutil
    # shutil.rmtree(iconset_dir)
    print("Done! Icons updated.")

if __name__ == '__main__':
    process_icon()
