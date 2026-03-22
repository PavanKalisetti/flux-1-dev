# Advertisement Creator - FLUX Image Generation

AI-powered ad generator using FLUX.1-dev model. Generates 3 ad variants (Studio Luxury, Lifestyle, Creative Concept) with platform-specific sizes and messaging styles.

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Login to Hugging Face (needed for FLUX model download)
huggingface-cli login

# 4. Run the app
python3 app.py

# 5. Open in browser
# http://localhost:5012
```

## Notes

- First run downloads the FLUX model (~12 GB) — takes a while.
- Needs a HuggingFace account with access to `black-forest-labs/FLUX.1-dev`.
- GPU recommended. Works on CPU with model offloading (slower).
- Generated images are saved in the `outputs/` folder.
