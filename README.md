# Asana Studio 🧘

A comprehensive yoga pose database, sequence generator, and interactive practice builder.

## Features

- **300+ Yoga Poses** with Sanskrit names, descriptions, difficulty levels, and categorization
- **Smart Sequence Generator** — 10 styles (Morning Flow, Power Vinyasa, Hip Opener, etc.) with warmup→peak→cooldown structure
- **Custom Practice Builder** — drag-and-drop, configurable hold times per pose
- **Practice Player** — countdown timer, SVG wireframes, voice announcements, play/pause/skip
- **Search & Filter** — by name, category, difficulty, tags

## Tech Stack

- **Backend**: Python / FastAPI / SQLite
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Voice**: Web Speech API (browser-native)

## Quick Start

```bash
# 1. Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Run the server (auto-seeds database on first run)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

## Project Structure

```
yoga/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # SQLite schema
│   ├── seed_poses.py        # 300+ pose data
│   └── routers/
│       ├── poses.py         # Search/filter API
│       ├── sequences.py     # Sequence generator
│       └── practices.py     # Custom practice CRUD
├── frontend/
│   ├── index.html           # SPA shell
│   ├── css/style.css        # Dark glassmorphism theme
│   └── js/
│       ├── app.js           # Router
│       ├── api.js           # Fetch wrapper
│       ├── poses.js         # Pose explorer
│       ├── sequences.js     # Sequence UI
│       ├── practice.js      # Practice player
│       └── svg-poses.js     # SVG wireframes
└── README.md
```
