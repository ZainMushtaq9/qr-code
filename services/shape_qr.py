"""Shape-Based QR Code Generator — Mask Overlay Engine
Creates QR codes that follow specific shapes (pizza, car, coffee, camera, etc.)
by using a mask overlay to determine which modules are visible.
Also supports dot, rounded, line styles, gradients, and frame text.
"""
import io
import base64
import math
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# ── Shape mask definitions (programmatic — no external files needed) ──

def _create_circle_mask(size):
    """Circle/pizza shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    draw.ellipse([0, 0, size-1, size-1], fill=255)
    return img

def _create_heart_mask(size):
    """Heart shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    # Heart using polygon points
    points = []
    for t_deg in range(360):
        t = math.radians(t_deg)
        x = 16 * math.sin(t)**3
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        px = int(cx + x * size / 40)
        py = int(cy + y * size / 40 - size * 0.05)
        points.append((px, py))
    draw.polygon(points, fill=255)
    return img

def _create_car_mask(size):
    """Car silhouette"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    w, h = size, size
    # Car body
    draw.rounded_rectangle([w*0.05, h*0.35, w*0.95, h*0.75], radius=int(w*0.05), fill=255)
    # Car roof
    draw.rounded_rectangle([w*0.2, h*0.15, w*0.75, h*0.45], radius=int(w*0.08), fill=255)
    # Wheels
    r = int(w * 0.1)
    draw.ellipse([w*0.12-r, h*0.7-r, w*0.12+r, h*0.7+r], fill=0)
    draw.ellipse([w*0.12-r, h*0.7-r, w*0.12+r, h*0.7+r], outline=255, width=3)
    draw.ellipse([w*0.85-r, h*0.7-r, w*0.85+r, h*0.7+r], fill=0)
    draw.ellipse([w*0.85-r, h*0.7-r, w*0.85+r, h*0.7+r], outline=255, width=3)
    return img

def _create_coffee_mask(size):
    """Coffee cup shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    w, h = size, size
    # Cup body (trapezoid)
    draw.polygon([(w*0.2, h*0.25), (w*0.8, h*0.25), (w*0.7, h*0.85), (w*0.3, h*0.85)], fill=255)
    # Cup rim
    draw.rounded_rectangle([w*0.15, h*0.2, w*0.85, h*0.32], radius=int(w*0.03), fill=255)
    # Handle
    draw.arc([w*0.75, h*0.35, w*0.95, h*0.6], start=-90, end=90, fill=255, width=int(w*0.04))
    # Saucer
    draw.ellipse([w*0.15, h*0.82, w*0.85, h*0.95], fill=255)
    return img

def _create_camera_mask(size):
    """Camera shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    w, h = size, size
    # Camera body
    draw.rounded_rectangle([w*0.08, h*0.3, w*0.92, h*0.85], radius=int(w*0.06), fill=255)
    # Lens bump top
    draw.rounded_rectangle([w*0.3, h*0.18, w*0.7, h*0.38], radius=int(w*0.04), fill=255)
    # Lens circle
    r = int(w * 0.18)
    cx, cy = int(w * 0.5), int(h * 0.58)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=200)
    draw.ellipse([cx-r+8, cy-r+8, cx+r-8, cy+r-8], fill=255)
    return img

def _create_shopping_bag_mask(size):
    """Shopping bag shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    w, h = size, size
    # Bag body
    draw.rounded_rectangle([w*0.15, h*0.3, w*0.85, h*0.92], radius=int(w*0.04), fill=255)
    # Handle
    draw.arc([w*0.3, h*0.1, w*0.7, h*0.4], start=180, end=0, fill=255, width=int(w*0.04))
    return img

