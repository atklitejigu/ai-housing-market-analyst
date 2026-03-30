from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Data folders
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Output folders
OUTPUT_CHARTS = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_MODELS = PROJECT_ROOT / "outputs" / "model_results"
OUTPUT_SUMMARIES = PROJECT_ROOT / "outputs" / "summaries"

# Documentation folders
DOCS_HMDA = PROJECT_ROOT / "docs" / "hmda_docs"
DOCS_NOTES = PROJECT_ROOT / "docs" / "project_notes"

# App folders
APP_PAGES = PROJECT_ROOT / "app" / "pages"
APP_UTILS = PROJECT_ROOT / "app" / "utils"

# Notebook folder
NOTEBOOKS = PROJECT_ROOT / "notebooks"

# Source folder
SRC = PROJECT_ROOT / "src"

# ✅ Ensure output folders exist
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUT_MODELS.mkdir(parents=True, exist_ok=True)
OUTPUT_SUMMARIES.mkdir(parents=True, exist_ok=True)
