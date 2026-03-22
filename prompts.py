"""
Prompt Templates for Advertisement Generation

Includes:
- Ad formats (platform-specific sizes)
- Messaging styles (emotional, CTA, informative, etc.)
- Ad variant templates (Studio, Lifestyle, Creative)
- Style options
"""

# -----------------------
# AD FORMATS (Platform sizes)
# -----------------------
# gen_width/gen_height = FLUX-friendly generation size (multiples of 64, ~1M pixels)
# export_width/export_height = exact platform dimensions for final export

AD_FORMATS = [
    {
        "id": "square",
        "name": "Social Media Post",
        "aspect": "1:1",
        "width": 1024,
        "height": 1024,
    },
    {
        "id": "portrait",
        "name": "Story / Reels / Portrait",
        "aspect": "9:16",
        "width": 768,
        "height": 1344,
    },
    {
        "id": "landscape",
        "name": "Banner / Landscape",
        "aspect": "16:9",
        "width": 1024,
        "height": 576,
    },
]

# -----------------------
# MESSAGING STYLES
# -----------------------

MESSAGING_STYLES = [
    {
        "id": "emotional",
        "name": "Emotional",
        "description": "Evokes feelings and personal connection",
        "prompt_suffix": (
            "Evoke deep emotion and personal connection. Warm, heartfelt mood. "
            "Soft tones, intimate composition, storytelling feel."
        ),
    },
    {
        "id": "informative",
        "name": "Informative",
        "description": "Highlights specs, facts, and product details",
        "prompt_suffix": (
            "Clean, informative layout. Emphasize product details and specifications. "
            "Clear visibility, neutral background, structured composition."
        ),
    },
    {
        "id": "call_to_action",
        "name": "Call-to-Action",
        "description": "Urgency-driven, encourages immediate action",
        "prompt_suffix": (
            "Bold, attention-grabbing, urgency-driven composition. "
            "High contrast, dynamic angles, energetic colors, strong visual impact."
        ),
    },
    {
        "id": "inspirational",
        "name": "Inspirational",
        "description": "Motivational, aspirational imagery",
        "prompt_suffix": (
            "Inspirational and aspirational mood. Grand, uplifting composition. "
            "Golden hour lighting, expansive framing, motivational atmosphere."
        ),
    },
    {
        "id": "humorous",
        "name": "Humorous",
        "description": "Playful, fun, lighthearted tone",
        "prompt_suffix": (
            "Playful, fun, lighthearted composition. Bright vibrant colors, "
            "whimsical elements, cheerful and engaging visual style."
        ),
    },
    {
        "id": "professional",
        "name": "Professional",
        "description": "Corporate, trustworthy, polished look",
        "prompt_suffix": (
            "Corporate, professional, polished aesthetic. "
            "Clean lines, muted color palette, structured layout, trustworthy feel."
        ),
    },
]

# -----------------------
# AD VARIANTS
# -----------------------

AD_VARIANTS = [
    {
        "name": "Creative Concept",
        "description": "Surreal, artistic, eye-catching ad composition",
        "template": (
            "Creative advertisement of {product} by {brand}, surreal and eye-catching composition. "
            "{style} artistic style. Feature emphasized: {feature}. "
            "Floating elements, dramatic lighting, bold colors, high-end campaign look. "
            "{messaging}"
        ),
    },
    {
        "name": "Studio Luxury",
        "description": "Clean studio product shot with professional lighting",
        "template": (
            "Luxury product photo of {product} by {brand}, {style} style. "
            "Feature: {feature}. "
            "Single product, centered, clean studio, gradient background, "
            "softbox lighting, rim light, 85mm lens, shallow depth of field, ultra sharp. "
            "{messaging}"
        ),
    },
    {
        "name": "Lifestyle",
        "description": "Product in a real-life usage scenario",
        "template": (
            "Lifestyle advertisement of {product} by {brand} being used in real life. "
            "{style} aesthetic. Highlight: {feature}. "
            "Natural lighting, human interaction, realistic environment, candid photography. "
            "{messaging}"
        ),
    },
]

# -----------------------
# AD STYLES
# -----------------------

AD_STYLES = [
    "luxury",
    "minimal",
    "energetic",
    "bold",
    "elegant",
    "playful",
    "professional",
    "vintage",
    "futuristic",
    "natural",
]


# -----------------------
# HELPERS
# -----------------------

def get_format_by_id(format_id: str):
    for fmt in AD_FORMATS:
        if fmt["id"] == format_id:
            return fmt
    return None


def get_messaging_by_id(messaging_id: str):
    for msg in MESSAGING_STYLES:
        if msg["id"] == messaging_id:
            return msg
    return None


def build_prompts(brand: str, product: str, style: str, feature: str,
                  messaging_id: str = "informative", description: str = ""):
    """
    Build prompts for all ad variants using user input.

    Returns a list of dicts with keys: name, description, prompt
    """
    messaging = get_messaging_by_id(messaging_id)
    messaging_suffix = messaging["prompt_suffix"] if messaging else ""

    results = []
    for variant in AD_VARIANTS:
        prompt = variant["template"].format(
            product=product,
            brand=brand,
            style=style,
            feature=feature,
            messaging=messaging_suffix,
        )
        if description.strip():
            prompt += " " + description.strip()
        results.append({
            "name": variant["name"],
            "description": variant["description"],
            "prompt": prompt,
        })
    return results
