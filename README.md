# Hangman

A web-based Hangman game with a Python/Flask server and a browser client.

**Play it live:** _link coming after deployment_

The server holds all game logic and the hidden word; the browser only ever sees the masked pattern until the game ends.

## Features

- Easy, Medium, and Hard word lists
- On-screen and physical keyboard input
- Animated hangman drawing, win/loss messages
- Responsive layout for desktop and phones, light and dark themes
- REST API usable from any HTTP client

## Run locally (Windows)

```
git clone https://github.com/vingluck07/hangman-app.git
cd hangman-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python server.py
```

Open http://localhost:5000.

Environment variables: `PORT` (default 5000), `FLASK_DEBUG=1` for debug mode, `LOG_LEVEL` (default `INFO`).

## Tests

```
pytest
```

Browser end-to-end tests in `tests/test_browser.py` are skipped unless Playwright is installed:

```
pip install playwright
python -m playwright install chromium
```

## REST API

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/api/games` | `{"difficulty": "easy" \| "medium" \| "hard"}` | Start a game (201) |
| GET | `/api/games/{game_id}` | — | Current state |
| POST | `/api/games/{game_id}/guess` | `{"letter": "e"}` | Guess a letter |
| GET | `/healthz` | — | Health check |

Example:

```
curl -X POST https://<your-app>.onrender.com/api/games -H "Content-Type: application/json" -d "{\"difficulty\":\"easy\"}"
```

Responses include `game_id`, `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, `max_incorrect`, and `status` (`playing`, `won`, `lost`). Guess responses add `correct`. `word` appears only after the game ends.

Errors return `{"error": "..."}` with status 400 (bad input or duplicate guess), 404 (unknown game), 409 (game already over), 413 (body too large), or 500.

## Deployment (Render)

The repo includes `render.yaml`, a Render Blueprint:

1. Push to GitHub.
2. On [render.com](https://render.com), sign in with GitHub → **New** → **Blueprint** → pick `hangman-app` → **Apply**.
3. Render installs `requirements.txt` and starts `gunicorn server:app` with one worker (games live in memory, so all requests must hit the same process).
4. Every push to `main` redeploys automatically.

Notes on the free plan: the service sleeps after ~15 minutes without traffic, so the first visit afterward takes up to about a minute to load. Games in progress are lost when it sleeps or redeploys.

## Project structure

```
server.py          Flask app and REST API
game.py            HangmanGame engine (no Flask dependency)
words.py           Word list loading and random selection
words/             easy.txt, medium.txt, hard.txt
static/            index.html, style.css, app.js, fonts/
tests/             pytest suites (engine, words, API, browser)
render.yaml        Render deployment config
documentation/     Specification, TODO, bug log, chat transcripts
```

Title font: [Fredoka](https://github.com/hafontia/Fredoka-One), SIL Open Font License (`static/fonts/OFL.txt`).
