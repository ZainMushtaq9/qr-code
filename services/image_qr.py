"""Image QR Code Generator — Star Feature
Embeds user-uploaded images into QR codes using 3 styles:
  - center: logo/image placed in center of QR
  - blend: image colors used as QR texture
  - background: image as QR background
All use ERROR_CORRECT_H (30% damage tolerance) for reliable scanning.
"""
import io
import base64
import qrcode
from PIL import Image, ImageChops, ImageDraw, ImageFilter


def generate_image_qr(image_file, qr_data, style="center",
                      fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    """
    Generate an Image QR code.

    Args:
        image_file: file-like object (uploaded image)
        qr_data: string to encode (URL, text, etc.)
        style: 'center' | 'blend' | 'background'
        fg_color: QR foreground color hex
        bg_color: QR background color hex
        dot_shape: 'square' | 'circle' | 'gapped'

    Returns:
        dict with 'image' (base64 PNG) and 'success' bool
    """
    try:
        # ── Open & normalize the uploaded image ────────────────
        user_img = Image.open(image_file).convert("RGBA")
        user_img = user_img.resize((300, 300), Image.LANCZOS)

        # ── Generate base QR with HIGH error correction ────────
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # ── Style: CENTER — image overlay in middle ────────────
        if style == "center":
            qr_img = qr.make_image(
                fill_color=fg_color, back_color=bg_color
            ).convert("RGBA")
            qr_w, qr_h = qr_img.size

            # Logo takes up ~25% of QR — within 30% error correction limit
            logo_size = min(qr_w, qr_h) // 4
            logo = user_img.resize((logo_size, logo_size), Image.LANCZOS)

            # Create circular mask for cleaner look
            mask = Image.new("L", (logo_size, logo_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                [0, 0, logo_size - 1, logo_size - 1],
                radius=logo_size // 8,
                fill=255,
            )

            # White background behind logo for contrast
            white_pad = 8
            white_bg = Image.new("RGBA",
                                 (logo_size + white_pad * 2, logo_size + white_pad * 2),
                                 (255, 255, 255, 255))
            pos_logo = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
            pos_bg = (pos_logo[0] - white_pad, pos_logo[1] - white_pad)

            qr_img.paste(white_bg, pos_bg)
            qr_img.paste(logo, pos_logo, mask)

        # ── Style: BLEND — image texture on QR modules ────────
        elif style == "blend":
            qr_img = qr.make_image(
                fill_color=fg_color, back_color=bg_color
            ).convert("RGBA")
            img_full = user_img.resize(qr_img.size, Image.LANCZOS)

            # Multiply blend: QR pattern × image texture
            blended = ImageChops.multiply(qr_img, img_full)

            # Keep white background where QR is white
            bg = Image.new("RGBA", qr_img.size, bg_color)
            # Use QR as mask — dark modules get image texture
            qr_gray = qr_img.convert("L")
            # Invert: white=0 (bg), black=255 (modules)
            qr_mask = Image.eval(qr_gray, lambda x: 255 if x < 128 else 0)

            bg.paste(blended, (0, 0), qr_mask)
            qr_img = bg

        # ── Style: BACKGROUND — image behind QR ───────────────
        elif style == "background":
            qr_img = qr.make_image(
                fill_color=fg_color,
                back_color=(255, 255, 255, 0),
            ).convert("RGBA")

            bg = user_img.resize(qr_img.size, Image.LANCZOS).convert("RGBA")
            # Lighten the background so QR is scannable
            enhancer = Image.blend(
                bg,
                Image.new("RGBA", bg.size, (255, 255, 255, 200)),
                alpha=0.5,
            )
            enhancer.paste(qr_img, (0, 0), qr_img)
            qr_img = enhancer

        else:
            return {"success": False, "error": f"Unknown style: {style}"}

        # ── Convert to base64 PNG ──────────────────────────────
        buf = io.BytesIO()
        final = qr_img.convert("RGB")
        final.save(buf, format="PNG", quality=95)
        b64 = base64.b64encode(buf.getvalue()).decode()

        return {"image": b64, "success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
