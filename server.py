"""Flask server exposing the Hangman REST API and serving the browser client."""

import logging
import os
import threading
import time
import uuid
from collections import OrderedDict

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from game import GameOverError, GuessError, HangmanGame
from words import InvalidDifficultyError, WordManager

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
MAX_ACTIVE_GAMES = 10_000  # oldest games are dropped beyond this
MAX_BODY_BYTES = 16 * 1024  # API bodies are tiny; reject anything larger

log = logging.getLogger("hangman")


class GameStore:
    """Thread-safe in-memory storage for active games."""

    def __init__(self, max_games=MAX_ACTIVE_GAMES):
        self._games = OrderedDict()
        self._lock = threading.Lock()
        self.max_games = max_games

    def add(self, game):
        game_id = uuid.uuid4().hex
        with self._lock:
            self._games[game_id] = game
            while len(self._games) > self.max_games:
                self._games.popitem(last=False)
        return game_id

    def get(self, game_id):
        with self._lock:
            return self._games.get(game_id)

    def lock(self):
        return self._lock

    def __len__(self):
        return len(self._games)


def error(message, status):
    return jsonify({"error": message}), status


def game_response(game_id, game, **extra):
    body = {"game_id": game_id, **game.to_dict(), **extra}
    return body


def create_app(word_manager=None, max_games=MAX_ACTIVE_GAMES):
    app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
    app.json.sort_keys = False
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES
    words = word_manager or WordManager()
    store = GameStore(max_games)
    app.config["GAME_STORE"] = store

    def read_json_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None
        return data

    # ----- browser client --------------------------------------------------

    @app.get("/")
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    # ----- REST API ----------------------------------------------------------

    @app.post("/api/games")
    def create_game():
        data = read_json_body()
        if data is None:
            return error("request body must be a JSON object", 400)
        try:
            word = words.random_word(data.get("difficulty"))
        except InvalidDifficultyError as e:
            return error(str(e), 400)
        game = HangmanGame(word)
        game_id = store.add(game)
        return jsonify(game_response(game_id, game)), 201

    @app.get("/api/games/<game_id>")
    def get_game(game_id):
        game = store.get(game_id)
        if game is None:
            return error("game not found", 404)
        with store.lock():
            return jsonify(game_response(game_id, game))

    @app.post("/api/games/<game_id>/guess")
    def guess(game_id):
        game = store.get(game_id)
        if game is None:
            return error("game not found", 404)
        data = read_json_body()
        if data is None:
            return error("request body must be a JSON object", 400)
        if "letter" not in data:
            return error("missing 'letter'", 400)
        with store.lock():
            try:
                correct = game.guess(data["letter"])
            except GameOverError as e:
                return error(str(e), 409)
            except GuessError as e:
                return error(str(e), 400)
            return jsonify(game_response(game_id, game, correct=correct))

    # ----- request logging ---------------------------------------------------

    @app.before_request
    def start_timer():
        request.environ["hangman.start"] = time.perf_counter()

    @app.after_request
    def log_request(response):
        if request.path.startswith("/api/"):
            start = request.environ.get("hangman.start", time.perf_counter())
            ms = (time.perf_counter() - start) * 1000
            level = logging.WARNING if response.status_code >= 400 else logging.INFO
            log.log(level, "%s %s -> %s (%.1f ms)",
                    request.method, request.path, response.status_code, ms)
        return response

    # ----- JSON errors ----------------------------------------------------------

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        if request.path.startswith("/api/"):
            return error(e.description or e.name, e.code)
        return e

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        log.exception("Unhandled error on %s %s", request.method, request.path)
        if request.path.startswith("/api/"):
            return error("internal server error", 500)
        return "Internal server error", 500

    return app


logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
