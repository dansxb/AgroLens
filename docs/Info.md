# AgroLens — Project Info & Overview

This document explains what this project is, what has been built so far, how everything
fits together, and what the next steps are. Written for someone who is new to software
development but wants to understand what's going on.

---

## What Is This Project?

**AgroLens** is a startup idea being turned into a real software product. The goal is to
help farmers use less pesticide — not by guessing, but by using satellite images analyzed
by AI to show exactly which parts of a field need treatment and which parts don't.

Instead of spraying an entire field uniformly (which wastes pesticide and money, and
harms the environment), AgroLens gives farmers a precise map: "spray less here, spray
more there." This is called **Variable Rate Application (VRA)**.

The business model is a **SaaS subscription** (Software as a Service) — farmers pay a
monthly or yearly fee per hectare of land they want monitored.

---

## How the Project Was Created — Agent Teams

Instead of one AI writing everything, this project used an **agent team**: four separate
AI instances (called "agents"), each playing a different role, working in sequence.

Think of it like a real company structure:

```
CEO → gives goals to the →
  Planner → gives tasks to the →
    Software Developer → builds the code →
      Checker → reviews and approves/rejects everything
```

Each agent is defined by a "definition file" stored in `.claude/agents/`. These files
tell each agent who they are, what their job is, and what rules they must follow. The
agents were each run using the Claude Sonnet model.

---

## The Four Agents

### 1. CEO (`ceo.md`)
The CEO agent researched the market and defined the business strategy. It searched for
real 2024 market data, analyzed competitors, and produced a detailed strategy document.

**What it produced:** `docs/ceo-strategy.md` — 612 lines covering:
- The global precision agriculture market is worth ~$11.7 billion today and is projected
  to reach ~$24.1 billion by 2030
- Our cost advantage: we use **Sentinel-2 satellite imagery**, which is provided free by
  the European Space Agency. Competitors pay for commercial imagery — we don't.
- Target customers: mid-size European grain farmers first, then large US operations
- Pricing: €8/hectare/year for the starter plan (Farmers Edge charges €25+)
- Competitors analyzed: Taranis, Farmers Edge (went nearly bankrupt — cautionary tale),
  Climate Corporation (owned by Bayer — conflict of interest we can exploit)
- 16 specific MVP feature requirements (what the product must do in version 1)

### 2. Planner (`planner.md`)
The Planner read the CEO's strategy and turned it into a structured development plan —
essentially a detailed to-do list for the developer, organized in phases with clear
dependencies (meaning: "you can't build Phase 2 until Phase 1 is done").

**What it produced:** `docs/development-plan.md` — 905 lines covering 28 tasks across
6 phases, plus it created the entire folder and file structure for the project (162 files).

Each task specifies:
- Exactly what to build
- Which files to create or modify
- What it depends on
- How to verify it's working

### 3. Software Developer (`software-developer.md`)
The Developer took the Phase 0 tasks and wrote the actual code. It follows strict rules:
every Python function must have documentation (called docstrings), every variable must
have a type label, code must be formatted with a tool called Black, and no secrets
(passwords, API keys) can ever appear in the code files.

**What it produced:** 33 fully working files — the entire project foundation. See the
"What Was Built" section below for details.

### 4. Checker (`checker.md`)
The Checker reviewed every output from the other three agents. It runs security checks,
code quality checks, and verifies that everything aligns with the business goals.

**What it produced:** `docs/checker-review.md` — a detailed review that found:
- 2 **CRITICAL** issues (fixed immediately by the Checker itself)
- 1 **HIGH** issue (dev-log inaccuracy — fixed manually)
- 3 **MEDIUM** issues (to be addressed in Phase 1)

The Checker's status was **NEEDS CHANGES** — meaning Phase 0 is nearly done but a few
small things need attention before moving to Phase 1.

---

## What Was Built — The Codebase

Everything lives inside the `src/` folder. Here is what each part does:

