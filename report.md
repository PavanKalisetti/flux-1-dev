# Advertisement Creator - Using Image Generation

**Capstone Project CS[03]**

---

## Abstract

This project presents an AI-powered advertisement image generator built as a web application. The system uses the FLUX.1-dev text-to-image diffusion model, loaded via the `FluxPipeline` from the Diffusers library, to automatically create professional advertisement visuals from user-provided product details. Users interact through a web interface where they specify brand name, product, visual style, messaging tone, ad format, and optional custom requirements. The system generates multiple ad variants — Creative Concept, Studio Luxury, and Lifestyle — each producing distinct visual compositions from the same input. Images are exported in PNG, JPG, and WebP formats suitable for social media platforms. The project demonstrates the practical application of open-source generative AI models in commercial creative workflows, reducing the time and cost of producing advertisement visuals while maintaining high visual quality. A Flask-based backend handles model inference and image processing, while the frontend provides real-time generation progress and a history of all previous runs.

---

## 1. Introduction

- The advertising industry relies heavily on high-quality visual content for product promotion across digital platforms such as Instagram, Facebook, YouTube, and LinkedIn. Traditionally, creating advertisement images requires professional photographers, graphic designers, and significant production budgets.
- Recent advances in text-to-image diffusion models have made it possible to generate photorealistic images from natural language descriptions. Models like Stable Diffusion, DALL-E, and FLUX have demonstrated remarkable capabilities in producing high-fidelity visuals that closely follow textual prompts.
- This project explores the application of the FLUX.1-dev model — recognized for its strong prompt adherence and high realism — to automate advertisement image generation. The model is loaded using `FluxPipeline` from the Diffusers library in bfloat16 precision with CPU offloading for memory efficiency. The motivation is to build an accessible tool that enables small businesses, marketers, and students to create professional-grade ad visuals without specialized design skills or expensive software.
- The system is designed as a complete end-to-end pipeline: from user input collection through a web interface, to prompt engineering, AI image generation, brand text overlay, and multi-format export. A history feature allows users to review and compare all previous generations.

---

## 2. Problem Statement

- Creating advertisement visuals is a time-consuming and resource-intensive process. Small businesses and individual marketers often lack the budget for professional photography and graphic design, leading to lower-quality promotional materials.
- Existing AI image generation tools are often command-line based, require technical expertise to operate, and do not provide purpose-built workflows for advertisement creation. There is a gap between raw AI image generation capabilities and a user-friendly tool tailored specifically for ad creation.
- This project addresses the need for an accessible, web-based advertisement generation tool that combines AI image generation with ad-specific features such as multiple visual variants, platform-specific formats, messaging styles, and brand text overlays — all controlled through a simple user interface.

---

## 3. Objectives

- Develop a web-based application that generates professional advertisement images using the FLUX.1-dev text-to-image model loaded via `FluxPipeline` from the Diffusers library.
- Design a prompt engineering system with multiple ad variant templates (Creative Concept, Studio Luxury, Lifestyle) that produce visually distinct advertisements from the same product information.
- Support multiple ad formats with appropriate aspect ratios for different social media platforms (1:1 for posts, 9:16 for stories/reels, 16:9 for banners).
- Implement messaging style modifiers (Emotional, Informative, Call-to-Action, Inspirational, Humorous, Professional) that alter the tone and composition of generated images.
- Provide automatic brand text overlay with shadow effects, scaled dynamically to image dimensions.
- Allow users to provide optional custom requirements for fine-grained control over generated output.
- Export generated images in multiple formats (PNG, JPG, WebP) with full metadata for reproducibility.
- Build a history system that allows users to review, compare, and download all previous generations.

---

## 4. Methodology

