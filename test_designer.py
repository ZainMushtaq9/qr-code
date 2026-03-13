"""Test script for Modern Designer QR API."""
from app import create_app

app = create_app()

tests = [
    ("dots + no shape", {"qr_data": "https://test.com", "style": "dots", "shape": "none", "fg_color": "#000000", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "", "image_style": "overlay", "category": ""}),
    ("dots + circle shape", {"qr_data": "https://test.com", "style": "dots", "shape": "circle", "fg_color": "#e63946", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "Scan Me", "image_style": "overlay", "category": ""}),
    ("lines + car shape", {"qr_data": "https://test.com", "style": "lines", "shape": "car", "fg_color": "#1a73e8", "bg_color": "#FFFFFF", "gradient_color": "#000088", "frame_text": "Car Wash", "image_style": "overlay", "category": ""}),
    ("rounded + heart", {"qr_data": "https://test.com", "style": "rounded", "shape": "heart", "fg_color": "#ad1457", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "Scan Me", "image_style": "overlay", "category": ""}),
    ("category=cafe", {"qr_data": "https://test.com", "style": "dots", "shape": "none", "fg_color": "#000000", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "", "image_style": "overlay", "category": "cafe"}),
    ("category=car_wash", {"qr_data": "https://test.com", "style": "dots", "shape": "none", "fg_color": "#000000", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "", "image_style": "overlay", "category": "car_wash"}),
    ("category=medical_shop", {"qr_data": "https://test.com", "style": "dots", "shape": "none", "fg_color": "#000000", "bg_color": "#FFFFFF", "gradient_color": "", "frame_text": "", "image_style": "overlay", "category": "medical_shop"}),
    ("SVG export", None),
]

with app.test_client() as c:
    all_ok = True
    for name, data in tests:
        if name == "SVG export":
            resp = c.post("/generate-designer-svg", json={"qr_data": "https://test.com", "style": "dots"})
            ok = resp.status_code == 200 and b"<svg" in resp.data
            print(f"  {'OK' if ok else 'FAIL'} {name}: status={resp.status_code}, svg_len={len(resp.data)}")
        else:
            resp = c.post("/generate-designer-qr", data=data, content_type="multipart/form-data")
            r = resp.get_json()
            ok = bool(r and r.get("success"))
            img_len = len(r.get("image", "")) if r else 0
            err = r.get("error") if r else str(resp.data[:80])
            print(f"  {'OK' if ok else 'FAIL'} {name}: success={ok}, img_len={img_len}, err={err}")
        if not ok:
            all_ok = False

    print()
    print("  --- ALL TESTS PASSED ---" if all_ok else "  *** SOME TESTS FAILED ***")
