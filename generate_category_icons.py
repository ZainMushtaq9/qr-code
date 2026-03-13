import os
import sys

# ensure path
os.makedirs(os.path.join("static", "category_images"), exist_ok=True)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL not installed, skipping.")
    sys.exit(1)

categories = [
    ("car_wash", "C", "#1a73e8", "#ffffff"),
    ("mobile_shop", "M", "#6a0572", "#ffffff"),
    ("computer_shop", "C", "#264653", "#ffffff"),
    ("medical_shop", "M", "#e63946", "#ffffff"),
    ("restaurant", "R", "#d62828", "#fff3e0"),
    ("cafe", "C", "#5d4037", "#fff8e1"),
    ("salon", "S", "#ad1457", "#fce4ec"),
    ("gym", "G", "#1b5e20", "#e8f5e9"),
    ("real_estate", "H", "#0d47a1", "#e3f2fd"),
    ("education", "E", "#ff6f00", "#fff3e0"),
    ("grocery", "G", "#2e7d32", "#ffffff"),
    ("photography", "P", "#37474f", "#ffffff"),
    ("pizza", "P", "#e65100", "#fff3e0"),
]

for cat_id, letter, fg, bg in categories:
    img = Image.new("RGBA", (400, 400), bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 250)
    except:
        font = ImageFont.load_default()
    
    # Draw letter in center
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (400 - tw) / 2
    y = (400 - th) / 2
    draw.text((x, y - (th/4)), letter, fill=fg, font=font)
    
    # Add a border
    draw.rectangle([20, 20, 380, 380], outline=fg, width=20)
    
    path = os.path.join("static", "category_images", f"{cat_id}.png")
    img.save(path)

print("Icons created successfully.")
