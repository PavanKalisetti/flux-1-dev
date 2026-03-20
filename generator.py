"""
FLUX Image Generation Pipeline

Handles model loading and image generation with brand text overlay.
"""

import torch
import random
import os
import re
import json
import platform
from PIL import Image, ImageDraw, ImageFont

# -----------------------
# CONSTANTS
# -----------------------
GUIDANCE_SCALE = 3.5
INFERENCE_STEPS = 50
BRAND_TEXT_Y_RATIO = 0.85
SHADOW_OFFSET = 3
OUTPUT_DIR = "outputs"

# Global pipeline reference
_pipeline = None


def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-]', '_', name).strip('_').lower()


def get_font(size: int = 70):
    font_paths = {
        "Darwin": "/System/Library/Fonts/Supplemental/Arial.ttf",
        "Linux": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Windows": "C:/Windows/Fonts/arial.ttf",
    }
    path = font_paths.get(platform.system())
    try:
        if path:
            return ImageFont.truetype(path, size)
        else:
            return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def load_pipeline():
    """Load the FLUX pipeline (cached globally)."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    print("Loading FLUX model...")
    from diffusers import FluxPipeline

    _pipeline = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16
    )
    _pipeline.enable_model_cpu_offload()
    print("FLUX model loaded.")
    return _pipeline


def generate_image(prompt: str, gen_width: int = 1024, gen_height: int = 1024,
                   export_width: int = None, export_height: int = None,
                   seed: int = None):
    """Generate a single image from a prompt at the given dimensions."""
    pipe = load_pipeline()

    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    print(f"Generating {gen_width}x{gen_height} with seed: {seed}")

    with torch.inference_mode():
        image = pipe(
            prompt,
            height=gen_height,
            width=gen_width,
            guidance_scale=GUIDANCE_SCALE,
            num_inference_steps=INFERENCE_STEPS,
            max_sequence_length=512,
            generator=torch.Generator("cpu").manual_seed(seed)
        ).images[0]

    # Resize to export dimensions if different from generation size
    if export_width and export_height:
        if export_width != gen_width or export_height != gen_height:
            image = image.resize((export_width, export_height), Image.LANCZOS)

    return image, seed


def add_brand_text(image: Image.Image, brand: str) -> Image.Image:
    """Overlay brand name on the image, font scales with image size."""
    draw = ImageDraw.Draw(image)
    # Scale font relative to image width (~6.5% of width)
    font_size = max(24, int(image.width * 0.065))
    font = get_font(font_size)
    text = brand.upper()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    position = (
        (image.width - text_width) // 2,
        int(image.height * BRAND_TEXT_Y_RATIO)
    )

    # Shadow
    draw.text(
        (position[0] + SHADOW_OFFSET, position[1] + SHADOW_OFFSET),
        text,
        fill="black",
        font=font
    )

    # Main text
    draw.text(position, text, fill="white", font=font)

    return image


def save_image(image: Image.Image, brand: str, prompt: str, seed: int,
               variant_name: str, variant_index: int, data: dict) -> dict:
    """Save image in multiple formats and return file paths."""
    safe_brand = sanitize_filename(brand)
    base_name = f"{safe_brand}_v{variant_index}"
    base_path = os.path.join(OUTPUT_DIR, base_name)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    image.save(base_path + ".png")
    image.save(base_path + ".jpg", "JPEG")
    image.save(base_path + ".webp", "WEBP")

    metadata = {
        "variant": variant_index,
        "variant_name": variant_name,
        "prompt": prompt,
        "seed": seed,
        "brand": data["brand"],
        "product": data["product"],
        "style": data["style"],
        "feature": data["feature"],
        "format": data.get("format", ""),
        "messaging": data.get("messaging", ""),
        "dimensions": f"{image.width}x{image.height}",
    }

    with open(base_path + "_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved variant {variant_index}: {base_path}")

    return {
        "png": f"{base_name}.png",
        "jpg": f"{base_name}.jpg",
        "webp": f"{base_name}.webp",
        "metadata": metadata,
    }