def _create_star_mask(size):
    """Star shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r_outer = size * 0.48
    r_inner = size * 0.2
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=255)
    return img

def _create_diamond_mask(size):
    """Diamond shape"""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    s = size * 0.45
    draw.polygon([(cx, cy-s), (cx+s, cy), (cx, cy+s), (cx-s, cy)], fill=255)
    return img


SHAPE_GENERATORS = {
    "circle": _create_circle_mask,
    "pizza": _create_circle_mask,  # Pizza = circle with texture
    "heart": _create_heart_mask,
    "car": _create_car_mask,
    "coffee": _create_coffee_mask,
    "camera": _create_camera_mask,
    "shopping_bag": _create_shopping_bag_mask,
    "star": _create_star_mask,
    "diamond": _create_diamond_mask,
}


def _get_finder_pattern_regions(qr_matrix_size, box_size, border):
    """Returns list of (x1,y1,x2,y2) regions for the 3 finder patterns that must be protected."""
    finder_size = 7  # QR finder patterns are always 7 modules
    regions = []
    for (row, col) in [(0, 0), (0, qr_matrix_size - finder_size), (qr_matrix_size - finder_size, 0)]:
        x1 = (col + border) * box_size
        y1 = (row + border) * box_size
        x2 = x1 + finder_size * box_size
        y2 = y1 + finder_size * box_size
        # Add 1-module padding around finders
        pad = box_size
        regions.append((max(0, x1 - pad), max(0, y1 - pad), x2 + pad, y2 + pad))
    return regions


def _is_in_finder(x, y, finder_regions):
    """Check if pixel coordinates fall within any finder pattern region."""
    for (x1, y1, x2, y2) in finder_regions:
        if x1 <= x < x2 and y1 <= y < y2:
            return True
    return False


def generate_modern_qr(
    data,
    style="dots",           # dots | rounded | lines | classic
    shape="none",           # none | circle | heart | car | coffee | camera | shopping_bag | star | diamond
    fg_color="#000000",
    bg_color="#FFFFFF",
    gradient_color="",      # if set, gradient from fg_color to this
    gradient_type="linear", # linear | radial
    frame_text="",          # e.g. "Scan Me"
    logo_file=None,         # file-like object for center logo
    image_file=None,        # file-like object for image-art QR
    image_style="overlay",  # overlay | halftone | blend
    box_size=10,
    border=4,
):
    """Generate a modern designer QR code with various styles and shapes."""
    try:
        # ── Step 1: Generate QR matrix with Error Correction H ──
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        mat_size = len(matrix)

        total_size = (mat_size + border * 2) * box_size
        img = Image.new("RGBA", (total_size, total_size), bg_color)
        draw = ImageDraw.Draw(img)

        # ── Step 2: Determine finder pattern regions ──
        finder_regions = _get_finder_pattern_regions(mat_size, box_size, border)

        # ── Step 3: Create shape mask if needed ──
        shape_mask = None
        if shape != "none" and shape in SHAPE_GENERATORS:
            shape_mask = SHAPE_GENERATORS[shape](total_size)

        # ── Step 4: Generate gradient colors if needed ──
        def get_module_color(row, col, total_rows, total_cols):
            if not gradient_color:
                return fg_color
            # Parse colors
            def hex_to_rgb(h):
                h = h.lstrip('#')
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            c1 = hex_to_rgb(fg_color)
            c2 = hex_to_rgb(gradient_color)
            if gradient_type == "radial":
                cx, cy = total_cols / 2, total_rows / 2
                dist = math.sqrt((col - cx)**2 + (row - cy)**2)
                max_dist = math.sqrt(cx**2 + cy**2)
                t = min(dist / max_dist, 1.0)
            else:  # linear
                t = row / max(total_rows - 1, 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            return f"#{r:02x}{g:02x}{b:02x}"

        # ── Step 5: Render QR modules with selected style ──
        for row_idx, row in enumerate(matrix):
            for col_idx, module in enumerate(row):
                if not module:
                    continue  # Skip white modules

                px = (col_idx + border) * box_size
                py = (row_idx + border) * box_size
                cx = px + box_size // 2
                cy = py + box_size // 2

                # Check shape mask
                if shape_mask:
                    mask_val = shape_mask.getpixel((min(cx, total_size - 1), min(cy, total_size - 1)))
                    # Always show finder patterns regardless of mask
                    if mask_val < 128 and not _is_in_finder(px, py, finder_regions):
                        continue

                color = get_module_color(row_idx, col_idx, mat_size, mat_size)

                # Finder patterns always rendered as classic squares
                if _is_in_finder(px, py, finder_regions):
                    draw.rectangle([px, py, px + box_size - 1, py + box_size - 1], fill=color)
                    continue

                # Apply style
                if style == "dots":
                    r = box_size * 0.4
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
                elif style == "rounded":
                    r = box_size // 4
                    draw.rounded_rectangle([px + 1, py + 1, px + box_size - 2, py + box_size - 2],
                                           radius=r, fill=color)
                elif style == "lines":
                    # Thin vertical line
                    lw = max(2, box_size // 3)
                    draw.rectangle([cx - lw // 2, py, cx + lw // 2, py + box_size - 1], fill=color)
                elif style == "diamond":
                    s = box_size * 0.4
                    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=color)
                elif style == "star":
                    s = box_size * 0.4
                    points = []
                    for i in range(10):
                        angle = math.radians(i * 36 - 90)
                        r2 = s if i % 2 == 0 else s * 0.4
                        points.append((cx + r2 * math.cos(angle), cy + r2 * math.sin(angle)))
                    draw.polygon(points, fill=color)
                else:  # classic
                    draw.rectangle([px, py, px + box_size - 1, py + box_size - 1], fill=color)

        # ── Step 6: Apply image overlay if provided ──
        if image_file:
            user_img = Image.open(image_file).convert("RGBA")

            if image_style == "halftone":
                # Portrait-art style: convert image to grayscale, use as density mask
                gray = user_img.convert("L").resize((total_size, total_size), Image.LANCZOS)
                # Make QR modules vary in size based on image brightness
                img_halftone = Image.new("RGBA", (total_size, total_size), bg_color)
                draw_ht = ImageDraw.Draw(img_halftone)

                for row_idx, row in enumerate(matrix):
                    for col_idx, module in enumerate(row):
                        if not module:
                            continue
                        px = (col_idx + border) * box_size
                        py = (row_idx + border) * box_size
                        cx_m = px + box_size // 2
                        cy_m = py + box_size // 2

                        if shape_mask:
                            mask_val = shape_mask.getpixel((min(cx_m, total_size-1), min(cy_m, total_size-1)))
                            if mask_val < 128 and not _is_in_finder(px, py, finder_regions):
                                continue

                        # Get image brightness at this point
                        brightness = gray.getpixel((min(cx_m, total_size-1), min(cy_m, total_size-1)))
                        # Darker pixels = larger modules, lighter = smaller
                        scale = 0.2 + (1.0 - brightness / 255.0) * 0.8
                        r_mod = box_size * 0.45 * scale

                        color = get_module_color(row_idx, col_idx, mat_size, mat_size)

                        if _is_in_finder(px, py, finder_regions):
                            draw_ht.rectangle([px, py, px + box_size - 1, py + box_size - 1], fill=fg_color)
                        else:
                            draw_ht.ellipse([cx_m - r_mod, cy_m - r_mod, cx_m + r_mod, cy_m + r_mod], fill=color)

                img = img_halftone

            elif image_style == "blend":
                # Multiply blend
                user_resized = user_img.resize((total_size, total_size), Image.LANCZOS)
                from PIL import ImageChops
                img = ImageChops.multiply(img.convert("RGBA"), user_resized.convert("RGBA"))

            else:  # overlay — image as background, QR on top
                user_resized = user_img.resize((total_size, total_size), Image.LANCZOS).convert("RGBA")
                # Lighten background
                lightened = Image.blend(user_resized, Image.new("RGBA", user_resized.size, (255,255,255,200)), 0.4)
                lightened.paste(img, (0, 0), img)
                img = lightened

        # ── Step 7: Add center logo if provided ──
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            logo_size = total_size // 5  # 20% of QR
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            # White background behind logo
            pad = 8
            white_bg = Image.new("RGBA", (logo_size + pad*2, logo_size + pad*2), (255,255,255,255))
            pos = ((total_size - logo_size) // 2, (total_size - logo_size) // 2)
            pos_bg = (pos[0] - pad, pos[1] - pad)
            img.paste(white_bg, pos_bg)
            img.paste(logo, pos, logo)

        # ── Step 8: Add frame text if provided ──
        if frame_text:
            # Expand image to add text bar at bottom
            text_height = 40
            framed = Image.new("RGBA", (total_size, total_size + text_height), bg_color)
            framed.paste(img, (0, 0))
            draw_frame = ImageDraw.Draw(framed)
            # Draw text bar
            draw_frame.rectangle([0, total_size, total_size, total_size + text_height], fill=fg_color)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            bbox = draw_frame.textbbox((0, 0), frame_text, font=font)
            tw = bbox[2] - bbox[0]
            tx = (total_size - tw) // 2
            draw_frame.text((tx, total_size + 8), frame_text, fill=bg_color, font=font)
            img = framed

        # ── Step 9: Convert to base64 ──
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG", quality=95)
        b64 = base64.b64encode(buf.getvalue()).decode()

        return {"image": b64, "success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_modern_qr_svg(data, style="dots", fg_color="#000000", bg_color="#FFFFFF",
                           shape="none", box_size=10, border=4):
    """Generate SVG version of modern QR code for scalable output."""
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=1,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        mat_size = len(matrix)
        total = mat_size + border * 2
        svg_size = total * box_size

        finder_regions = _get_finder_pattern_regions(mat_size, box_size, border)
        shape_mask = None
        if shape != "none" and shape in SHAPE_GENERATORS:
            shape_mask = SHAPE_GENERATORS[shape](svg_size)

        elements = []
        for row_idx, row in enumerate(matrix):
            for col_idx, module in enumerate(row):
                if not module:
                    continue
                px = (col_idx + border) * box_size
                py = (row_idx + border) * box_size
                cx = px + box_size // 2
                cy = py + box_size // 2

                if shape_mask:
                    mask_val = shape_mask.getpixel((min(cx, svg_size-1), min(cy, svg_size-1)))
                    if mask_val < 128 and not _is_in_finder(px, py, finder_regions):
                        continue

                if _is_in_finder(px, py, finder_regions) or style == "classic":
                    elements.append(f'<rect x="{px}" y="{py}" width="{box_size}" height="{box_size}" fill="{fg_color}"/>')
                elif style == "dots":
                    r = box_size * 0.4
                    elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fg_color}"/>')
                elif style == "rounded":
                    r = box_size // 4
                    elements.append(f'<rect x="{px+1}" y="{py+1}" width="{box_size-2}" height="{box_size-2}" rx="{r}" fill="{fg_color}"/>')
                elif style == "lines":
                    lw = max(2, box_size // 3)
                    elements.append(f'<rect x="{cx-lw//2}" y="{py}" width="{lw}" height="{box_size}" fill="{fg_color}"/>')
                elif style == "diamond":
                    s = box_size * 0.4
                    elements.append(f'<polygon points="{cx},{cy-s} {cx+s},{cy} {cx},{cy+s} {cx-s},{cy}" fill="{fg_color}"/>')

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_size} {svg_size}" width="{svg_size}" height="{svg_size}">
<rect width="{svg_size}" height="{svg_size}" fill="{bg_color}"/>
{"".join(elements)}
</svg>'''

        return {"svg": svg, "success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
