# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working with this repository.

## Repository Status

**Insight** is a sourcing intelligence platform that pulls company data from Salesforce and enriches it with news, leadership changes, funding signals, and AI-generated outreach strategies. It serves both a React web dashboard and a daily email digest.

---

## Development Branch

All development should happen on feature branches. The naming convention for Claude-managed branches is:

```
claude/<description>-<session-id>
```

Always push to the designated feature branch and never directly to `main` or `master`.

---

## Git Workflow

### Creating and pushing changes

```bash
# Stage changes
git add <files>

# Commit with a descriptive message
git commit -m "feat: describe what was done"

# Push to remote branch
git push -u origin <branch-name>
```

### Commit message conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation changes only
- `chore:` — maintenance tasks, dependency updates
- `refactor:` — code changes that neither fix a bug nor add a feature
- `test:` — adding or updating tests
- `ci:` — CI/CD configuration changes

---

## Project Structure

```
insight/
├── CLAUDE.md
├── .env.example           # Copy to .env and fill in credentials
├── .gitignore
├── backend/
│   ├── main.py            # FastAPI app + CORS + auth middleware + lifespan
│   ├── database.py        # SQLAlchemy engine + session helpers
│   ├── models.py          # Company, Signal, DigestLog ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── scheduler.py       # APScheduler: daily enrichment (6AM) + digest (7AM)
│   ├── requirements.txt
│   ├── routers/
│   │   ├── companies.py   # GET/POST /api/companies, /api/companies/{id}/enrich
│   │   ├── signals.py     # GET /api/signals/{company_id}
│   │   └── digest.py      # GET /api/digest/preview, POST /api/digest/send
│   ├── services/
│   │   ├── salesforce.py  # simple-salesforce: Account + Task/Note sync
│   │   ├── news.py        # NewsAPI enrichment
│   │   ├── linkedin.py    # RapidAPI LinkedIn company signals
│   │   ├── crunchbase.py  # Crunchbase funding signals
│   │   ├── ai_analyst.py  # OpenAI: summaries + cracking strategies
│   │   ├── enricher.py    # Async orchestrator for all services
│   │   └── email_digest.py # Jinja2 HTML email + SendGrid sender
│   └── templates/
│       └── digest.html    # Email digest HTML template
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js     # Vite + proxy to :8000
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js         # Axios client
        ├── components/
        │   ├── CompanyCard.jsx
        │   ├── FilterBar.jsx
        │   ├── SignalFeed.jsx
        │   └── CrackingBrief.jsx
        └── pages/
            ├── Dashboard.jsx
            └── CompanyDetail.jsx
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11+, FastAPI, Uvicorn |
| ORM / DB | SQLAlchemy 2.x, SQLite (MVP) |
| Background jobs | APScheduler (AsyncIOScheduler) |
| Salesforce | simple-salesforce |
| HTTP client | httpx (async) |
| AI | OpenAI GPT-4o |
| Email | SendGrid + Jinja2 HTML |
| Frontend | React 18, Vite 5, Axios |

---

## Development Workflows

### Setup

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env  # fill in credentials

# Frontend
cd frontend
npm install
```

### Running the Application

```bash
# Backend (from backend/)
uvicorn main:app --reload --port 8000

# Frontend (from frontend/)
npm run dev
# Opens at http://localhost:5173
```

### Initial Data Load

```bash
# 1. Sync accounts from Salesforce
curl -X POST http://localhost:8000/api/companies/sync \
  -H "Authorization: Bearer <your-api-key>"

# 2. Enrich all companies (news + LinkedIn + Crunchbase + OpenAI)
curl -X POST http://localhost:8000/api/enrich/all \
  -H "Authorization: Bearer <your-api-key>"

# 3. Preview the email digest in browser
open http://localhost:8000/api/digest/preview
```

---

## Key Conventions

- **Salesforce field**: `Priority__c` on Account (integer 1–5)
- **Priority 5** companies get AI "cracking strategies" generated automatically
- Enrichment clears old signals and re-fetches fresh data each run
- API auth: Bearer token via `API_KEY` env var (leave blank to disable for local dev)
- All datetimes stored in UTC

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SF_USERNAME` | Salesforce login email | Yes |
| `SF_PASSWORD` | Salesforce password | Yes |
| `SF_SECURITY_TOKEN` | Salesforce security token | Yes |
| `SF_DOMAIN` | `login` or `test` (sandbox) | Yes |
| `SF_OWNER_ID` | Your Salesforce User ID (18-char) | Yes |
| `NEWS_API_KEY` | newsapi.org API key | Yes |
| `RAPIDAPI_KEY` | RapidAPI key (LinkedIn) | Yes |
| `CRUNCHBASE_API_KEY` | Crunchbase Basic API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | Default: `gpt-4o` | No |
| `SENDGRID_API_KEY` | SendGrid API key | Yes |
| `DIGEST_RECIPIENT_EMAIL` | Where to send digests | Yes |
| `API_KEY` | Bearer token for API auth | No |
| `DATABASE_URL` | Default: `sqlite:///./insight.db` | No |
| `FRONTEND_URL` | Default: `http://localhost:5173` | No |

Create a `.env` file (never committed) with these values.

---

## CI/CD

> **Note:** Update once CI/CD pipelines are configured.

---

## For AI Assistants

When working in this repository:

1. **Read this file first** before making any changes.
2. **Understand the context** — check recent commits and open PRs for ongoing work.
3. **Follow conventions** — match the style and patterns already in use.
4. **Small, focused commits** — one logical change per commit.
5. **Never force-push** to shared branches.
6. **Ask before destructive actions** — deleting files, dropping data, etc.
7. **Update this file** whenever significant new patterns, tools, or workflows are introduced.
