# CS Demo Coach AI

CS Demo Coach AI is a FastAPI and machine-learning portfolio project for analyzing real Counter-Strike 2 demo files. Upload a `.dem` file, choose a player, and receive a player-facing coaching report with round summaries, recurring mistakes, replay data when available, and a model-backed review result.

This project is intentionally built around real parser output. It does not use mock demo data or generated CS2 events. If Awpy cannot parse a demo or a feature is unavailable, the app returns a clear error or marks that feature as missing.

## Features

- Upload and parse real Counter-Strike 2 `.dem` files with Awpy.
- Extract player and round-level features from real event/tick data.
- Generate a player-facing match report with grades, takeaways, round cards, and improvement advice.
- Export model-ready CSV datasets from analyzed demos.
- Train a scikit-learn `RandomForestClassifier` using generated feature CSVs.
- Load `models/bad_round_model.pkl` with joblib for FastAPI inference.
- Fall back to a transparent baseline score when the model artifact is missing.
- Serve a plain HTML/CSS/JavaScript frontend with no React dependency.
- Provide operational endpoints for health checks, model info, replay data, and diagnostics.
- Run locally or in Docker.

## Architecture

```text
                         +--------------------------+
                         |  Browser UI              |
                         |  HTML / CSS / JavaScript |
                         +------------+-------------+
                                      |
                                      | .dem upload + player_name
                                      v
+------------------+      +----------+-----------+      +------------------+
| FastAPI routes   | ---> | Awpy demo parser     | ---> | Feature builder  |
| app/main.py      |      | app/parser.py        |      | app/features.py  |
+--------+---------+      +----------+-----------+      +---------+--------+
         |                           |                            |
         |                           | real demo frames/events    |
         |                           v                            v
         |                +----------+-----------+      +---------+--------+
         |                | Replay extraction    |      | Report builder   |
         |                | app/replay.py        |      | app/report.py    |
         |                +----------+-----------+      +---------+--------+
         |                                                       |
         |                                                       v
         |                +----------------------+      +---------+--------+
         +--------------> | Model inference      | ---> | JSON response    |
                          | app/model_service.py |      | + frontend views |
                          +----------+-----------+      +------------------+
                                     |
                                     v
                          models/bad_round_model.pkl
```

## Example Workflow

1. Start the FastAPI server.
2. Open `http://127.0.0.1:8000/`.
3. Upload a real CS2 `.dem` file.
4. Enter the exact in-demo player name.
5. Review the generated tabs:
   - `Match Report`: overall grade, strengths, weaknesses, and takeaways.
   - `Rounds`: filterable round cards with plain-English explanations.
   - `Replay`: map playback when Awpy exposes usable tick coordinates.
   - `Improve`: recurring issue summary and next-match focus plan.
6. Optionally export features with `POST /extract-features`.
7. Retrain the weak-label model with `python -m ml.train_model`.

## Tech Stack

- Python 3.11+
- FastAPI
- Awpy
- pandas
- scikit-learn
- joblib
- python-multipart
- uvicorn
- Docker / Docker Compose
- Plain HTML, CSS, and JavaScript frontend

## Installation

Create and activate a virtual environment, then install dependencies:

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

Run the API locally:

```bash
python -m uvicorn app.main:app --reload
```

If Windows resolves `python` to the Microsoft Store alias or cannot find Python, use the included helper:

```bat
run-local.cmd
```

Open:

```text
http://127.0.0.1:8000/
```

Useful local endpoints:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
http://127.0.0.1:8000/model-info
```

## Docker Usage

Build the image:

```bash
docker build -t cs-demo-coach-ai .
```

Run the app:

```bash
docker run --rm -p 8000:8000 cs-demo-coach-ai
```

Or use Docker Compose:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000/
```

The Docker image copies `app/`, `ml/`, `models/`, `data/`, and `static/`. Runtime uploads and generated feature CSVs should stay out of version control.

## API Endpoints

### `GET /`

Serves the player-facing frontend.

### `GET /health`

Returns service status:

```json
{
  "status": "ok",
  "service": "cs-demo-coach-ai"
}
```

### `GET /model-info`

Returns model metadata, including whether `models/bad_round_model.pkl` exists, model type, feature columns, and last modified timestamp.

### `POST /analyze-demo`

Accepts:

- `file`: required `.dem` upload
- `player_name`: required query parameter

Returns a match report with round reports, extracted raw features, missing feature summary, model status, baseline risk score, and model prediction fields.

### `POST /extract-features`

Accepts the same inputs as `/analyze-demo`, then writes a CSV dataset under `data/features/`.

CSV rows include:

```text
demo_id, player_name, round, kills, deaths, damage_dealt,
flashes_thrown, smokes_thrown, molotovs_incendiaries_thrown,
he_grenades_thrown, utility_count, survived_round, died_first,
death_tick, death_time, side, team, opening_kill, opening_death,
kills_before_death, damage_before_death, clutch_situation,
survived_after_first_kill, utility_used_before_death, round_win,
team_alive_when_player_died, enemies_alive_when_player_died, risk_score
```

### `POST /replay-data`

Returns lightweight per-round replay data from real Awpy tick/event data when available.

### `POST /diagnose-demo`

Returns diagnostic information about map name, tick count, player position records, and sample position rows.

## Model Training

The training script combines all CSV files under `data/features/`, creates a weak label called `bad_round`, audits for label leakage, trains a Random Forest model, prints metrics, and saves:

```text
models/bad_round_model.pkl
```

Run:

```bash
python -m ml.train_model
```

The current model uses weak labels derived from baseline risk and heuristics. Metrics are useful for development, but they are not equivalent to evaluation against human-labeled coaching data.

## Screenshots

Add screenshots before publishing the portfolio page:

- Landing page
- Match report summary
- Round cards
- Replay viewer
- Improvement plan

Suggested folder:

```text
docs/screenshots/
```

## Known Limitations

- Awpy parser output can vary by demo and package version.
- Some demos may not expose position/tick data required for replay playback.
- Current labels are weak labels, not human coaching labels.
- Uploaded demos are saved locally and are not expired automatically.
- No authentication, database, async job queue, or cloud deployment is included yet.

## Future Roadmap

- Add human-labeled training data for stronger supervision.
- Add job queue support for long demo parses.
- Store analyses and upload metadata in Postgres.
- Add user accounts and report history.
- Add richer replay interactions and map calibration coverage.
- Add CI, tests, and linting for public contributions.
- Deploy with AWS infrastructure and managed storage.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
