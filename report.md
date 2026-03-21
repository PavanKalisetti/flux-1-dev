# Advertisement Creator - Using Image Generation

**Capstone Project CS[03]**

---

## Abstract

This project presents an AI-powered advertisement image generator built as a web application. The system leverages the FLUX.1-dev text-to-image diffusion model to automatically create professional advertisement visuals from user-provided product details. Users interact through an intuitive web interface where they specify brand name, product, visual style, messaging tone, and ad format. The system then generates multiple ad variants — Studio Luxury, Lifestyle, and Creative Concept — each producing distinct visual compositions from the same input. Images are exported in PNG, JPG, and WebP formats optimized for social media platforms. The project demonstrates the practical application of open-source generative AI models in commercial creative workflows, reducing the time and cost of producing advertisement visuals while maintaining high visual quality. A Flask-based backend handles model inference and image processing, while the frontend provides real-time generation progress and a history of all previous runs.

---

## 1. Introduction

- The advertising industry relies heavily on high-quality visual content for product promotion across digital platforms such as Instagram, Facebook, YouTube, and LinkedIn. Traditionally, creating advertisement images requires professional photographers, graphic designers, and significant production budgets.
- Recent advances in text-to-image diffusion models have made it possible to generate photorealistic images from natural language descriptions. Models like Stable Diffusion, DALL-E, and FLUX have demonstrated remarkable capabilities in producing high-fidelity visuals that closely follow textual prompts.
- This project explores the application of the FLUX.1-dev model — recognized for its strong prompt adherence and high realism — to automate advertisement image generation. The motivation is to build an accessible tool that enables small businesses, marketers, and students to create professional-grade ad visuals without specialized design skills or expensive software.
- The system is designed as a complete end-to-end pipeline: from user input collection through a web interface, to prompt engineering, AI image generation, brand text overlay, and multi-format export. A history feature allows users to review and compare all previous generations.

---

## 2. Problem Statement

- Creating advertisement visuals is a time-consuming and resource-intensive process. Small businesses and individual marketers often lack the budget for professional photography and graphic design, leading to lower-quality promotional materials.
- Existing AI image generation tools are often command-line based, require technical expertise to operate, and do not provide purpose-built workflows for advertisement creation. There is a gap between raw AI image generation capabilities and a user-friendly tool tailored specifically for ad creation.
- This project addresses the need for an accessible, web-based advertisement generation tool that combines AI image generation with ad-specific features such as multiple visual variants, platform-specific formats, messaging styles, and brand text overlays — all controlled through a simple user interface.

---

## 3. Objectives

- Develop a web-based application that generates professional advertisement images using the FLUX.1-dev open-source text-to-image model.
- Design a prompt engineering system with multiple ad variant templates (Studio Luxury, Lifestyle, Creative Concept) that produce visually distinct advertisements from the same product information.
- Support multiple ad formats with appropriate aspect ratios for different social media platforms (1:1 for posts, 9:16 for stories/reels, 16:9 for banners).
- Implement messaging style modifiers (Emotional, Informative, Call-to-Action, Inspirational, Humorous, Professional) that alter the tone and composition of generated images.
- Provide automatic brand text overlay with shadow effects, scaled dynamically to image dimensions.
- Export generated images in multiple formats (PNG, JPG, WebP) with full metadata for reproducibility.
- Build a history system that allows users to review, compare, and download all previous generations.

---

## 4. Methodology

### 4.1 Tools and Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Model | FLUX.1-dev (Black Forest Labs) | Text-to-image generation with high prompt adherence and realism |
| ML Framework | PyTorch (bfloat16 precision) | Tensor computation and model inference |
| Diffusion Library | Hugging Face Diffusers | Model loading, pipeline management, inference |
| Backend Framework | Flask (Python) | Web server, REST API, template rendering |
| Frontend | HTML + Tailwind CSS + JavaScript | User interface, real-time progress, history display |
| Image Processing | Pillow (PIL) | Brand text overlay, image format conversion |
| Model Hosting | Hugging Face Hub | Model weights download and caching |

