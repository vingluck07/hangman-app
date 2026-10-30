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

- [ ] Create `server.py` using Flask.
- [ ] Add in-memory storage for active games.
- [ ] Generate unique game IDs.
- [ ] Implement `POST /api/games` (create game with difficulty).
- [ ] Implement `GET /api/games/{game_id}` (get current state).
- [ ] Implement `POST /api/games/{game_id}/guess` (submit a letter).
- [ ] Validate difficulty and guess input.
- [ ] Return consistent JSON responses and error bodies.
- [ ] Return appropriate HTTP status codes (200, 201, 400, 404).
- [ ] Handle unknown game IDs and malformed requests.
- [ ] Ensure the hidden word is never included while status is `playing`.
- [ ] Serve the browser client's static files from Flask.
- [ ] Add `requirements.txt`.

### Completion Criteria

A complete game can be played using only `curl` or another HTTP client.

---

## Phase 3 — Browser-Based Client

### Tasks

- [ ] Create `static/index.html`, `static/style.css`, `static/app.js`.
- [ ] Add a difficulty selector and New Game button.
- [ ] Display the masked word.
- [ ] Display guessed letters, incorrect letters, and remaining guesses.
- [ ] Add an on-screen alphabet keyboard.
- [ ] Support physical keyboard input.
- [ ] Disable already-guessed letters.
- [ ] Use `fetch()` to call the REST API.
- [ ] Draw the hangman figure and update it after each incorrect guess.
- [ ] Display win/loss messages and reveal the word at game end.
- [ ] Provide a restart/new-game flow.
- [ ] Show friendly messages for network or server errors.
- [ ] Make the layout usable on desktop and mobile screen sizes.

### Completion Criteria

A player can play a full server-hosted game from the browser. No hidden word is stored in browser-side JavaScript.

---

## Phase 4 — Testing and Debugging

### Unit Tests

- [ ] Set up `pytest` and a `tests/` folder.
- [ ] Test `HangmanGame`: correct/incorrect guesses, duplicates, invalid input, masked word.
- [ ] Test win paths and loss paths.
- [ ] Test answer-disclosure rules.
- [ ] Test word loading, validation, and random selection by difficulty.
- [ ] Test invalid difficulty handling.

### API Tests

- [ ] Use the Flask test client to test every endpoint.
- [ ] Test status codes and JSON shapes for success and error cases.
- [ ] Test missing/unknown game IDs and malformed bodies.
- [ ] Test that no response leaks the word during an active game.
- [ ] Add an end-to-end test that plays a full game through the API.

### Browser Testing and Debugging

- [ ] Manually test full games on each difficulty in Chrome, Firefox, and a mobile viewport.
- [ ] Check the browser console and network tab for errors.
- [ ] Verify keyboard and on-screen input don't double-submit.
- [ ] Add server-side logging for requests and errors.
- [ ] Track and fix bugs found; add a regression test for each.

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