```
src/
├── docker-compose.yml        ← Starts the entire local development environment
├── .env.example              ← Template for database passwords (you copy this to .env)
├── .gitignore                ← Tells Git which files to never upload (passwords, etc.)
├── README.md                 ← Setup instructions
│
├── backend/                  ← The server (Python / FastAPI)
├── frontend/                 ← The website (Next.js / TypeScript)
├── ml/                       ← AI and satellite image processing (Python)
└── infra/                    ← Infrastructure (database setup scripts)
```

### The Backend (server)
Located in `src/backend/`. This is the "brain" of the application — it handles requests
from the website, talks to the database, and runs AI processing jobs.

Built with **FastAPI** (a Python framework). Key files:

- `app/main.py` — the entry point. Starts the server and connects all the pieces.
- `app/core/config.py` — reads all settings from environment variables. If a required
  variable is missing, the app refuses to start and tells you what's missing.
- `app/core/security.py` — verifies that a user is who they say they are (using
  **Supabase Auth**, a service that handles logins).
- `app/db/session.py` — manages the connection to the database.
- `app/api/routes/health.py` — a simple `/health` endpoint. If you visit it, it
  returns "OK" if the server is running, or an error if the database is unreachable.
  Useful for checking that everything is working.

**Model files** (`app/models/`) — these define the shape of the data stored in the
database. For example, a `Field` model represents one farm field with its GPS boundary.
Currently these are **stubs** (placeholder files with no real code yet) — they will be
implemented in Phase 1.

### The Frontend (website)
Located in `src/frontend/`. This is what farmers see in their browser.

Built with **Next.js** (a React framework) and **TypeScript**. Key files:
- `app/page.tsx` — the landing page. Explains the product, shows pricing, has sign-up
  and login buttons.
- `app/layout.tsx` — the overall page wrapper (title, fonts, metadata for Google).
- `lib/supabase/` — handles user login/logout via Supabase.
- `lib/api/client.ts` — a typed wrapper for making requests to the backend server.

### The ML Pipeline (AI / satellite processing)
Located in `src/ml/`. This will be the core of the product — the part that actually
analyzes satellite images.

Currently all stub files. Will be implemented in Phase 2. Key modules planned:
- `sentinel/` — fetches satellite images from the European Space Agency's API
- `indices/` — calculates NDVI (a measure of plant health from satellite data)
- `zones/` — divides a field into low/medium/high pesticide need zones
- `prescription/` — generates the final prescription map and PDF report

---

## Key Concepts Explained Simply

### Docker
**Docker** packages the entire application (server, database, AI tools) into isolated
"containers" that run the same way on any computer. Instead of spending days installing
PostgreSQL, PostGIS, Python, Node.js, and 50 libraries one by one, you run one command
and everything starts automatically.

The file `src/docker-compose.yml` defines 6 containers that work together:

| Container | What it does |
|---|---|
| `postgres` | The database (with PostGIS for map data) |
| `redis` | A fast memory store used for background job queues |
| `backend` | The FastAPI server |
| `celery_worker` | Runs background jobs (like processing satellite images) |
| `celery_beat` | Schedules recurring jobs (like fetching new imagery every week) |
| `frontend` | The Next.js website |

### Environment Variables & Secrets
The app needs passwords and API keys (for Stripe, Supabase, AWS, Sentinel Hub, etc.).
These are **never** written into the code — that would be a major security risk if the
code were ever shared or uploaded to GitHub.

Instead, they live in `.env` files which are listed in `.gitignore` so they are never
accidentally uploaded anywhere.

The pattern used throughout this project:
- `.env.example` — a template file with placeholder values. This IS uploaded to GitHub.
  It tells other developers "these are the variables you need, fill them in yourself."
- `.env` — your actual file with real values. This NEVER gets uploaded.

### Alembic (Database Migrations)
The database needs tables to store data. **Alembic** is the tool that creates and updates
those tables over time.

Think of it like version control for your database structure. When a developer adds a new
field to a model (e.g., "farms now also store the farmer's phone number"), they create an
Alembic "migration" — a script that adds that column to the database. This keeps
everyone's database in sync.

Running `alembic upgrade head` applies all migrations up to the latest version. In Phase
0, this just creates the baseline tracking table (`alembic_version`) — no data tables yet
because the model files are still stubs.

