"""End-to-end browser tests (optional).

Skipped automatically unless Playwright and a Chromium browser are installed:

    pip install playwright
    python -m playwright install chromium
"""

import threading

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

from werkzeug.serving import make_server  # noqa: E402

from server import create_app  # noqa: E402
from words import WordManager  # noqa: E402


@pytest.fixture(scope="module")
def base_url(tmp_path_factory):
    words_dir = tmp_path_factory.mktemp("words")
    (words_dir / "easy.txt").write_text("cat\n")
    (words_dir / "medium.txt").write_text("garden\n")
    (words_dir / "hard.txt").write_text("jawbreaker\n")
    server = make_server("127.0.0.1", 0, create_app(WordManager(words_dir)), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # browser binaries not installed
            pytest.skip(f"Chromium not available: {e}")
        yield b
        b.close()


VIEWPORTS = {"desktop": {"width": 1100, "height": 800}, "mobile": {"width": 375, "height": 740}}


@pytest.fixture(params=list(VIEWPORTS))
def page(request, browser, base_url):
    ctx = browser.new_context(viewport=VIEWPORTS[request.param])
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.console_errors = errors
    pg.goto(base_url)
    pg.wait_for_selector(".key:not([disabled])")
    yield pg
    ctx.close()
    assert errors == [], f"browser console errors: {errors}"


def start(page, difficulty):
    page.select_option("#difficulty", difficulty)
    page.click("#new-game-btn")
    page.wait_for_function("document.querySelector('#message').textContent === 'Pick a letter.'")


def press(page, letter):
    page.keyboard.press(letter)
    # Wait for the server's answer. All keys are briefly disabled while a
    # request is in flight, so wait for the key's result color instead.
    page.wait_for_selector(
        f'.key[data-letter="{letter}"].correct, .key[data-letter="{letter}"].incorrect'
    )


def test_win_with_physical_keyboard(page):
    start(page, "easy")
    for ch in "cat":
        press(page, ch)
    assert "You won" in page.text_content("#message")
    assert page.text_content("#pattern") == "c a t"
    assert page.locator(".key:not([disabled])").count() == 0


def test_loss_with_on_screen_keyboard(page):
    start(page, "easy")
    for ch in "bdefgh":
        page.click(f'.key[data-letter="{ch}"]')
        page.wait_for_selector(f'.key[data-letter="{ch}"].incorrect')
    assert "Out of guesses" in page.text_content("#message")
    assert page.locator("#gallows .part.shown").count() == 6
    assert page.text_content("#pattern") == "c a t"


def test_drawing_tracks_wrong_guesses(page):
    start(page, "easy")
    for i, ch in enumerate("xyz", start=1):
        press(page, ch)
        assert page.locator("#gallows .part.shown").count() == i
    assert page.text_content("#remaining") == "3"
    assert page.text_content("#incorrect") == "x y z"


def test_rapid_double_press_counts_once(page):
    start(page, "easy")
    page.keyboard.press("z")
    page.keyboard.press("z")
    page.click('.key[data-letter="z"]', force=True)
    page.wait_for_selector('.key[data-letter="z"].incorrect')
    page.wait_for_timeout(300)
    assert page.text_content("#remaining") == "5"


def test_word_not_in_page_while_playing(page):
    start(page, "medium")
    press(page, "a")
    html = page.content()
    assert "garden" not in html
    assert "garden" not in page.evaluate("JSON.stringify(sessionStorage)")


def test_refresh_resumes_game(page):
    start(page, "easy")
    press(page, "a")
    page.reload()
    page.wait_for_function("document.querySelector('#pattern').textContent === '_ a _'")
    assert page.locator('.key[data-letter="a"][disabled]').count() == 1


def test_long_word_stays_on_one_line_without_page_scroll(page):
    """Regression: 8+ letter words used to wrap onto two lines."""
    start(page, "hard")
    pattern = page.locator("#pattern")
    line_height = page.evaluate(
        "parseFloat(getComputedStyle(document.querySelector('#pattern')).fontSize) * 1.6"
    )
    assert pattern.bounding_box()["height"] < line_height
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_unknown_saved_game_starts_fresh(page):
    start(page, "easy")
    page.evaluate("sessionStorage.setItem('hangman.gameId', 'does-not-exist')")
    page.reload()
    # unknown saved id -> a fresh game starts automatically
    page.wait_for_function("document.querySelector('#message').textContent === 'Pick a letter.'")
    # the browser logs the expected 404 as a console error; ignore only that
    page.console_errors[:] = [e for e in page.console_errors if "404" not in e]
