import random

import pytest

from words import DIFFICULTIES, InvalidDifficultyError, WordManager, load_word_file


def write_lists(tmp_path, easy="cat\n", medium="garden\n", hard="jazz\n"):
    (tmp_path / "easy.txt").write_text(easy)
    (tmp_path / "medium.txt").write_text(medium)
    (tmp_path / "hard.txt").write_text(hard)
    return tmp_path


def test_real_word_lists_load_and_are_valid():
    wm = WordManager()
    for d in DIFFICULTIES:
        assert len(wm.words[d]) > 0
        assert wm.rejected[d] == []
        assert all(w.isalpha() and w.islower() for w in wm.words[d])


def test_load_skips_blanks_comments_and_duplicates(tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("# comment\n\nCat\ncat\n  dog  \nCAT\n")
    words, rejected = load_word_file(p)
    assert words == ["cat", "dog"]
    assert rejected == []


def test_load_rejects_non_alphabetic(tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("cat\nice cream\nr2d2\nwell-known\ndog\n")
    words, rejected = load_word_file(p)
    assert words == ["cat", "dog"]
    assert rejected == ["ice cream", "r2d2", "well-known"]


def test_random_word_by_difficulty(tmp_path):
    wm = WordManager(write_lists(tmp_path))
    assert wm.random_word("easy") == "cat"
    assert wm.random_word("medium") == "garden"
    assert wm.random_word("hard") == "jazz"


def test_random_word_comes_from_list():
    wm = WordManager(rng=random.Random(0))
    for d in DIFFICULTIES:
        for _ in range(20):
            assert wm.random_word(d) in wm.words[d]


def test_difficulty_is_case_insensitive(tmp_path):
    wm = WordManager(write_lists(tmp_path))
    assert wm.random_word(" EASY ") == "cat"


@pytest.mark.parametrize("bad", ["", "expert", "e", None, 1])
def test_invalid_difficulty(bad, tmp_path):
    wm = WordManager(write_lists(tmp_path))
    with pytest.raises(InvalidDifficultyError):
        wm.random_word(bad)


def test_empty_list_raises(tmp_path):
    write_lists(tmp_path, hard="# nothing here\n")
    with pytest.raises(ValueError):
        WordManager(tmp_path)


def test_missing_file_raises(tmp_path):
    (tmp_path / "easy.txt").write_text("cat\n")
    with pytest.raises(FileNotFoundError):
        WordManager(tmp_path)