### 4.1 Tools and Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Model | FLUX.1-dev (Black Forest Labs) | Text-to-image generation with high prompt adherence and realism |
| Model Pipeline | `FluxPipeline` (Diffusers library) | Loading, configuring, and running the FLUX model |
| ML Framework | PyTorch (bfloat16 precision) | Tensor computation and model inference |
| Diffusion Library | Diffusers (`diffusers>=0.25.0`) | Pipeline management, model loading, inference scheduling |
| Backend Framework | Flask (Python) | Web server, REST API, template rendering |
| Frontend | HTML + Tailwind CSS (CDN) + Vanilla JavaScript | User interface, real-time progress, history display |
| Image Processing | Pillow (PIL) | Brand text overlay, image format conversion |
| Supporting Libraries | Transformers, Accelerate, SentencePiece, Protobuf | Tokenization, model acceleration, serialization |

### 4.2 Workflow / Conceptual Framework

The system follows a five-stage pipeline:

**Stage 1 — User Input Collection**
The web interface collects the following parameters: brand name, product name, ad format, visual style, messaging style, key product feature, and an optional custom requirements field where users can provide additional context such as color preferences, mood, background setting, or target audience. Users also select which ad variants to generate (Creative Concept, Studio Luxury, Lifestyle) and the number of images per variant (1–5).

**Stage 2 — Prompt Construction**
The prompt builder (`prompts.py`) combines user inputs with predefined variant templates. Each variant has a distinct prompt structure:
- *Creative Concept*: Uses surreal, artistic compositions with dramatic elements, floating objects, bold colors
- *Studio Luxury*: Focuses on clean studio photography with controlled lighting, gradient backgrounds, shallow depth of field
- *Lifestyle*: Emphasizes real-world usage with natural environments, human interaction, candid photography

The selected messaging style appends a tone-specific suffix that modifies composition, color palette, and mood. If the user provides custom requirements, these are appended to the end of the constructed prompt, allowing fine-grained control over the output.

**Stage 3 — Image Generation**
The FLUX.1-dev model generates images using the `FluxPipeline` from the Diffusers library:
- Model loaded with `FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)`
- CPU offloading enabled via `pipeline.enable_model_cpu_offload()` to manage memory
- 50 inference steps with guidance scale of 3.5
- Random seed per image for variation (stored in metadata for reproducibility)
- Dimensions determined by the selected ad format (1024x1024, 768x1344, or 1024x576)

**Stage 4 — Post-Processing**
Brand name text is overlaid on the generated image using Pillow:
- Font size scales dynamically (~6.5% of image width)
- Centered horizontally, positioned at 85% vertical height
- Black shadow offset (3px) for readability against any background
- System fonts used (Arial on macOS, DejaVu on Linux, Arial on Windows)

**Stage 5 — Export and Storage**
Each image is saved in three formats (PNG, JPG, WebP) with a unique timestamped filename (e.g., `nike_20260322_143022_v1.png`). A JSON metadata file records all generation parameters including the prompt, seed, brand, product, style, format, and timestamp.

### 4.3 Modules and Their Functionality

**`prompts.py` — Prompt Template Engine**
- Defines 3 ad variant templates (Creative Concept, Studio Luxury, Lifestyle) with placeholder variables
- Contains 3 ad format definitions with FLUX-optimized dimensions
- Stores 6 messaging style definitions with prompt suffixes
- Provides 10 visual style options (luxury, minimal, energetic, bold, elegant, playful, professional, vintage, futuristic, natural)
- Accepts optional custom requirements that append to generated prompts
- Exports helper functions for prompt construction

**`generator.py` — Image Generation Pipeline**
- Loads and caches the FLUX.1-dev model using `FluxPipeline.from_pretrained()` (singleton pattern)
- Configures bfloat16 precision and CPU offloading for memory efficiency
- Generates images at specified dimensions using `torch.inference_mode()`
- Applies brand text overlay with automatic font scaling using Pillow
- Saves images in PNG, JPG, and WebP formats with JSON metadata

**`main.py` — Web Server and API**
- Serves the web UI via Flask with `template_folder="."` (index.html in project root)
- Handles generation requests in background threads for non-blocking operation
- Provides real-time progress polling via `/api/status` endpoint
- Aggregates history by grouping images by run ID via `/api/gallery` endpoint