### PostGIS
Regular databases store numbers and text. **PostGIS** is an extension to PostgreSQL that
also lets you store and query geographic shapes — like the GPS boundary of a farm field,
or calculate which fields overlap with a given satellite image tile. It is essential for
any application that works with maps and location data.

### Supabase
**Supabase** is a service that handles user authentication (login, signup, password reset)
so we don't have to build that from scratch. It also provides a JWT token (a secure
digital pass) that the backend verifies on every request to confirm the user is logged in.

### Celery
**Celery** runs tasks in the background. Analyzing a satellite image for an entire farm
takes time — you don't want the user to sit waiting for their browser to respond for
2 minutes. Instead, the backend says "I've queued your request" and Celery processes it
in the background, then notifies the user when it's done.

---

## Current Status

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Project foundation, infrastructure, core setup | ✅ Complete (with minor fixes needed) |
| Phase 1 | User accounts, farm/field data models, auth | ⬜ Not started |
| Phase 2 | Satellite imagery pipeline, NDVI calculation | ⬜ Not started |
| Phase 3 | AI prescription engine, VRA maps | ⬜ Not started |
| Phase 4 | Farmer dashboard (map UI) | ⬜ Not started |
| Phase 5 | Billing & subscriptions (Stripe) | ⬜ Not started |

### What "Phase 0 Complete" actually means
The full project skeleton exists — all the folders, all the file names, all the
configuration. The core infrastructure files are **fully implemented** (Docker, database
connection, security, config, landing page). The feature files (models, routes, ML
pipeline) are **stubs** — the files exist in the right place with the right names, but
contain only a one-line comment. They are ready to be filled in during the next phases.

### Before Phase 1 can begin
1. Run `alembic upgrade head` inside Docker and confirm it succeeds (see the Alembic
   verification guide for step-by-step instructions)
2. The Checker flagged that `CORS allow_headers=["*"]` should be tightened — fix before
   staging deployment
3. CEO needs to clarify whether there's a free tier (50 ha free) or paid-only plans,
   before the Stripe billing work starts in Phase 5

---

## All Files in This Project

### Agent Definitions (`.claude/agents/`)
These define each AI agent's role and rules. They are reusable — in the future, you can
start a Claude Code terminal session and say "create an agent team using the ceo, planner,
software-developer, and checker agents" and the same four roles will spin up.

| File | Role |
|---|---|
| `ceo.md` | Market research, business strategy, goals |
| `planner.md` | Converts goals into ordered dev tasks |
| `software-developer.md` | Writes code following strict quality rules |
| `checker.md` | Reviews all outputs, blocks bad code from proceeding |

### Documentation (`docs/`)

| File | Contents |
|---|---|
| `Info.md` | This document |
| `ceo-strategy.md` | Full business strategy (market data, pricing, competitors, goals) |
| `development-plan.md` | All 28 development tasks across 6 phases |
| `dev-log.md` | Record of everything the developer built and any deviations from the plan |
| `blockers.md` | Things that need to be resolved before work can continue |
| `checker-review.md` | Full review of Phase 0 — issues found, fixes applied |
| `agent-teams-reference.md` | Technical reference guide for working with Claude agent teams |

### Settings (`.claude/`)

| File | Purpose |
|---|---|
| `settings.local.json` | Local project settings — enables the experimental agent teams feature |

---

## How to Start the Application (When Ready)

Once Phase 1 is implemented and you have all real API keys filled in:

```bash
# 1. Go to the src folder
cd src/

# 2. Start all services
docker-compose up

# 3. Run database migrations
docker-compose run --rm --no-deps backend alembic upgrade head

# 4. Open the website in your browser
# http://localhost:3000   ← Frontend (website)
# http://localhost:8000   ← Backend API
# http://localhost:8000/docs  ← Auto-generated API documentation
```

---

## What Comes Next

Say **"continue with Phase 1"** to the AI and it will spawn:
1. The Developer agent to implement all user, farm, and field data models
2. The Checker agent to review the work before Phase 2 begins

Each phase builds on the last. By the end of Phase 4, AgroLens will be a working product
that a real farmer can log into, draw their field on a map, and receive a pesticide
prescription map generated from live satellite data.
