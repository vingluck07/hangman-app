# TODO — Hangman Web App

Implementation roadmap for the Hangman project.

The authoritative requirements are defined in `Specification.md`.

## Implementation Rules

- Implement one phase at a time; complete and test each phase before moving on.
- Do not change the architecture or REST API defined in `Specification.md` unless necessary. Document any deviation in the README and update the specification.
- Keep the game engine independent from Flask and the browser UI.
- The server is authoritative and contains all game logic.
- Never expose the hidden word before a game ends.
- Add tests as each phase is built rather than at the end.
- The project should remain runnable after every completed phase.

---

## Phase 1 — Game Engine and Word Management

### Game Engine

- [x] Create the project directory structure.
- [x] Create `game.py` with a `HangmanGame` class.
- [x] Store the hidden word internally.
- [x] Track guessed letters and incorrect letters.
- [x] Track the maximum number of incorrect guesses.
- [x] Validate single-letter guesses (alphabetic, one character, case-insensitive).
- [x] Detect duplicate guesses.
- [x] Generate the masked word.
- [x] Detect win and loss.
- [x] Implement status values: `playing`, `won`, `lost`.
- [x] Return a client-safe game-state dictionary.
- [x] Reveal the answer only after the game ends.

### Word Management

- [x] Add `words/easy.txt`, `words/medium.txt`, `words/hard.txt`.
- [x] Create a word-loading module.
- [x] Validate that loaded words contain only alphabetic characters.
- [x] Remove duplicates and blank lines when loading.
- [x] Support random word selection by difficulty.
- [x] Raise a clear error for an invalid difficulty.

### Completion Criteria

The game engine and word loader work and can be tested without running a web server.

---

## Phase 2 — Flask Server and REST API

### Tasks

- [x] Create `server.py` using Flask.
- [x] Add in-memory storage for active games.
- [x] Generate unique game IDs.
- [x] Implement `POST /api/games` (create game with difficulty).
- [x] Implement `GET /api/games/{game_id}` (get current state).
- [x] Implement `POST /api/games/{game_id}/guess` (submit a letter).
- [x] Validate difficulty and guess input.
- [x] Return consistent JSON responses and error bodies.
- [x] Return appropriate HTTP status codes (200, 201, 400, 404).
- [x] Handle unknown game IDs and malformed requests.
- [x] Ensure the hidden word is never included while status is `playing`.
- [x] Serve the browser client's static files from Flask.
- [x] Add `requirements.txt`.

### Completion Criteria

A complete game can be played using only `curl` or another HTTP client.

---

## Phase 3 — Browser-Based Client

### Tasks

- [x] Create `static/index.html`, `static/style.css`, `static/app.js`.
- [x] Add a difficulty selector and New Game button.
- [x] Display the masked word.
- [x] Display guessed letters, incorrect letters, and remaining guesses.
- [x] Add an on-screen alphabet keyboard.
- [x] Support physical keyboard input.
- [x] Disable already-guessed letters.
- [x] Use `fetch()` to call the REST API.
- [x] Draw the hangman figure and update it after each incorrect guess.
- [x] Display win/loss messages and reveal the word at game end.
- [x] Provide a restart/new-game flow.
- [x] Show friendly messages for network or server errors.
- [x] Make the layout usable on desktop and mobile screen sizes.

### Completion Criteria

A player can play a full server-hosted game from the browser. No hidden word is stored in browser-side JavaScript.

---

## Phase 4 — Testing and Debugging

### Unit Tests

- [x] Set up `pytest` and a `tests/` folder.
- [x] Test `HangmanGame`: correct/incorrect guesses, duplicates, invalid input, masked word.
- [x] Test win paths and loss paths.
- [x] Test answer-disclosure rules.
- [x] Test word loading, validation, and random selection by difficulty.
- [x] Test invalid difficulty handling.

### API Tests

- [x] Use the Flask test client to test every endpoint.
- [x] Test status codes and JSON shapes for success and error cases.
- [x] Test missing/unknown game IDs and malformed bodies.
- [x] Test that no response leaks the word during an active game.
- [x] Add an end-to-end test that plays a full game through the API.

### Browser Testing and Debugging

- [x] Automated browser tests in Chromium at desktop and mobile sizes (`tests/test_browser.py`).
- [ ] Manually test full games on each difficulty in Firefox (Vin).
- [x] Check the browser console and network tab for errors.
- [x] Verify keyboard and on-screen input don't double-submit.
- [x] Add server-side logging for requests and errors.
- [x] Track and fix bugs found; add a regression test for each.

### Completion Criteria

All tests pass locally with `pytest`, and major user flows and failure cases are covered.

---

## Phase 5 — Cloud Deployment

### Tasks

- [ ] Choose a free hosting platform (e.g. Render).
- [ ] Add a production WSGI server (`gunicorn`) to `requirements.txt`.
- [ ] Read host/port from environment variables; disable Flask debug mode in production.
- [ ] Add any platform config needed (start command, Python version).
- [ ] Push the project to GitHub.
- [ ] Connect the GitHub repo to the hosting platform and deploy.
- [ ] Verify the deployed app: play full games and hit each API endpoint.
- [ ] Enable auto-deploy on push to the main branch.
- [ ] Document the live URL, local setup, and deployment steps in `README.md`.

### Completion Criteria

The app is publicly accessible at a live URL, and a new user can clone, run, and deploy it using only the README.

---

## Recommended Development Order

1. Game Engine and Word Management
2. Flask Server and REST API
3. Browser-Based Client
4. Testing and Debugging
5. Cloud Deployment