### 4.2 Workflow / Conceptual Framework

The system follows a five-stage pipeline:

**Stage 1 — User Input Collection**
The web interface collects six parameters: brand name, product name, ad format, visual style, messaging style, and key product feature. Users also select which ad variants to generate and the number of images per variant.

**Stage 2 — Prompt Construction**
The prompt builder (`prompts.py`) combines user inputs with predefined variant templates. Each variant has a distinct prompt structure:
- *Studio Luxury*: Focuses on clean studio photography with controlled lighting
- *Lifestyle*: Emphasizes real-world usage with natural environments
- *Creative Concept*: Uses surreal, artistic compositions with dramatic elements

The selected messaging style appends a tone-specific suffix that modifies composition, color palette, and mood.

**Stage 3 — Image Generation**
The FLUX.1-dev model generates images through an iterative denoising process:
- Model loaded in bfloat16 precision with CPU offloading to manage memory
- 50 inference steps with guidance scale of 3.5
- Random seed per image for variation (stored in metadata for reproducibility)
- Dimensions determined by the selected ad format

**Stage 4 — Post-Processing**
Brand name text is overlaid on the generated image:
- Font size scales dynamically (~6.5% of image width)
- Centered horizontally, positioned at 85% vertical height
- Black shadow offset for readability against any background

**Stage 5 — Export and Storage**
Each image is saved in three formats (PNG, JPG, WebP) with a unique timestamped filename. A JSON metadata file records all generation parameters including the prompt, seed, brand, product, style, format, and timestamp.

### 4.3 Modules and Their Functionality

**`prompts.py` — Prompt Template Engine**
- Defines 3 ad variant templates with placeholder variables
- Contains 3 ad format definitions with FLUX-optimized dimensions
- Stores 6 messaging style definitions with prompt suffixes
- Provides 10 visual style options
- Exports helper functions for prompt construction

**`generator.py` — Image Generation Pipeline**
- Loads and caches the FLUX.1-dev model (singleton pattern)
- Generates images at specified dimensions with configurable parameters
- Applies brand text overlay with automatic font scaling
- Saves images in multiple formats with metadata JSON

**`app.py` — Web Server and API**
- Serves the web UI via Flask templates
- Handles generation requests in background threads
- Provides real-time progress polling via status API
- Aggregates history by grouping images by run ID

**`templates/index.html` — Web Interface**
- Input form with dropdowns, checkboxes, and slider controls
- Real-time progress bar during generation
- Result cards with image preview and download links
- History panel showing all previous runs grouped chronologically

---

## 5. Implementation Details

### 5.1 Model Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | `black-forest-labs/FLUX.1-dev` | FLUX.1 development variant |
| Precision | `bfloat16` | Reduced precision for memory efficiency |
| Guidance Scale | 3.5 | Controls prompt adherence (higher = more literal) |
| Inference Steps | 50 | Denoising iterations (quality vs. speed tradeoff) |
| Max Sequence Length | 512 | Maximum prompt token length |
| Memory Management | CPU Offloading | Moves unused layers to CPU to fit in available RAM |

### 5.2 Supported Ad Formats

| Format | Aspect Ratio | Dimensions | Platform Use Cases |
|--------|-------------|------------|-------------------|
| Social Media Post | 1:1 | 1024 x 1024 | Instagram, Facebook, Twitter posts |
| Story / Reels / Portrait | 9:16 | 768 x 1344 | Instagram Stories, Reels, TikTok |
| Banner / Landscape | 16:9 | 1024 x 576 | YouTube thumbnails, website banners |

### 5.3 Messaging Styles

