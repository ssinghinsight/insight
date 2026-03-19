import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import init_db
    from scheduler import create_scheduler

    init_db()

    scheduler = create_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Insight Sourcing API",
    description="Salesforce-connected sourcing intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173"), "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API key auth middleware
API_KEY = os.getenv("API_KEY", "")


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Skip auth for health check and docs
    if request.url.path in ("/api/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)

    if API_KEY:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})

    return await call_next(request)


from routers import companies, signals, digest  # noqa: E402

app.include_router(companies.router)
app.include_router(signals.router)
app.include_router(digest.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "insight-sourcing"}


@app.post("/api/enrich/all")
async def enrich_all():
    from services.enricher import run_all_companies
    count = await run_all_companies()
    return {"status": "ok", "enriched": count}
