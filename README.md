# CS Demo Coach AI

Analyze real Counter-Strike 2 demos and receive player-friendly coaching reports, round reviews, replay visualization, and improvement suggestions.

Built with:
- Python
- FastAPI
- scikit-learn
- Awpy
- Docker

CS Demo Coach AI turns raw CS2 `.dem` files into practical coaching feedback. A player uploads a demo, selects their in-game name, and the app extracts real gameplay data to produce a match report, round-by-round review, replay view, and improvement plan.

## What This Project Does

- Upload a CS2 demo file
- Select a player
- Extract real gameplay data
- Analyze rounds with machine learning
- Review replay visualizations
- Receive improvement suggestions

## Features

### Player Features

- Player-facing match report with an overall performance grade
- Round cards with plain-English explanations
- Replay viewer when demo tick data is available
- Improvement plan based on recurring mistakes
- Clean dark esports-style frontend

### Machine Learning Features

- Feature extraction from real Awpy parser output
- Model-ready CSV dataset export
- Weak-label training pipeline for bad-round classification
- scikit-learn `RandomForestClassifier`
- joblib model loading for FastAPI inference
- Baseline scoring fallback when no model artifact is available

### Engineering Features

- FastAPI backend with typed response schemas
- Real-world `.dem` file ingestion
- Clear error handling for parser failures and missing players
- Docker and Docker Compose support
- Operational endpoints for health checks and model metadata
- Plain HTML/CSS/JavaScript frontend with no React dependency

## How It Works

1. Upload a demo
2. Parse replay data using Awpy
3. Extract player and round features
4. Run machine learning analysis
5. Generate a coaching report
6. Display replay and round insights

## Technical Highlights

- End-to-end ML pipeline
- Real-world file ingestion
- Feature engineering from gameplay events
- Model training and inference
- FastAPI backend
- Dockerized deployment
- Replay visualization

## Skills Demonstrated

- Python
- FastAPI
- Machine Learning
- Docker
- Git
- Data Processing
- Feature Engineering
- API Development

## Tech Stack

Backend:
- FastAPI
- Uvicorn
- python-multipart

Data and ML:
- Awpy
- pandas
- scikit-learn
- joblib

Frontend and Deployment:
- HTML/CSS/JavaScript
- Docker
- Docker Compose

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Local Development

Run the app:

```bash
python -m uvicorn app.main:app --reload
```

On Windows, this helper is also available:

```bat
run-local.cmd
```

Open:

```text
http://127.0.0.1:8000/
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Docker Usage

Build:

```bash
docker build -t cs-demo-coach-ai .
```

Run:

```bash
docker run --rm -p 8000:8000 cs-demo-coach-ai
```

Or use Docker Compose:

```bash
docker compose up --build
```

## API Endpoints

- `GET /` - player-facing frontend
- `GET /health` - service health check
- `GET /model-info` - model artifact metadata
- `POST /analyze-demo` - upload a `.dem` file and generate a player report
- `POST /extract-features` - export extracted features to CSV
- `POST /replay-data` - return replay data when tick coordinates are available
- `POST /diagnose-demo` - inspect whether a demo exposes player position data

## Model Training

Export feature CSVs through `/extract-features`, then train the model:

```bash
python -m ml.train_model
```

The script combines CSV files from `data/features/`, creates weak labels, checks for label leakage, trains a Random Forest model, prints metrics and feature importances, and saves:

```text
models/bad_round_model.pkl
```

## Screenshots

Screenshots make this project much easier to evaluate visually. Recommended captures:

- Landing page
- Match report
- Round review cards
- Replay viewer
- Improvement plan

## Notes

- The app uses real Awpy parser output, not mock events.
- Feature availability depends on the demo file and Awpy output.
- Replay visualization requires usable tick/position data.
- Current model labels are weak labels generated from heuristics and baseline scoring.

## Next Steps

- AWS deployment
- PostgreSQL integration
- Analysis history
- Background job processing
- Monitoring and observability
- CI/CD automation

## License

MIT License. See [LICENSE](LICENSE).
