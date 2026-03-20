"""
Advertisement Creator - Flask Application

Web interface for generating advertisement images using FLUX.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading

from prompts import build_prompts, AD_STYLES, AD_VARIANTS, AD_FORMATS, MESSAGING_STYLES, get_format_by_id
from generator import generate_image, add_brand_text, save_image, OUTPUT_DIR

app = Flask(__name__)

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

    if not all([brand, product, style, feature]):
        return jsonify({"error": "All fields are required"}), 400

    ad_format = get_format_by_id(format_id)
    if not ad_format:
        return jsonify({"error": "Invalid ad format"}), 400

    # Reset status
    generation_status = {
        "running": True,
        "progress": 0,
        "total": 3,
        "current_variant": "",
        "results": [],
        "error": None,
    }

    # Run generation in background thread
    thread = threading.Thread(
        target=_run_generation,
        args=(brand, product, style, feature, format_id, messaging_id, ad_format),
    )
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Generation started", "total": 3})


def _run_generation(brand, product, style, feature, format_id, messaging_id, ad_format):
    global generation_status

    try:
        prompts = build_prompts(brand, product, style, feature, messaging_id)
        data = {
            "brand": brand, "product": product, "style": style,
            "feature": feature, "format": format_id, "messaging": messaging_id,
        }

        for i, variant in enumerate(prompts, start=1):
            generation_status["current_variant"] = variant["name"]
            generation_status["progress"] = i - 1

            image, seed = generate_image(
                variant["prompt"],
                gen_width=ad_format["gen_width"],
                gen_height=ad_format["gen_height"],
                export_width=ad_format["export_width"],
                export_height=ad_format["export_height"],
            )
            image = add_brand_text(image, brand)

            result = save_image(
                image, brand, variant["prompt"], seed,
                variant["name"], i, data
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
    """List all previously generated images."""
    if not os.path.exists(OUTPUT_DIR):
        return jsonify([])

    images = []
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith("_meta.json"):
            import json
            with open(os.path.join(OUTPUT_DIR, f)) as fh:
                meta = json.load(fh)
            base = f.replace("_meta.json", "")
            meta["files"] = {
                "png": f"{base}.png",
                "jpg": f"{base}.jpg",
                "webp": f"{base}.webp",
            }
            images.append(meta)

    return jsonify(images)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
