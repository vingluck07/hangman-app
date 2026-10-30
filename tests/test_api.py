import pytest

from server import create_app
from words import WordManager


@pytest.fixture
def client(tmp_path):
    (tmp_path / "easy.txt").write_text("cat\n")
    (tmp_path / "medium.txt").write_text("garden\n")
    (tmp_path / "hard.txt").write_text("jazz\n")
    app = create_app(WordManager(tmp_path))
    app.config["TESTING"] = True
    return app.test_client()


def new_game(client, difficulty="easy"):
    r = client.post("/api/games", json={"difficulty": difficulty})
    assert r.status_code == 201
    return r.get_json()


def guess(client, game_id, letter):
    return client.post(f"/api/games/{game_id}/guess", json={"letter": letter})


# ----- create ---------------------------------------------------------------

def test_create_game(client):
    body = new_game(client, "medium")
    assert body["game_id"]
    assert body["pattern"] == "_ _ _ _ _ _"
    assert body["remaining_guesses"] == 6
    assert body["status"] == "playing"
    assert body["guessed_letters"] == []
    assert "word" not in body


def test_game_ids_are_unique(client):
    ids = {new_game(client)["game_id"] for _ in range(20)}
    assert len(ids) == 20


@pytest.mark.parametrize("payload", [{"difficulty": "expert"}, {"difficulty": ""}, {}, {"difficulty": 3}])
def test_create_invalid_difficulty(client, payload):
    r = client.post("/api/games", json=payload)
    assert r.status_code == 400
    assert "error" in r.get_json()


@pytest.mark.parametrize("kwargs", [
    {"data": "not json", "content_type": "application/json"},
    {"data": "difficulty=easy", "content_type": "application/x-www-form-urlencoded"},
    {"json": ["easy"]},
])
def test_create_malformed_body(client, kwargs):
    r = client.post("/api/games", **kwargs)
    assert r.status_code == 400
    assert "error" in r.get_json()


# ----- get state ------------------------------------------------------------

def test_get_game(client):
    gid = new_game(client)["game_id"]
    r = client.get(f"/api/games/{gid}")
    assert r.status_code == 200
    assert r.get_json()["game_id"] == gid


def test_unknown_game_id(client):
    assert client.get("/api/games/nope").status_code == 404
    r = guess(client, "nope", "a")
    assert r.status_code == 404
    assert r.get_json() == {"error": "game not found"}


# ----- guess ----------------------------------------------------------------

def test_correct_guess(client):
    gid = new_game(client)["game_id"]
    r = guess(client, gid, "a")
    body = r.get_json()
    assert r.status_code == 200
    assert body["correct"] is True
    assert body["pattern"] == "_ a _"
    assert body["guessed_letters"] == ["a"]


def test_incorrect_guess(client):
    gid = new_game(client)["game_id"]
    body = guess(client, gid, "z").get_json()
    assert body["correct"] is False
    assert body["incorrect_letters"] == ["z"]
    assert body["remaining_guesses"] == 5


@pytest.mark.parametrize("letter", ["", "ab", "1", None, 7])
def test_invalid_letter(client, letter):
    gid = new_game(client)["game_id"]
    r = guess(client, gid, letter)
    assert r.status_code == 400
    assert client.get(f"/api/games/{gid}").get_json()["guessed_letters"] == []


def test_missing_letter_and_malformed_guess(client):
    gid = new_game(client)["game_id"]
    assert client.post(f"/api/games/{gid}/guess", json={}).status_code == 400
    r = client.post(f"/api/games/{gid}/guess", data="x", content_type="application/json")
    assert r.status_code == 400


def test_duplicate_guess(client):
    gid = new_game(client)["game_id"]
    guess(client, gid, "z")
    r = guess(client, gid, "z")
    assert r.status_code == 400
    assert "already" in r.get_json()["error"]
    assert client.get(f"/api/games/{gid}").get_json()["remaining_guesses"] == 5


def test_guess_after_game_over(client):
    gid = new_game(client)["game_id"]
    for ch in "cat":
        guess(client, gid, ch)
    assert guess(client, gid, "z").status_code == 409


