(() => {
  "use strict";

  const LETTERS = "abcdefghijklmnopqrstuvwxyz".split("");
  const STORAGE_KEY = "hangman.gameId";

  const els = {
    form: document.getElementById("new-game-form"),
    difficulty: document.getElementById("difficulty"),
    newGameBtn: document.getElementById("new-game-btn"),
    pattern: document.getElementById("pattern"),
    remaining: document.getElementById("remaining"),
    incorrect: document.getElementById("incorrect"),
    message: document.getElementById("message"),
    keyboard: document.getElementById("keyboard"),
    gallows: document.getElementById("gallows"),
    parts: Array.from(document.querySelectorAll("#gallows .part")),
  };

  let gameId = null;
  let state = null;
  let busy = false; // prevents overlapping requests / double submits
  const keys = {};

  // ----- API -------------------------------------------------------------

  async function api(method, path, body) {
    let res;
    try {
      res = await fetch(path, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (e) {
      throw new ApiError("Can't reach the server. Check your connection and try again.", 0);
    }
    let data = null;
    try { data = await res.json(); } catch (e) { /* non-JSON response */ }
    if (!res.ok) {
      const msg = (data && data.error) || `Server error (${res.status}).`;
      throw new ApiError(msg, res.status);
    }
    return data;
  }

  class ApiError extends Error {
    constructor(message, status) { super(message); this.status = status; }
  }

  // ----- storage (optional convenience: resume game after refresh) ------

  function saveId(id) {
    try { id ? sessionStorage.setItem(STORAGE_KEY, id) : sessionStorage.removeItem(STORAGE_KEY); }
    catch (e) { /* storage unavailable */ }
  }
  function loadId() {
    try { return sessionStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  // ----- rendering -------------------------------------------------------

  function buildKeyboard() {
    for (const letter of LETTERS) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "key";
      btn.textContent = letter;
      btn.dataset.letter = letter;
      btn.setAttribute("aria-label", `Guess ${letter.toUpperCase()}`);
      btn.addEventListener("click", () => guess(letter));
      els.keyboard.appendChild(btn);
      keys[letter] = btn;
    }
  }

  function setMessage(text, kind = "") {
    els.message.textContent = text;
    els.message.className = "message" + (kind ? " " + kind : "");
  }

  function render() {
    if (!state) {
      els.pattern.innerHTML = "&nbsp;";
      els.remaining.textContent = "–";
      els.incorrect.textContent = "—";
      els.parts.forEach(p => p.classList.remove("shown"));
      els.gallows.classList.remove("lost");
      for (const l of LETTERS) {
        keys[l].disabled = true;
        keys[l].classList.remove("correct", "incorrect");
      }
      return;
    }

    const over = state.status !== "playing";
    // On loss, show the full word with the missed letters filled in.
    els.pattern.textContent = over && state.word
      ? state.word.split("").join(" ")
      : state.pattern;
    els.remaining.textContent = state.remaining_guesses;
    els.incorrect.textContent = state.incorrect_letters.length
      ? state.incorrect_letters.join(" ")
      : "—";

    // Map wrong guesses onto the 6 body parts (scales if max_incorrect differs).
    const wrong = state.incorrect_letters.length;
    const max = state.max_incorrect || els.parts.length;
    const shown = Math.min(els.parts.length, Math.ceil((wrong / max) * els.parts.length));
    els.parts.forEach((p, i) => p.classList.toggle("shown", i < shown));
    els.gallows.classList.toggle("lost", state.status === "lost");

    for (const l of LETTERS) {
      const guessed = state.guessed_letters.includes(l);
      const isWrong = state.incorrect_letters.includes(l);
      keys[l].disabled = guessed || over || busy;
      keys[l].classList.toggle("incorrect", isWrong);
      keys[l].classList.toggle("correct", guessed && !isWrong);
    }

    if (state.status === "won") {
      setMessage(`You won! The word was "${state.word}".`, "won");
    } else if (state.status === "lost") {
      setMessage(`Out of guesses. The word was "${state.word}".`, "lost");
    }
  }

  function setBusy(value) {
    busy = value;
    els.newGameBtn.disabled = value;
    render();
  }

  // ----- actions ---------------------------------------------------------

  async function newGame() {
    if (busy) return;
    setBusy(true);
    setMessage("");
    try {
      const data = await api("POST", "/api/games", { difficulty: els.difficulty.value });
      gameId = data.game_id;
      state = data;
      saveId(gameId);
      setMessage("Pick a letter.");
    } catch (e) {
      setMessage(e.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function guess(letter) {
    if (busy || !state || state.status !== "playing") return;
    if (state.guessed_letters.includes(letter)) {
      setMessage(`You already guessed "${letter}".`);
      return;
    }
    setBusy(true);
    try {
      const data = await api("POST", `/api/games/${gameId}/guess`, { letter });
      state = data;
      if (data.status === "playing") {
        setMessage(data.correct ? `Yes, "${letter}" is in the word.` : `No "${letter}".`);
      }
    } catch (e) {
      if (e.status === 404) {
        state = null;
        gameId = null;
        saveId(null);
        setMessage("That game expired (the server may have restarted). Start a new game.", "error");
      } else {
        setMessage(e.message, "error");
      }
    } finally {
      setBusy(false);
    }
  }

  async function resume() {
    const id = loadId();
    if (!id) return newGame();
    setBusy(true);
    try {
      state = await api("GET", `/api/games/${id}`);
      gameId = id;
      if (state.status === "playing") setMessage("Welcome back. Pick a letter.");
    } catch (e) {
      saveId(null);
      state = null;
    } finally {
      setBusy(false);
    }
    if (!state) newGame();
  }

  // ----- events ----------------------------------------------------------

  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    newGame();
  });

  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
    if (e.target instanceof HTMLSelectElement) return;
    const k = e.key.toLowerCase();
    if (k.length === 1 && k >= "a" && k <= "z") {
      e.preventDefault();
      guess(k);
    } else if (e.key === "Enter" && state && state.status !== "playing"
               && !(e.target instanceof HTMLButtonElement)) {
      newGame();
    }
  });

  buildKeyboard();
  render();
  resume();
})();
