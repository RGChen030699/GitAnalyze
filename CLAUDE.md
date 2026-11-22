# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

GitAnalyze is a dashboard application. The repo is currently a Django + Django REST Framework skeleton in `backend/`: no project apps, models, or API endpoints exist yet, and only `admin/` is routed.

## Commands

Run everything from the repo root.

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

pytest                                                    # all tests
pytest backend/tests/test_smoke.py::test_project_settings_load  # single test

ruff check .
ruff format .
mypy backend

python backend/manage.py migrate
python backend/manage.py runserver
python backend/manage.py makemigrations
```

## Architecture and conventions

- `backend/` is the Python import root, set by `pythonpath` in `pytest.ini` and implicitly by `manage.py` living there. Import as `config.settings`, not `backend.config.settings`.
- All settings live in the single module `backend/config/settings.py` and are driven by environment variables. `.env.example` lists them.
- **`.env` is not loaded automatically.** The project has no dotenv dependency, so variables must be exported in the shell.
- The database is selected by `POSTGRES_DB`: PostgreSQL when set, otherwise SQLite at `backend/db.sqlite3`. This also applies to `pytest`, so an exported `POSTGRES_DB` makes tests run against Postgres.
- DRF renders JSON only (`DEFAULT_RENDERER_CLASSES`), so the browsable API is unavailable.
- `settings.GITHUB_TOKEN` is reserved for a GitHub client that is not written yet. That client is expected to fail with a clear error when the token is missing. `requests` is the HTTP dependency, and `responses` is available for mocking it in tests.
- Time zone is UTC with `USE_TZ = True`, and a smoke test asserts this.
- Tooling targets Python 3.12 with a 100-character line length.
