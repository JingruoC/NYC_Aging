# Simple Servings Menu Planning MVP

Standalone NYC Aging menu-planning prototype for building, reviewing, and printing weekly menus from approved recipes.

The recommendation logic is intentionally deterministic. It does not use generative AI, LLM APIs, OpenAI APIs, or free-text generation. Suggestions come from approved recipe records, nutrition values, historical co-occurrence, menu patterns, and rule-based ranking.

## Current Stack

- Blazor Server / .NET 10 for the main web UI
- Python FastAPI for data, nutrition checks, and recommendation endpoints
- PostgreSQL for Docker-based local runs
- SQLite for the one-command local developer launcher
- SQLAlchemy, pandas, and scikit-learn-compatible service code for rule-based and historical ranking

The older `frontend/` Next.js prototype is still kept in the repository as a reference while the .NET version replaces it. The current app to review is `blazor-ui/`.

## Product Scope

The MVP currently supports:

- Admin / Department staff and Provider / Caterer role views
- Home to-do lists that change by role
- Approved recipe browsing, favorites, category filters, and recipe details
- New recipe submission based on the Simple Servings recipe-entry workflow
- Admin recipe review with direct field editing, comments, and email-ready comment summaries
- Weekly menu building with 5-day / 7-day service patterns and cycle weeks
- Component-based meal planning for breakfast, lunch, and dinner
- Sample menu browsing with calendar-style previews
- Saved menu list with legacy-style filters
- Admin menu review with cell-level comments, general comments, review history, and rule-based attention checks
- Provider-visible comments for returned menus
- Reports catalog for provider printing workflows
- Resource file list with categories, descriptions, audience, upload dates, and admin-only add/remove actions

## Project Layout

```text
.
├── backend/              # FastAPI app, SQLAlchemy models, seed data, deterministic recommendation services
├── blazor-ui/            # Current Blazor Server UI
├── frontend/             # Archived Next.js prototype for reference only
├── docker-compose.yml    # PostgreSQL + FastAPI + Blazor local stack
├── start-all.sh          # One-command SQLite-backed local launcher
└── README.md
```

## Quick Start

From the repository root:

```bash
bash ./start-all.sh
```

Then open:

- Web app: `http://127.0.0.1:5050`
- Backend health check: `http://127.0.0.1:8000/health`
- Backend API docs: `http://127.0.0.1:8000/docs`

The script creates `backend/.venv` if needed, runs the backend with `backend/local.db`, seeds mock data, and starts the Blazor UI.

## Docker Start

If Docker Desktop is installed:

```bash
docker compose up --build
```

Then open:

- Web app: `http://localhost:5050`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Docker Compose runs the current Blazor UI, not the archived Next.js prototype.

## Hosted Interactive Prototype

The simplest hosted prototype path is Render Blueprint deployment using `render.yaml`.

This runs a single Docker web service:

- Blazor Server is the public app.
- FastAPI runs inside the same container on `127.0.0.1:8000`.
- SQLite stores seeded demo data at `/tmp/simple-servings.db`.

Steps:

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint**.
3. Connect the GitHub repository.
4. Render will detect `render.yaml` and create `simple-servings-prototype`.
5. Open the generated `onrender.com` URL.

Prototype hosting limitation:

- The Render prototype uses SQLite on ephemeral container storage. It is good for click-through demos, but data can reset on redeploy or service restart.
- For a longer-running pilot, use the Docker Compose architecture or a managed PostgreSQL database.

## Manual Development Run

Start the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///$(pwd)/local.db"
export AUTO_SEED_DB=true
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the UI in a second terminal:

```bash
cd blazor-ui
dotnet restore
dotnet run -- --urls http://127.0.0.1:5050
```

## Main Routes

- `/` - role-specific home and to-do list
- `/recipes/home` - recipe home
- `/recipes` - recipe list
- `/recipes/new` - add recipe
- `/recipes/review` - admin recipe review
- `/recipes/favorites` - favorite recipes
- `/menus/list` - saved menu list
- `/menus/new/blank` - start a blank menu
- `/menus/new/sample` - start from a sample menu
- `/menus/new` - menu planner
- `/menus/drafts` - provider draft and returned menus
- `/menus/{id}` - saved menu review/detail
- `/sample-menus/{id}` - sample menu calendar preview
- `/reports` - report catalog
- `/resources` - resource files

## Backend API

Core endpoints:

- `GET /health`
- `GET /recipes`
- `GET /recipes/search?q=`
- `POST /recipes`
- `GET /recipes/{recipe_id}`
- `PUT /recipes/{recipe_id}`
- `GET /recipes/{recipe_id}/comments`
- `POST /recipes/{recipe_id}/comments`
- `GET /menus`
- `POST /menus`
- `GET /menus/{menu_id}`
- `PATCH /menus/{menu_id}/favorite`
- `GET /menus/{menu_id}/comments`
- `POST /menus/{menu_id}/comments`
- `POST /menus/analyze`
- `GET /sample-menus`
- `GET /sample-menus/{menu_id}`
- `POST /recommendations/autocomplete`
- `POST /recommendations/revisions`
- `POST /recommendations/similar-menus`
- `GET /analytics`

`GET /analytics` is used internally by the UI for usage and pairing summaries; there is no separate top-level analytics page in the current Blazor app.

## Data and Recommendations

The seed data includes realistic mock recipes, historical menus, sample menus, menu comments, recipe comments, nutrient thresholds, and common menu-review states. It is safe demo data and is meant to match the granularity of the existing Simple Servings workflow before real data integration.

Recommendation behavior is based on:

- Approved recipes only
- Matching meal type
- Complementary meal components
- Historical recipe co-occurrence
- Nutrition thresholds
- Repeated recipe detection
- Lower-sodium, higher-protein, and higher-fiber alternatives from existing recipes

## Configuration

Backend:

- `DATABASE_URL` - SQLAlchemy database URL
- `AUTO_SEED_DB` - set to `true` to seed demo data at startup
- `FRONTEND_URL` - allowed frontend origin for CORS

Blazor UI:

- `PythonApi__BaseUrl` - FastAPI base URL, for example `http://localhost:8000` or `http://backend:8000`

## Database Schema

The reference PostgreSQL schema is in `backend/sql/schema.sql`.

For the local SQLite launcher, the backend creates tables from SQLAlchemy models and applies lightweight SQLite-only compatibility migrations for older local databases.

## Current Limitations

- Authentication and authorization are simulated with the role switcher.
- Resource upload/open actions are local UI workflow mocks, not file storage integration.
- The prototype is not connected to the existing NYC Aging SQL Server yet.
- The archived Next.js prototype remains in `frontend/` for comparison and can be removed later if the team wants a smaller public repo.
- There is not yet an automated test suite; current validation is build and compile checks.

## GitHub and Hosting Notes

GitHub is a good place to share the source code. To let other people view the running app in a browser, this full-stack app needs a host that can run .NET, Python, and a database. GitHub Pages alone cannot host this app because Blazor Server and FastAPI require server processes.

Reasonable hosting options include Azure App Service / Container Apps, Render, Railway, Fly.io, or another Docker-capable environment.
