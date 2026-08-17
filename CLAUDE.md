# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Dependency management is via `uv` (see `pyproject.toml`, `uv.lock`); Python 3.11+.

- Install deps: `uv sync`
- Run the API locally (requires Postgres reachable via `POSTGRES_*` env vars; defaults to `localhost:5432`, user/password `user`/`password`): `uv run uvicorn src.main:app --reload`
- Run the full stack (Postgres + backend + nginx frontend + cloudflared): `docker-compose up`
- Run all tests: `uv run pytest`
- Run a single test: `uv run pytest tests/test_api.py::test_generate_short_url`

Tests use `pytest-asyncio` in `auto` mode (see `pytest.ini`) and override the DB to a local SQLite file (`.test.db`) via `tests/conftest.py` — they do **not** require Postgres. `pythonpath` includes both `.` and `src`, so imports like `from src.main import app` work.

## Architecture

FastAPI + async SQLAlchemy 2.0 (asyncpg in prod, aiosqlite for tests). Two endpoints in `src/main.py`:

- `POST /short_url` — body `{"long_url": "..."}` → `{"data": "<6-char slug>"}`
- `GET /{slug}` — 302 redirect to the stored long URL, or 400 if unknown

Request flow (generation): `main.generate_short_url` → `service.generate_slug` (retries up to 5x on `SlugAlreadyExistsError`) → `shortener.generate_random_slug` (6 chars from `[a-zA-Z0-9]`, 62^6 ≈ 5.68e10 combinations) → `database.crud.add_slug_to_db`.

Schema: single table `short_urls(slug PK, long_url)` defined in `src/database/models.py`. Table creation is done in the FastAPI `lifespan` handler with a 10-attempt retry loop (3s sleep) to wait for Postgres on cold boot.

Custom exceptions live in `src/exceptions.py` and inherit from `ShortenerBaseError`. They're caught at the route layer and translated to HTTP errors — keep that boundary: services raise typed exceptions, routes map to HTTP.

DB session lifecycle: `src/database/db.py` builds the async engine from `POSTGRES_*` env vars; `main.get_session` is the FastAPI dependency. Tests swap this via `app.dependency_overrides[get_session]` in `conftest.py` — do the same for any new session-dependent route.

## Frontend & deployment

`frontend/` is a static `index.html` served by nginx, which proxies `/short_url` and `/{slug}` patterns to the `backend` service (see `frontend/nginx.conf`). The `cloudflared` service in `docker-compose.yml` exposes the frontend via a Cloudflare Tunnel — it expects `cloudflared-credentials.json` next to `cloudflared-config.yml`, neither of which is committed — copy `cloudflared-config.example.yml` to `cloudflared-config.yml` and fill in the real tunnel ID/hostname.

## Known rough edges

- `service.generate_slug` has a fallthrough `return slug` after the retry loop that's only reached on the success path; the loop already returns on success, so this is dead code worth tidying if touched.
- `crud.get_long_by_slug_from_db` does `res.long_url if res.long_url else None` — if `res` is `None` (slug not found) this raises `AttributeError` instead of returning `None`. The route still maps it to a 400 via the `NoLongUrlFoundError` path, but only because `None.long_url` crashes before the check. Fix to `res.long_url if res else None` when in that file.
- `add_slug_to_db` catches `IntegrityError` around `session.add` (sync call that doesn't raise it) — the integrity violation actually happens at `await session.commit()`, which is outside the try. The retry logic in `service.generate_slug` therefore doesn't currently trigger on real collisions.
