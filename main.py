"""
Advertisement Creator - Flask Application

Web interface for generating advertisement images using FLUX.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import threading
from datetime import datetime

from prompts import build_prompts, AD_STYLES, AD_VARIANTS, AD_FORMATS, MESSAGING_STYLES, get_format_by_id
from generator import generate_image, add_brand_text, save_image, OUTPUT_DIR

app = Flask(__name__, template_folder=".")

# Track generation status
generation_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "current_variant": "",
    "results": [],
    "error": None,
}


@app.route("/")
def index():
    return render_template("index.html", styles=AD_STYLES, variants=AD_VARIANTS,
                           formats=AD_FORMATS, messaging_styles=MESSAGING_STYLES)


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/api/generate", methods=["POST"])
def generate():
    global generation_status

    if generation_status["running"]:
        return jsonify({"error": "Generation already in progress"}), 409

    data = request.json
    brand = data.get("brand", "").strip()
    product = data.get("product", "").strip()
    style = data.get("style", "").strip()
    feature = data.get("feature", "").strip()
    format_id = data.get("format", "instagram_post").strip()
    messaging_id = data.get("messaging", "informative").strip()
    description = data.get("description", "").strip()
    num_images = min(int(data.get("num_images", 1)), 5)
    selected_variants = data.get("variants", [])

    if not all([brand, product, style, feature]):
        return jsonify({"error": "All fields are required"}), 400

    if not selected_variants:
        return jsonify({"error": "Select at least one variant"}), 400

    ad_format = get_format_by_id(format_id)
    if not ad_format:
        return jsonify({"error": "Invalid ad format"}), 400

    total = len(selected_variants) * num_images

    # Reset status
    generation_status = {
        "running": True,
        "progress": 0,
        "total": total,
        "current_variant": "",
        "results": [],
        "error": None,
    }

    # Run generation in background thread
    thread = threading.Thread(
        target=_run_generation,
        args=(brand, product, style, feature, format_id, messaging_id, ad_format, num_images, selected_variants, description),
    )
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Generation started", "total": total})


def _run_generation(brand, product, style, feature, format_id, messaging_id, ad_format, num_images, selected_variants, description):
    global generation_status

    try:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_prompts = build_prompts(brand, product, style, feature, messaging_id, description)
        prompts = [p for p in all_prompts if p["name"] in selected_variants]
        data = {
            "brand": brand, "product": product, "style": style,
            "feature": feature, "format": format_id, "messaging": messaging_id,
        }

        count = 0
        for i, variant in enumerate(prompts, start=1):
            for img_num in range(1, num_images + 1):
                count += 1
                label = f"{variant['name']} #{img_num}" if num_images > 1 else variant["name"]
                generation_status["current_variant"] = label
                generation_status["progress"] = count - 1

                image, seed = generate_image(
                    variant["prompt"],
                    width=ad_format["width"],
                    height=ad_format["height"],
                )
                image = add_brand_text(image, brand)

                variant_label = f"{i}_{img_num}" if num_images > 1 else str(i)
                result = save_image(
                    image, brand, variant["prompt"], seed,
                    label, variant_label, data, run_id
                )
                generation_status["results"].append(result)

        generation_status["progress"] = generation_status["total"]

    except Exception as e:
        generation_status["error"] = str(e)
        print(f"Generation error: {e}")

    finally:
        generation_status["running"] = False


@app.route("/api/status")
def status():
    return jsonify(generation_status)


@app.route("/api/gallery")
def gallery():
    """List all previous runs grouped by run_id, newest first."""
    if not os.path.exists(OUTPUT_DIR):
        return jsonify([])

    runs = {}
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if not f.endswith("_meta.json"):
            continue
        with open(os.path.join(OUTPUT_DIR, f)) as fh:
            meta = json.load(fh)
        base = f.replace("_meta.json", "")
        meta["files"] = {
            "png": f"{base}.png",
            "jpg": f"{base}.jpg",
            "webp": f"{base}.webp",
        }

        run_id = meta.get("run_id", "unknown")
        if run_id not in runs:
            runs[run_id] = {
                "run_id": run_id,
                "brand": meta.get("brand", ""),
                "product": meta.get("product", ""),
                "style": meta.get("style", ""),
                "feature": meta.get("feature", ""),
                "format": meta.get("format", ""),
                "messaging": meta.get("messaging", ""),
                "created_at": meta.get("created_at", ""),
                "images": [],
            }
        runs[run_id]["images"].append(meta)

    # Sort runs newest first
    result = sorted(runs.values(), key=lambda r: r["created_at"], reverse=True)
    return jsonify(result)


def run_terminal():
    """Run ad generation via terminal prompts."""
    from prompts import AD_FORMATS, MESSAGING_STYLES, AD_STYLES, AD_VARIANTS

    print("\n=== Advertisement Creator - Terminal Mode ===\n")

    # Brand
    brand = input("Brand Name (e.g. Nike, Sony): ").strip()
    if not brand:
        print("Brand name is required.")
        return

    # Product
    product = input("Product Name (e.g. Headphone, Running Shoes): ").strip()
    if not product:
        print("Product name is required.")
        return

    # Ad Format
    print("\nAd Formats:")
    for i, fmt in enumerate(AD_FORMATS, 1):
        print(f"  {i}. {fmt['name']} ({fmt['aspect']}) — {fmt['width']}x{fmt['height']}")
    fmt_choice = input(f"Choose format [1-{len(AD_FORMATS)}] (default: 1): ").strip()
    fmt_idx = int(fmt_choice) - 1 if fmt_choice.isdigit() and 1 <= int(fmt_choice) <= len(AD_FORMATS) else 0
    ad_format = AD_FORMATS[fmt_idx]

    # Messaging Style
    print("\nMessaging Styles:")
    for i, msg in enumerate(MESSAGING_STYLES, 1):
        print(f"  {i}. {msg['name']} — {msg['description']}")
    msg_choice = input(f"Choose messaging [1-{len(MESSAGING_STYLES)}] (default: 2 Informative): ").strip()
    msg_idx = int(msg_choice) - 1 if msg_choice.isdigit() and 1 <= int(msg_choice) <= len(MESSAGING_STYLES) else 1
    messaging_id = MESSAGING_STYLES[msg_idx]["id"]

    # Visual Style
    print("\nVisual Styles:")
    for i, s in enumerate(AD_STYLES, 1):
        print(f"  {i}. {s.capitalize()}")
    style_choice = input(f"Choose style [1-{len(AD_STYLES)}] (default: 7 Professional): ").strip()
    style_idx = int(style_choice) - 1 if style_choice.isdigit() and 1 <= int(style_choice) <= len(AD_STYLES) else 6
    style = AD_STYLES[style_idx]

    # Key Feature
    feature = input("\nKey Feature (e.g. Ultra lightweight): ").strip()
    if not feature:
        print("Key feature is required.")
        return

    # Custom Requirements
    description = input("Custom Requirements (optional, press Enter to skip): ").strip()

    # Variants
    print("\nVariants:")
    for i, v in enumerate(AD_VARIANTS, 1):
        print(f"  {i}. {v['name']} — {v['description']}")
    var_input = input(f"Select variants (comma-separated, e.g. 1,2,3) (default: 1): ").strip()
    if var_input:
        var_indices = [int(x.strip()) - 1 for x in var_input.split(",") if x.strip().isdigit()]
        selected_variants = [AD_VARIANTS[i]["name"] for i in var_indices if 0 <= i < len(AD_VARIANTS)]
    else:
        selected_variants = [AD_VARIANTS[0]["name"]]

    if not selected_variants:
        print("At least one variant must be selected.")
        return

    # Images per variant
    num_input = input("Images per variant [1-5] (default: 1): ").strip()
    num_images = int(num_input) if num_input.isdigit() and 1 <= int(num_input) <= 5 else 1

    total = len(selected_variants) * num_images
    print(f"\n--- Generating {total} image(s) ---")
    print(f"Brand: {brand} | Product: {product} | Style: {style}")
    print(f"Format: {ad_format['name']} | Messaging: {messaging_id} | Feature: {feature}")
    if description:
        print(f"Custom: {description}")
    print(f"Variants: {', '.join(selected_variants)} | Images per variant: {num_images}")
    print()

    # Generate
    from datetime import datetime as dt
    run_id = dt.now().strftime("%Y%m%d_%H%M%S")
    all_prompts = build_prompts(brand, product, style, feature, messaging_id, description)
    prompts = [p for p in all_prompts if p["name"] in selected_variants]
    data = {"brand": brand, "product": product, "style": style, "feature": feature, "format": ad_format["id"], "messaging": messaging_id}

    count = 0
    for i, variant in enumerate(prompts, start=1):
        for img_num in range(1, num_images + 1):
            count += 1
            label = f"{variant['name']} #{img_num}" if num_images > 1 else variant["name"]
            print(f"[{count}/{total}] Generating: {label}...")

            image, seed = generate_image(variant["prompt"], width=ad_format["width"], height=ad_format["height"])
            image = add_brand_text(image, brand)

            variant_label = f"{i}_{img_num}" if num_images > 1 else str(i)
            result = save_image(image, brand, variant["prompt"], seed, label, variant_label, data, run_id)
            print(f"  Saved: {result['png']}, {result['jpg']}, {result['webp']}")

    print(f"\nDone! {total} image(s) saved to outputs/")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Advertisement Creator")
    print("  1. Terminal")
    print("  2. Web UI")
    choice = input("Choose mode [1/2] (default: 1): ").strip()

    if choice == "2":
        print("Starting web server on http://localhost:5012")
        app.run(debug=True, port=5012)
    else:
        run_terminal()