| Style | Prompt Effect |
|-------|--------------|
| Emotional | Warm tones, intimate composition, storytelling feel |
| Informative | Clean layout, neutral background, structured composition |
| Call-to-Action | High contrast, dynamic angles, energetic colors |
| Inspirational | Golden hour lighting, expansive framing, uplifting mood |
| Humorous | Bright colors, whimsical elements, cheerful style |
| Professional | Clean lines, muted palette, structured layout |

### 5.4 Output File Structure

```
outputs/
├── nike_20260321_143022_v1.png
├── nike_20260321_143022_v1.jpg
├── nike_20260321_143022_v1.webp
├── nike_20260321_143022_v1_meta.json
├── nike_20260321_143022_v2.png
├── nike_20260321_143022_v2.jpg
├── nike_20260321_143022_v2.webp
└── nike_20260321_143022_v2_meta.json
```

Each `_meta.json` contains the full generation parameters:

```json
{
  "run_id": "20260321_143022",
  "variant_name": "Creative Concept",
  "prompt": "Creative advertisement of Air Max 90 by Nike...",
  "seed": 2847193650,
  "brand": "Nike",
  "product": "Air Max 90",
  "style": "luxury",
  "feature": "Ultra lightweight",
  "format": "square",
  "messaging": "call_to_action",
  "dimensions": "1024x1024",
  "created_at": "2026-03-21T14:30:25.123456"
}
```

---

## 6. Results and Analysis

### 6.1 Key Findings

- The FLUX.1-dev model produces high-quality, photorealistic advertisement images that closely follow the constructed prompts across all three variant types.
- The prompt engineering approach — combining variant templates with messaging style suffixes — successfully produces visually distinct outputs from the same product information.
- Different messaging styles produce measurably different compositions: Call-to-Action images tend toward high contrast and dynamic angles, while Professional images maintain muted tones and structured layouts.
- The 1:1 format (Social Media Post) produces the most consistent results, as the model is primarily trained on square aspect ratios.
- Portrait (9:16) and landscape (16:9) formats occasionally require higher inference steps for comparable quality.

### 6.2 Performance

| Metric | Value |
|--------|-------|
| Model Size (Weights) | ~12 GB |
| RAM Usage (with CPU Offloading) | ~26 GB |
| Generation Time per Image (CPU) | 3-8 minutes (varies by dimensions) |
| Generation Time per Image (GPU) | 15-45 seconds (varies by GPU) |
| Supported Export Formats | PNG, JPG, WebP |

### 6.3 Variant Comparison

| Variant | Strengths | Best For |
|---------|-----------|----------|
| Studio Luxury | Clean, professional, product-focused | E-commerce, product catalogs |
| Lifestyle | Relatable, context-rich, human element | Social media, brand storytelling |
| Creative Concept | Eye-catching, unique, memorable | Brand campaigns, print ads |

---

## 7. Conclusion

### 7.1 Summary of Contributions

- Built a complete, end-to-end web application for AI-powered advertisement generation using the FLUX.1-dev open-source diffusion model.
- Designed a prompt engineering system with three distinct ad variant templates and six messaging styles that produce diverse, high-quality advertisement visuals from minimal user input.
- Implemented platform-aware ad formats (1:1, 9:16, 16:9) that generate images at optimal dimensions for social media deployment.
- Created a user-friendly web interface with real-time generation progress, multi-format downloads, and a searchable history of all previous runs.
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

1. Black Forest Labs. "FLUX.1-dev." Hugging Face Model Hub. https://huggingface.co/black-forest-labs/FLUX.1-dev
2. Hugging Face. "Diffusers: State-of-the-art diffusion models." https://github.com/huggingface/diffusers
3. PyTorch. "An open source machine learning framework." https://pytorch.org
4. Flask. "A micro web framework for Python." https://flask.palletsprojects.com
5. Tailwind CSS. "A utility-first CSS framework." https://tailwindcss.com
6. Pillow. "Python Imaging Library (Fork)." https://pillow.readthedocs.io
