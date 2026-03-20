"""
Advertisement Generator (FLUX Local) - Multi Variant

Generates 3 different advertisement styles for the same product:
1. Studio Luxury
2. Lifestyle
3. Creative Concept

Author: [Your Name]
"""

import torch
from diffusers import FluxPipeline
from PIL import Image, ImageDraw, ImageFont
import os
import platform
import random
import re
import json

# -----------------------
# CONSTANTS
# -----------------------
IMAGE_SIZE = 1024
GUIDANCE_SCALE = 3.5
INFERENCE_STEPS = 50
FONT_SIZE = 70
BRAND_TEXT_Y_RATIO = 0.85
SHADOW_OFFSET = 3
OUTPUT_DIR = "outputs"

# -----------------------
# UTILS
# -----------------------

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-]', '_', name).strip('_').lower()

def get_font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont:
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
    except:
        return ImageFont.load_default()

# -----------------------
# SETUP
# -----------------------

def load_pipeline() -> FluxPipeline:
    print(" Loading FLUX model...")
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16
    )
    pipe.enable_model_cpu_offload()
    return pipe

# -----------------------
# USER INPUT
# -----------------------

def get_user_input() -> dict:
    return {
        "brand": input("Enter brand name: "),
        "product": input("Enter product name: "),
        "style": input("Ad style (luxury/minimal/energetic): "),
        "feature": input("Product feature: ")
    }

# -----------------------
# PROMPTS (3 VARIANTS)
# -----------------------

def build_prompts(data: dict) -> list:
    base = f"{data['product']} by {data['brand']}"

    return [
        # 1. Studio Luxury
        (
            f"Luxury product photo of {base}, {data['style']} style. "
            f"Feature: {data['feature']}. "
            "Single product, centered, clean studio, gradient background, "
            "softbox lighting, rim light, 85mm lens, shallow depth of field, ultra sharp."
        ),

        # 2. Lifestyle
        (
            f"Lifestyle advertisement of {base} being used in real life. "
            f"{data['style']} aesthetic. Highlight: {data['feature']}. "
            "Natural lighting, human interaction, realistic environment, candid photography."
        ),

        # 3. Creative Concept
        (
            f"Creative advertisement of {base}, surreal and eye-catching composition. "
            f"{data['style']} artistic style. Feature emphasized: {data['feature']}. "
            "Floating elements, dramatic lighting, bold colors, high-end campaign look."
        )
    ]

# -----------------------
# IMAGE GENERATION
# -----------------------

def generate_image(pipe: FluxPipeline, prompt: str, seed: int = None):
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    print(f" Generating with seed: {seed}")

    with torch.inference_mode():
        image = pipe(
            prompt,
            height=IMAGE_SIZE,
            width=IMAGE_SIZE,
            guidance_scale=GUIDANCE_SCALE,
            num_inference_steps=INFERENCE_STEPS,
            max_sequence_length=512,
            generator=torch.Generator("cpu").manual_seed(seed)
        ).images[0]

    return image, seed

# -----------------------
# ADD BRAND TEXT
# -----------------------

def add_brand_text(image: Image.Image, brand: str) -> Image.Image:
    draw = ImageDraw.Draw(image)
    font = get_font(FONT_SIZE)
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

# -----------------------
# SAVE OUTPUT
# -----------------------

def save_image(image, brand, prompt, seed, data, variant):
    safe_brand = sanitize_filename(brand)
    base_path = os.path.join(OUTPUT_DIR, f"{safe_brand}_v{variant}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    image.save(base_path + ".png")
    image.save(base_path + ".jpg", "JPEG")
    image.save(base_path + ".webp", "WEBP")

    metadata = {
        "variant": variant,
        "prompt": prompt,
        "seed": seed,
        "brand": data["brand"],
        "product": data["product"],
        "style": data["style"],
        "feature": data["feature"]
    }

    with open(base_path + "_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f" Saved variant {variant}: {base_path}")

# -----------------------
# MAIN
# -----------------------

def main():
    print("\n Advertisement Generator (FLUX Multi-Variant)\n")

    data = get_user_input()
    prompts = build_prompts(data)

    pipe = load_pipeline()

    for i, prompt in enumerate(prompts, start=1):
        print(f"\n--- Variant {i} ---")
        print("Prompt:", prompt)

        image, seed = generate_image(pipe, prompt)

        image = add_brand_text(image, data["brand"])

        save_image(image, data["brand"], prompt, seed, data, i)

    print("\n All 3 ad variations generated successfully!")

# -----------------------
if __name__ == "__main__":
    main()