import pytest

from game import (
    DuplicateGuessError,
    GameOverError,
    HangmanGame,
    InvalidGuessError,
    LOST,
    PLAYING,
    WON,
)


def test_new_game_initial_state():
    g = HangmanGame("apple")
    state = g.to_dict()
    assert state["pattern"] == "_ _ _ _ _"
    assert state["guessed_letters"] == []
    assert state["incorrect_letters"] == []
    assert state["remaining_guesses"] == 6
    assert state["status"] == PLAYING
    assert "word" not in state


def test_correct_guess_reveals_all_positions():
    g = HangmanGame("apple")
    assert g.guess("p") is True
    assert g.pattern == "_ p p _ _"
    assert g.remaining_guesses == 6


def test_incorrect_guess_costs_a_life():
    g = HangmanGame("apple")
    assert g.guess("z") is False
    assert g.incorrect_letters == ["z"]
    assert g.remaining_guesses == 5


def test_guess_is_case_insensitive_and_trimmed():
    g = HangmanGame("Apple")
    g.guess(" A ")
    assert g.pattern == "a _ _ _ _"
    assert g.guessed_letters == ["a"]


@pytest.mark.parametrize("bad", ["", "ab", "1", "!", " ", "é", None, 5])
def test_invalid_guesses_rejected(bad):
    g = HangmanGame("apple")
    with pytest.raises(InvalidGuessError):
        g.guess(bad)
    assert g.guessed_letters == []
    assert g.remaining_guesses == 6


def test_duplicate_guess_rejected_without_penalty():
    g = HangmanGame("apple")
    g.guess("z")
    with pytest.raises(DuplicateGuessError):
        g.guess("Z")
    assert g.remaining_guesses == 5
    assert g.guessed_letters == ["z"]


def test_win():
    g = HangmanGame("apple")
    for ch in "aple":
        g.guess(ch)
    assert g.status == WON
    state = g.to_dict()
    assert state["word"] == "apple"
    assert state["pattern"] == "a p p l e"


def test_loss():
    g = HangmanGame("apple")
    for ch in "bcdfgh":
        g.guess(ch)
    assert g.status == LOST
    assert g.remaining_guesses == 0
    assert g.to_dict()["word"] == "apple"


def test_win_on_last_life():
    g = HangmanGame("cat", max_incorrect=2)
    g.guess("z")
    for ch in "cat":
        g.guess(ch)
    assert g.status == WON
    assert g.remaining_guesses == 1


def test_no_guesses_after_game_over():
    g = HangmanGame("cat")
    for ch in "cat":
        g.guess(ch)
    with pytest.raises(GameOverError):
        g.guess("z")


def test_word_hidden_while_playing():
    g = HangmanGame("secret")
    g.guess("e")
    g.guess("z")
    state = g.to_dict()
    assert "word" not in state
    assert "secret" not in str(state)


def test_custom_max_incorrect():
    g = HangmanGame("cat", max_incorrect=3)
    assert g.remaining_guesses == 3


@pytest.mark.parametrize("bad", ["", "two words", "abc1", None, "café"])
def test_invalid_word_rejected(bad):
    with pytest.raises(ValueError):
        HangmanGame(bad)


def test_invalid_max_incorrect_rejected():
    with pytest.raises(ValueError):
        HangmanGame("cat", max_incorrect=0)


def test_to_dict_returns_copies():
    g = HangmanGame("cat")
    g.guess("c")
    state = g.to_dict()
    state["guessed_letters"].append("x")
    assert g.guessed_letters == ["c"]
