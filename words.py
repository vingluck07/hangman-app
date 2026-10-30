"""Word list loading and random word selection."""

import os
import random

DIFFICULTIES = ("easy", "medium", "hard")
DEFAULT_WORDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words")


class InvalidDifficultyError(ValueError):
    """The requested difficulty does not exist."""


def load_word_file(path):
    """Read a word file and return (valid_words, rejected_lines).

    Blank lines and lines starting with ``#`` are ignored. Words are
    lower-cased and de-duplicated, keeping first-seen order. Lines that are
    not purely a-z letters are returned in ``rejected_lines``.
    """
    words, rejected, seen = [], [], set()
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            word = line.lower()
            if not (word.isalpha() and word.isascii()):
                rejected.append(line)
                continue
            if word not in seen:
                seen.add(word)
                words.append(word)
    return words, rejected


class WordManager:
    """Loads the Easy/Medium/Hard word lists and picks random words."""

    def __init__(self, words_dir=DEFAULT_WORDS_DIR, rng=None):
        self.words_dir = words_dir
        self._rng = rng or random.Random()
        self.words = {}
        self.rejected = {}
        for difficulty in DIFFICULTIES:
            path = os.path.join(words_dir, f"{difficulty}.txt")
            words, rejected = load_word_file(path)
            if not words:
                raise ValueError(f"no valid words found in {path}")
            self.words[difficulty] = words
            self.rejected[difficulty] = rejected

    @staticmethod
    def normalize_difficulty(difficulty):
        if not isinstance(difficulty, str) or difficulty.strip().lower() not in DIFFICULTIES:
            raise InvalidDifficultyError(
                f"difficulty must be one of: {', '.join(DIFFICULTIES)}"
            )
        return difficulty.strip().lower()

    def random_word(self, difficulty):
        difficulty = self.normalize_difficulty(difficulty)
        return self._rng.choice(self.words[difficulty])
