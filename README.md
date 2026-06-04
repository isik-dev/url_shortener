# URL Shortener

A small, production-shaped URL shortener built with async FastAPI and async SQLAlchemy, containerized
end to end. Send a long URL, get back a 6-character slug; hit the slug, get redirected.

## Why this exists

A deliberately small service used to practice doing the boring parts properly: async I/O end to end,
collision-safe ID generation, a real test suite, and a one-command Docker setup — the same concerns
that matter in production, at a size you can read in one sitting.

## Architecture

```
client ──POST /short_url──▶ FastAPI ──▶ service layer ──▶ async SQLAlchemy ──▶ database
client ──GET  /{slug}─────▶ FastAPI ──▶ 302 redirect to the original URL
```

- **`src/main.py`** — FastAPI app, routes, dependency-injected async sessions, lifespan DB init with retry/backoff
- **`src/service.py`** — business logic: generate a slug, persist it, retry on collision
- **`src/shortener.py`** — slug generation
- **`src/database/`** — async engine, session factory, SQLAlchemy models, CRUD
- **`frontend/`** — minimal static UI served by nginx

## Design notes

- **Collision-safe slugs** — slugs are 6 characters from a 62-symbol alphabet (a–z, A–Z, 0–9), giving
  62^6 ≈ 56.8 billion combinations. They are drawn with `secrets.choice` (CSPRNG), and writes retry up
  to 5 times on a uniqueness clash before surfacing an error.
- **Async all the way down** — FastAPI + async SQLAlchemy (greenlet) so the redirect path never blocks
  on the database.
- **Resilient startup** — table creation on boot retries with backoff so the API can start before the
  database is fully ready under Docker Compose.

## Tech stack

Python, FastAPI, SQLAlchemy (async), Docker, Docker Compose, nginx, pytest

## Run it

```sh
docker compose up
```

The API comes up and creates its tables on first boot.

## API

| Method | Path          | Body                  | Returns                          |
|--------|---------------|-----------------------|----------------------------------|
| POST   | `/short_url`  | `{ "long_url": "…" }` | `{ "data": "<slug>" }`           |
| GET    | `/{slug}`     | —                     | `302` redirect to the long URL   |

## Tests

```sh
pytest
```

Covers the service layer (slug generation, collision retry, lookup) and the API endpoints.

## Roadmap

- [ ] URL validation before persistence
- [ ] Custom, human-readable slugs on request
- [ ] Load testing on the read/redirect path
- [ ] Deploy to a free tier (GCP / AWS)
