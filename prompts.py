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
        "id": "instagram_post",
        "name": "Instagram Post",
        "platform": "Instagram",
        "aspect": "1:1",
        "gen_width": 1024,
        "gen_height": 1024,
        "export_width": 1080,
        "export_height": 1080,
    },
    {
        "id": "instagram_story",
        "name": "Instagram Story / Reels",
        "platform": "Instagram",
        "aspect": "9:16",
        "gen_width": 768,
        "gen_height": 1344,
        "export_width": 1080,
        "export_height": 1920,
    },
    {
        "id": "facebook_post",
        "name": "Facebook Post",
        "platform": "Facebook",
        "aspect": "1.91:1",
        "gen_width": 1024,
        "gen_height": 576,
        "export_width": 1200,
        "export_height": 630,
    },
    {
        "id": "twitter_post",
        "name": "Twitter / X Post",
        "platform": "Twitter / X",
        "aspect": "16:9",
        "gen_width": 1024,
        "gen_height": 576,
        "export_width": 1200,
        "export_height": 675,
    },
    {
        "id": "linkedin_post",
        "name": "LinkedIn Post",
        "platform": "LinkedIn",
        "aspect": "1.91:1",
        "gen_width": 1024,
        "gen_height": 576,
        "export_width": 1200,
        "export_height": 627,
    },
    {
        "id": "youtube_thumbnail",
        "name": "YouTube Thumbnail",
        "platform": "YouTube",
        "aspect": "16:9",
        "gen_width": 1024,
        "gen_height": 576,
        "export_width": 1280,
        "export_height": 720,
    },
    {
        "id": "pinterest_pin",
        "name": "Pinterest Pin",
        "platform": "Pinterest",
        "aspect": "2:3",
        "gen_width": 768,
        "gen_height": 1152,
        "export_width": 1000,
        "export_height": 1500,
    },
    {
        "id": "banner_landscape",
        "name": "Web Banner (Landscape)",
        "platform": "Display Ad",
        "aspect": "3.5:1",
        "gen_width": 1024,
        "gen_height": 320,
        "export_width": 728,
        "export_height": 90,
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
                  messaging_id: str = "informative"):
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
        results.append({
            "name": variant["name"],
            "description": variant["description"],
            "prompt": prompt,
        })
    return results