**`index.html` — Web Interface**
- Input form with text fields, dropdowns, checkboxes, slider, and optional custom requirements textarea
- Real-time progress bar with shimmer animation during generation
- Result cards with image preview, metadata display, and download links (PNG/JPG/WebP)
- History panel shown by default, displaying all previous runs grouped chronologically with timestamps

---

## 5. Implementation Details

### 5.1 Model Configuration

The FLUX model is loaded using the Diffusers library's `FluxPipeline`:

```python
from diffusers import FluxPipeline

pipeline = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)
pipeline.enable_model_cpu_offload()
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | `black-forest-labs/FLUX.1-dev` | FLUX.1 development variant |
| Pipeline | `FluxPipeline` (Diffusers) | Handles model loading, tokenization, and inference |
| Precision | `torch.bfloat16` | Reduced precision for memory efficiency |
| Guidance Scale | 3.5 | Controls prompt adherence (higher = more literal) |
| Inference Steps | 50 | Denoising iterations (quality vs. speed tradeoff) |
| Max Sequence Length | 512 | Maximum prompt token length |
| Memory Management | `enable_model_cpu_offload()` | Moves unused layers to CPU to fit in available RAM |

### 5.2 Supported Ad Formats

| Format | Aspect Ratio | Dimensions | Platform Use Cases |
|--------|-------------|------------|-------------------|
| Social Media Post | 1:1 | 1024 x 1024 | Instagram, Facebook, Twitter posts |
| Story / Reels / Portrait | 9:16 | 768 x 1344 | Instagram Stories, Reels, TikTok |
| Banner / Landscape | 16:9 | 1024 x 576 | YouTube thumbnails, website banners |

Dimensions are chosen as multiples of 64, optimized for the FLUX model's architecture (~1M total pixels).

### 5.3 Messaging Styles

| Style | Prompt Effect |
|-------|--------------|
| Emotional | Warm tones, intimate composition, storytelling feel |
| Informative | Clean layout, neutral background, structured composition |
| Call-to-Action | High contrast, dynamic angles, energetic colors |
| Inspirational | Golden hour lighting, expansive framing, uplifting mood |
| Humorous | Bright colors, whimsical elements, cheerful style |
| Professional | Clean lines, muted palette, structured layout |

### 5.4 Project Structure

```
flux_img_gen/
├── main.py              # Flask web server, API endpoints, generation orchestration
├── generator.py         # FluxPipeline loading, image generation, brand overlay, saving
├── prompts.py           # Prompt templates, ad formats, messaging styles, visual styles
├── index.html           # Web UI (Tailwind CSS, Jinja2 templates)
├── requirements.txt     # Python dependencies
├── outputs/             # Generated images and metadata (auto-created)
└── README.md
```

### 5.5 Output File Structure

```
outputs/
├── nike_20260322_143022_v1.png
├── nike_20260322_143022_v1.jpg
├── nike_20260322_143022_v1.webp
├── nike_20260322_143022_v1_meta.json
├── nike_20260322_143022_v2.png
├── nike_20260322_143022_v2.jpg
├── nike_20260322_143022_v2.webp
└── nike_20260322_143022_v2_meta.json
```

Each `_meta.json` contains the full generation parameters:

```json
{
  "run_id": "20260322_143022",
  "variant_name": "Creative Concept",
  "prompt": "Creative advertisement of Air Max 90 by Nike...",
  "seed": 2847193650,
  "brand": "Nike",
  "product": "Air Max 90",
  "style": "professional",
  "feature": "Ultra lightweight",
  "format": "square",
  "messaging": "call_to_action",
  "dimensions": "1024x1024",
  "created_at": "2026-03-22T14:30:25.123456"
}
```

### 5.6 Dependencies

```
torch>=2.0.0
diffusers>=0.25.0
transformers>=4.36.0
accelerate>=0.25.0
sentencepiece>=0.1.99
protobuf>=3.20.0
Pillow>=10.0.0
flask>=3.0.0
```

---

## 6. Results and Analysis

### 6.1 Key Findings

- The FLUX.1-dev model, loaded via `FluxPipeline`, produces high-quality, photorealistic advertisement images that closely follow the constructed prompts across all three variant types.
- The prompt engineering approach — combining variant templates with messaging style suffixes — successfully produces visually distinct outputs from the same product information.
- Different messaging styles produce measurably different compositions: Call-to-Action images tend toward high contrast and dynamic angles, while Professional images maintain muted tones and structured layouts.
- The optional custom requirements field provides effective fine-grained control, allowing users to specify colors, moods, and settings that meaningfully influence the generated output.
- The 1:1 format (Social Media Post) produces the most consistent results, as the model is primarily trained on square aspect ratios.
- Portrait (9:16) and landscape (16:9) formats occasionally require higher inference steps for comparable quality.

### 6.2 Performance

| Metric | Value |
|--------|-------|
| Model Size (Weights) | ~12 GB |
| RAM Usage (with CPU Offloading) | ~26 GB |
| Generation Time per Image (CPU) | 3–8 minutes (varies by dimensions) |
| Generation Time per Image (GPU) | 15–45 seconds (varies by GPU) |
| Supported Export Formats | PNG, JPG, WebP |

### 6.3 Variant Comparison

| Variant | Strengths | Best For |
|---------|-----------|----------|
| Creative Concept | Eye-catching, unique, memorable, artistic | Brand campaigns, print ads |
| Studio Luxury | Clean, professional, product-focused | E-commerce, product catalogs |
| Lifestyle | Relatable, context-rich, human element | Social media, brand storytelling |

---

## 7. Conclusion

### 7.1 Summary of Contributions

- Built a complete, end-to-end web application for AI-powered advertisement generation using the FLUX.1-dev model loaded via `FluxPipeline` from the Diffusers library.
- Designed a prompt engineering system with three distinct ad variant templates (Creative Concept, Studio Luxury, Lifestyle) and six messaging styles that produce diverse, high-quality advertisement visuals from minimal user input.
- Implemented platform-aware ad formats (1:1, 9:16, 16:9) that generate images at FLUX-optimized dimensions for social media deployment.
- Added optional custom requirements input for fine-grained user control over generated imagery.
- Created a user-friendly web interface with real-time generation progress, multi-format downloads (PNG, JPG, WebP), and a history view of all previous runs grouped by session.
- Demonstrated that modern open-source text-to-image models can be practically applied to commercial creative workflows, significantly reducing the time and cost of advertisement production.

### 7.2 Possible Extensions and Improvements

- **Logo Upload**: Allow users to upload brand logos for automatic placement on generated images instead of text-only overlays.
- **Batch Generation**: Support generating ads for multiple products in a single session with a CSV upload feature.
- **A/B Testing**: Generate multiple variations and provide side-by-side comparison tools for selecting the best output.
- **Fine-tuning**: Fine-tune the FLUX model on specific brand styles or product categories for more consistent brand-aligned outputs.
- **Template Library**: Expand the variant library with industry-specific templates (fashion, food, technology, automotive).
- **Multi-language Support**: Add support for brand text overlay in non-Latin scripts.
- **Cloud Deployment**: Deploy on cloud GPU instances (AWS, GCP) for faster generation and multi-user access.
- **Image Editing**: Add post-generation editing capabilities such as background replacement, color adjustment, and text positioning.

---

## References

1. Black Forest Labs. "FLUX.1-dev." https://blackforestlabs.ai
2. Diffusers Library. "FluxPipeline — State-of-the-art diffusion models." https://github.com/huggingface/diffusers
3. PyTorch. "An open source machine learning framework." https://pytorch.org
4. Flask. "A micro web framework for Python." https://flask.palletsprojects.com
5. Tailwind CSS. "A utility-first CSS framework." https://tailwindcss.com
6. Pillow. "Python Imaging Library (Fork)." https://pillow.readthedocs.io
7. Transformers Library. "State-of-the-art Natural Language Processing." https://github.com/huggingface/transformers