# ----- full games & answer disclosure ---------------------------------------

def test_full_game_win(client):
    gid = new_game(client, "hard")["game_id"]
    for ch in "jaz":
        body = guess(client, gid, ch).get_json()
        if ch != "z":
            assert "word" not in body
    assert body["status"] == "won"
    assert body["word"] == "jazz"


def test_full_game_loss(client):
    gid = new_game(client)["game_id"]
    for ch in "bdefgh":
        body = guess(client, gid, ch).get_json()
    assert body["status"] == "lost"
    assert body["word"] == "cat"
    assert client.get(f"/api/games/{gid}").get_json()["word"] == "cat"


def test_word_never_leaked_while_playing(client):
    gid = new_game(client, "medium")["game_id"]
    responses = [client.get(f"/api/games/{gid}")]
    for ch in "garzqxw":
        responses.append(guess(client, gid, ch))
        responses.append(client.get(f"/api/games/{gid}"))
    for r in responses:
        body = r.get_json()
        if body.get("status") == "playing":
            assert "word" not in body
            assert "garden" not in r.get_data(as_text=True)


# ----- misc -----------------------------------------------------------------

def test_unknown_api_route_returns_json(client):
    r = client.get("/api/nothing")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_wrong_method_returns_json(client):
    r = client.delete("/api/games")
    assert r.status_code == 405
    assert "error" in r.get_json()


def test_index_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Hangman" in r.data


def test_store_evicts_oldest(tmp_path):
    (tmp_path / "easy.txt").write_text("cat\n")
    (tmp_path / "medium.txt").write_text("garden\n")
    (tmp_path / "hard.txt").write_text("jazz\n")
    app = create_app(WordManager(tmp_path), max_games=2)
    c = app.test_client()
    first = new_game(c)["game_id"]
    new_game(c)
    new_game(c)
    assert c.get(f"/api/games/{first}").status_code == 404


# ----- Phase 4: robustness, logging, concurrency -----------------------------

def test_oversized_body_rejected(client):
    r = client.post("/api/games", data="x" * (32 * 1024), content_type="application/json")
    assert r.status_code == 413
    assert "error" in r.get_json()


def test_unexpected_error_returns_json_500(tmp_path):
    class BrokenWords:
        def random_word(self, difficulty):
            raise RuntimeError("boom")

    app = create_app(BrokenWords())
    r = app.test_client().post("/api/games", json={"difficulty": "easy"})
    assert r.status_code == 500
    assert r.get_json() == {"error": "internal server error"}


def test_requests_are_logged(client, caplog):
    caplog.set_level("INFO", logger="hangman")
    gid = new_game(client)["game_id"]
    client.get("/api/games/missing")
    messages = [r.getMessage() for r in caplog.records]
    assert any("POST /api/games -> 201" in m for m in messages)
    assert any("GET /api/games/missing -> 404" in m for m in messages)
    assert all("cat" not in m for m in messages)  # hidden word never logged


def test_concurrent_guesses_are_consistent(client):
    """Many threads guessing on one game must not double-count or corrupt state."""
    import threading

    gid = new_game(client, "medium")["game_id"]  # word: garden
    letters = list("bcfhijk")  # 7 wrong letters, only 6 lives
    codes = []

    def worker(letter):
        codes.append(guess(client, gid, letter).status_code)

    threads = [threading.Thread(target=worker, args=(l,)) for l in letters]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    state = client.get(f"/api/games/{gid}").get_json()
    assert state["status"] == "lost"
    assert len(state["incorrect_letters"]) == 6
    assert sorted(codes) == [200] * 6 + [409]


def test_same_letter_sent_twice_concurrently_counts_once(client):
    import threading

    gid = new_game(client)["game_id"]
    codes = []
    threads = [threading.Thread(target=lambda: codes.append(guess(client, gid, "z").status_code))
               for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(codes) == [200] + [400] * 4
    assert client.get(f"/api/games/{gid}").get_json()["remaining_guesses"] == 5
