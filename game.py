"""Core Hangman game engine.

This module has no dependency on Flask or any user interface, so it can be
used and tested on its own.
"""

PLAYING = "playing"
WON = "won"
LOST = "lost"

DEFAULT_MAX_INCORRECT = 6


class GuessError(ValueError):
    """Base class for rejected guesses."""


class InvalidGuessError(GuessError):
    """The guess is not a single alphabetic character."""


class DuplicateGuessError(GuessError):
    """The letter has already been guessed."""


class GameOverError(GuessError):
    """A guess was made after the game ended."""


class HangmanGame:
    """A single game of Hangman.

    The hidden word is kept private. Use ``to_dict()`` to get a
    client-safe view of the game that only includes the word once the
    game has ended.
    """

    def __init__(self, word, max_incorrect=DEFAULT_MAX_INCORRECT):
        if not isinstance(word, str) or not word.isalpha() or not word.isascii():
            raise ValueError("word must be a non-empty string of letters a-z")
        if max_incorrect < 1:
            raise ValueError("max_incorrect must be at least 1")
        self._word = word.lower()
        self.max_incorrect = max_incorrect
        self.guessed_letters = []      # every accepted guess, in order
        self.incorrect_letters = []    # wrong guesses, in order

    # ----- derived state -------------------------------------------------

    @property
    def remaining_guesses(self):
        return self.max_incorrect - len(self.incorrect_letters)

    @property
    def status(self):
        if all(ch in self.guessed_letters for ch in self._word):
            return WON
        if self.remaining_guesses <= 0:
            return LOST
        return PLAYING

    @property
    def is_over(self):
        return self.status != PLAYING

    @property
    def pattern(self):
        """Masked word with spaces between characters, e.g. ``_ e _ _ e``."""
        return " ".join(ch if ch in self.guessed_letters else "_" for ch in self._word)

    # ----- actions -------------------------------------------------------

    def guess(self, letter):
        """Submit a guess. Returns True if the letter is in the word.

        Raises a ``GuessError`` subclass if the guess is rejected. Rejected
        guesses never change the game state.
        """
        if self.is_over:
            raise GameOverError("the game is already over")
        if not isinstance(letter, str):
            raise InvalidGuessError("guess must be a single letter")
        letter = letter.strip().lower()
        if len(letter) != 1 or not letter.isalpha() or not letter.isascii():
            raise InvalidGuessError("guess must be a single letter a-z")
        if letter in self.guessed_letters:
            raise DuplicateGuessError(f"'{letter}' has already been guessed")

        self.guessed_letters.append(letter)
        correct = letter in self._word
        if not correct:
            self.incorrect_letters.append(letter)
        return correct

    # ----- serialization -------------------------------------------------

    def to_dict(self):
        """Client-safe game state. The word is included only after the game ends."""
        state = {
            "pattern": self.pattern,
            "guessed_letters": list(self.guessed_letters),
            "incorrect_letters": list(self.incorrect_letters),
            "remaining_guesses": self.remaining_guesses,
            "max_incorrect": self.max_incorrect,
            "status": self.status,
        }
        if self.is_over:
            state["word"] = self._word
        return state
