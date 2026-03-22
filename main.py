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


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5012)
