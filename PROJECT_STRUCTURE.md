# Project Structure

This document explains the main folders and files in CS Demo Coach AI.

```text
cs-demo-coach-ai/
  app/
  data/
  ml/
  models/
  static/
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
  PROJECT_STRUCTURE.md
  LICENSE
```

## `app/`

FastAPI application code.

- `main.py` - API routes, upload handling, report orchestration, feature export, and static frontend serving.
- `frontend.py` - Plain HTML/CSS/JavaScript frontend embedded as a FastAPI `HTMLResponse`.
- `parser.py` - Awpy demo parsing wrapper with readable error messages.
- `features.py` - Player and round-level feature extraction from real Awpy dataframes.
- `report.py` - Baseline scoring and JSON report construction.
- `model_service.py` - Joblib model loading, model metadata, and prediction helpers.
- `replay.py` - Replay payload extraction from real tick, kill, and grenade data.
- `map_config.py` - Radar image metadata and world-to-map coordinate conversion.
- `diagnostics.py` - Lightweight endpoint support for checking tick/position availability.
- `schemas.py` - Pydantic response models.
- `__init__.py` - Marks `app` as a Python package.

## `ml/`

Model training scripts.

- `train_model.py` - Loads feature CSVs, creates weak labels, audits leakage, trains a Random Forest, prints metrics/importances, and saves the model artifact.

## `models/`

Model artifacts used by the API.

- `bad_round_model.pkl` - Optional trained scikit-learn pipeline loaded by `app/model_service.py`.
- `.gitkeep` - Keeps the directory present when no model artifact is committed.

The model artifact is intentionally not ignored by `.gitignore` so a public demo can include a small ready-to-run model.

## `data/`

Local runtime data.

- `uploads/` - Uploaded `.dem` files saved by the API. Ignored by Git.
- `features/` - Generated CSV feature datasets. Ignored by Git.
- `.gitkeep` files - Keep empty runtime directories in the repository.

Do not commit real uploaded demo files. They are large and may contain player data.

## `static/`

Static assets served by FastAPI.

- `maps/` - CS radar images used by the replay viewer.

## Docker Files

- `Dockerfile` - Builds a Python 3.13 slim image, installs dependencies, copies the app, and starts uvicorn.
- `docker-compose.yml` - Runs the API with local bind mounts for uploads, feature exports, and read-only model artifacts.
- `.dockerignore` - Keeps local caches, demos, and generated files out of Docker build context.

## Repository Metadata

- `README.md` - Portfolio-ready project overview and setup guide.
- `LICENSE` - MIT license.
- `.gitignore` - Excludes local environments, uploaded demos, generated datasets, caches, and temporary files.
- `requirements.txt` - Python dependencies.
- `run-local.cmd` - Windows helper for launching the local FastAPI server.
