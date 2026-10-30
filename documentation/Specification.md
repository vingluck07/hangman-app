# Hangman Web App Specification

## Overview

This project implements a web-based Hangman game with a Flask server
and a browser client, deployed to the cloud.

The server contains all game logic. The browser never knows the hidden
word until the game has ended.

------------------------------------------------------------------------

# System Architecture

                       +----------------------+
                       |    Hangman Server    |
                       |   (Python / Flask)   |
                       |----------------------|
                       | Game Engine          |
                       | Word Manager         |
                       | REST API             |
                       +----------+-----------+
                                  |
                         HTTP / JSON API
                                  |
                        +---------v--------+
                        |  Browser Client  |
                        |   HTML/CSS/JS    |
                        +------------------+

------------------------------------------------------------------------

# Components

## 1. Game Engine

Responsible for:

-   Tracking guessed letters
-   Tracking incorrect guesses
-   Determining win/loss
-   Producing the masked word
-   Serializing client-safe game state

The game engine must not depend on Flask or any user interface.

## 2. Word Manager

Responsible for:

-   Loading the Easy, Medium, and Hard word lists
-   Validating words (alphabetic only) and removing duplicates
-   Selecting a random word by difficulty
-   Rejecting invalid difficulty values

## 3. REST Server

Implementation: Python + Flask.

Responsibilities:

-   Create games
-   Process guesses
-   Return JSON responses with appropriate status codes
-   Store active games in memory
-   Serve the browser client's static files

## 4. Browser Client

Features:

-   Difficulty selection
-   Graphical Hangman drawing
-   On-screen and physical keyboard input
-   Remaining guesses
-   Previous guesses
-   New game button
-   Responsive layout for desktop and mobile

Communication uses the REST API only.

------------------------------------------------------------------------

# REST API

## Create Game

POST

    /api/games

Request

``` json
{
    "difficulty":"medium"
}
```

Response

``` json
{
    "game_id":"abc123",
    "pattern":"_ _ _ _ _",
    "remaining_guesses":6,
    "status":"playing"
}
```

------------------------------------------------------------------------

## Guess Letter

POST

    /api/games/{game_id}/guess

Request

``` json
{
    "letter":"e"
}
```

Response

``` json
{
    "pattern":"_ e _ _ e",
    "guessed_letters":["e"],
    "incorrect_letters":[],
    "remaining_guesses":6,
    "status":"playing"
}
```

------------------------------------------------------------------------

## Get Current State

GET

    /api/games/{game_id}

------------------------------------------------------------------------

## Errors

-   `400` — invalid difficulty, invalid letter, duplicate guess, or
    malformed request
-   `404` — unknown game ID

Error responses use a consistent JSON body, e.g.
`{"error": "message"}`.

------------------------------------------------------------------------

# Game Rules

-   One letter per guess
-   Duplicate guesses are rejected
-   Six incorrect guesses allowed
-   Word is revealed only after the game ends (`won` or `lost`)
-   Server is authoritative

------------------------------------------------------------------------

# Word Lists

Three difficulty levels:

-   Easy
-   Medium
-   Hard

Stored as

    words/
        easy.txt
        medium.txt
        hard.txt

------------------------------------------------------------------------

# Testing

-   `pytest` unit tests for the game engine and word manager
-   API tests using the Flask test client for every endpoint, including
    error cases
-   A test confirming no response includes the word while `playing`
-   An end-to-end test that plays a full game through the API
-   Manual browser testing on desktop and mobile viewports

------------------------------------------------------------------------

# Deployment

-   Hosted on a free cloud platform (e.g. Render), deployed from GitHub
-   Served in production with `gunicorn`
-   Port and settings read from environment variables; debug mode off
-   Live URL and setup/deploy steps documented in `README.md`

------------------------------------------------------------------------

# Project Structure

    hangman-app/
    │
    ├── README.md
    ├── requirements.txt
    ├── server.py
    ├── game.py
    ├── words.py
    ├── static/
    │   ├── index.html
    │   ├── style.css
    │   └── app.js
    ├── words/
    │   ├── easy.txt
    │   ├── medium.txt
    │   └── hard.txt
    ├── tests/
    └── documentation/

------------------------------------------------------------------------

# Out of Scope

Not part of this project: terminal client, student bots, evaluation
mode, scoring, leaderboard, logging/replay, accounts, and persistent
database storage.
