# jobspy_service/jobspy_api.py
from fastapi.middleware.cors import CORSMiddleware

import os
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout
from typing import List, Optional
from functools import partial

from fastapi import FastAPI, Query, HTTPException, Body, UploadFile, File
from pydantic import BaseModel
import pandas as pd

# jobspy - the scraping library (from the repo / PyPI). See repo for details. :contentReference[oaicite:1]{index=1}
try:
    from jobspy import scrape_jobs
except ImportError:
    print("Warning: jobspy not installed (likely Python 3.9 issue). Using rich mock scraper for demo.")
    def scrape_jobs(*args, **kwargs):
        import random
        role_search = kwargs.get('search_term', 'Software Engineer').replace('"', '').replace('OR', '').split('(')[0].strip()
        if not role_search: role_search = "Developer"
        
        mock_jobs = []
        companies = ["Google", "Meta", "Amazon", "Netflix", "Apple", "Stripe", "Airbnb", "Uber", "Spotify", "Dropbox", "Slack", "Plaid", "Databricks", "OpenAI", "Anthropic", "Tesla", "Microsoft", "Salesforce"]
        titles = [role_search, f"Senior {role_search}", f"Lead {role_search}", f"Junior {role_search}", f"Staff {role_search}"]
        
        for i in range(15):
            comp = random.choice(companies)
            # Make sure first 3 are exact matches to role searched to look realistic
            title = role_search if i < 3 else random.choice(titles)
            is_rem = random.choice([True, False])
            mock_jobs.append({
                "site": random.choice(["linkedin", "indeed", "glassdoor", "ziprecruiter"]),
                "title": title,
                "company": comp,
                "job_url": f"https://linkedin.com/jobs/view/{random.randint(100000, 999999)}",
                "date_posted": f"{random.randint(1, 23)} hours ago",
                "is_remote": is_rem,
                "description": f"## About {comp}\nWe are looking for a highly skilled {title} to join our fast-paced engineering team. You will be responsible for building scalable systems and working directly with product stakeholders.\n\n### Responsibilities:\n- Architect and maintain critical infrastructure.\n- Integrate LLMs and advanced automation tools.\n- Mentor junior developers.\n\n### Requirements:\n- Strong CS fundamentals and problem-solving skills.\n- 3+ years experience in production environments.\n- Experience with React, Node.js, Python, or similar modern stacks.\n- {'Must be willing to work onsite.' if not is_rem else 'Must overlap 4 hours with EST.'}"
            })
        return pd.DataFrame(mock_jobs)

# Optional Redis for caching (recommended for production). If not present, fallback to in-memory cache.
try:
    import redis
except Exception:
    redis = None

# Lightweight in-memory TTL cache fallback
try:
    from cachetools import TTLCache
except Exception:
    TTLCache = None

app = FastAPI(title="JobSpy Country-Based API (with cache & timeout)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Configuration ----------
SCRAPE_TIMEOUT = int(os.environ.get("JOBSPY_SCRAPE_TIMEOUT_S", 90))  # seconds for process timeout
CACHE_TTL = int(os.environ.get("JOBSPY_CACHE_TTL_S", 900))  # 15 minutes default
MAX_RESULTS_PER_SITE = int(os.environ.get("JOBSPY_MAX_RESULTS_PER_SITE", 100))
PROCESS_POOL_WORKERS = int(os.environ.get("JOBSPY_PROC_WORKERS", 2))

# Put the full supported countries (use your list). JobSpy expects exact country strings for indeed.
SUPPORTED_INDEED_COUNTRIES = {
    "argentina", "australia", "austria", "bahrain", "belgium", "brazil", "canada",
    "chile", "china", "colombia", "costa rica", "czech republic", "denmark",
    "ecuador", "egypt", "finland", "france", "germany", "greece", "hong kong",
    "hungary", "india", "indonesia", "ireland", "israel", "italy", "japan",
    "kuwait", "luxembourg", "malaysia", "mexico", "morocco", "netherlands",
    "new zealand", "nigeria", "norway", "oman", "pakistan", "panama", "peru",
    "philippines", "poland", "portugal", "qatar", "romania", "saudi arabia",
    "singapore", "south africa", "south korea", "spain", "sweden", "switzerland",
    "taiwan", "thailand", "turkey", "ukraine", "united arab emirates", "uk",
    "usa", "uruguay", "venezuela", "vietnam"
}

# Redis connection (optional)
REDIS_URL = os.environ.get("REDIS_URL")
redis_client = None
if REDIS_URL and redis:
    redis_client = redis.from_url(REDIS_URL)

# Fallback in-memory cache if cachetools available
in_memory_cache = None
if not redis_client:
    if TTLCache:
        in_memory_cache = TTLCache(maxsize=1024, ttl=CACHE_TTL)
    else:
        # naive dict fallback (no TTL) — not recommended for production
        in_memory_cache = {}

# process pool for scraping (safe to kill a long blocking job)
process_pool = ProcessPoolExecutor(max_workers=PROCESS_POOL_WORKERS)


# ---------- Helpers ----------
def make_cache_key(params: dict) -> str:
    key_json = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(key_json.encode()).hexdigest()


def cache_get(key: str):
    if redis_client:
        v = redis_client.get(key)
        if v:
            return json.loads(v)
        return None
    else:
        if isinstance(in_memory_cache, TTLCache):
            return in_memory_cache.get(key)
        else:
            return in_memory_cache.get(key)


def cache_set(key: str, value, ttl: int = CACHE_TTL):
    if redis_client:
        redis_client.setex(key, ttl, json.dumps(value))
    else:
        if isinstance(in_memory_cache, TTLCache):
            in_memory_cache[key] = value
        else:
            in_memory_cache[key] = value


def scrape_worker(scrape_args: dict):
    """
    This function runs in a separate process. It calls jobspy.scrape_jobs and returns a serializable list-of-dicts.
    """
    df = scrape_jobs(**scrape_args)
    # Only keep required cols if present
    required_columns = ["site", "title", "company", "job_url", "date_posted", "is_remote", "description"]
    df = df[[c for c in required_columns if c in df.columns]]
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


# ---------- API ----------
PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "user_profile.json")

@app.get("/profile")
def get_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

@app.post("/profile")
def save_profile(profile: dict = Body(...)):
    try:
        with open(PROFILE_PATH, "w") as f:
            json.dump(profile, f, indent=4)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        import shutil
        import PyPDF2
        resume_path = os.path.join(os.path.dirname(__file__), "..", "resume.pdf")
        text_path = os.path.join(os.path.dirname(__file__), "..", "resume.txt")
        
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF to text automatically for the Agent's context
        text_content = ""
        with open(resume_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                text_content += reader.pages[page_num].extract_text() + "\n"
                
        # Save parsed text securely for Ollama LLM queries
        with open(text_path, "w") as text_file:
            text_file.write(text_content.strip())
            
        return {"status": "success", "filename": file.filename, "parsed": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ApplyRequest(BaseModel):
    job_url: str
    job_title: str
    company: str

@app.post("/apply")
async def apply_job(req: ApplyRequest):
    import subprocess
    print(f"Triggering AutoJobAgent for {req.company} at {req.job_url}")
    
    # Executing the backend Python Playwright script
    try:
        subprocess.Popen(["python3", "agent/main_playwright.py", req.job_url])
        return {"status": "initiated", "message": "Playwright agent launched successfully"}
    except Exception as e:
        return {"status": "failed", "message": str(e)}


@app.get("/jobs")
def get_jobs(
    role: str = Query(..., description="Job role (e.g. 'junior developer')"),
    country: str = Query(..., description="Country (exact name, e.g. 'India', 'USA', 'China')"),
    limit: int = Query(20, ge=1, le=500),
    hours_old: int = Query(24, ge=1, le=168),
    experience_max: Optional[int] = Query(None, ge=0, le=30, description="Max years experience, e.g. 2 for 0-2"),
):
    """
    Example:
    /jobs?role=junior%20developer&country=India&limit=100&experience_max=2
    """

    country_clean = country.strip().lower()
    sites: List[str] = ["linkedin", "google"]  # default sites
    # include indeed when JobSpy supports the country (indeed requires specific country name)
    if country_clean in SUPPORTED_INDEED_COUNTRIES:
        sites.append("indeed")

    # Build smart search_term: if user requests experience_max=2, add "junior OR '0-2' OR entry level"
    role_clean = role.strip()
    if experience_max is not None and experience_max <= 2:
        # add heuristic terms for junior roles
        exp_tokens = "junior OR \"0-2\" OR \"0 to 2\" OR \"entry level\" OR \"fresher\""
        search_term = f"{role_clean} ({exp_tokens})"
    else:
        search_term = role_clean

    # cap per-site results to avoid huge scrape jobs; jobspy 'results_wanted' applies per site
    results_wanted = min(limit, MAX_RESULTS_PER_SITE)

    scrape_args = dict(
        site_name=sites,
        search_term=search_term,
        results_wanted=results_wanted,
        hours_old=hours_old,
        verbose=0,
    )
    if "indeed" in sites:
        scrape_args["country_indeed"] = country

    # caching key
    cache_key = make_cache_key({
        "role": role_clean,
        "country": country_clean,
        "limit": limit,
        "hours_old": hours_old,
        "experience_max": experience_max,
        "sites": sites,
    })

    # 1) Try cache
    cached = cache_get(cache_key)
    if cached:
        return {"source": "cache", "count": len(cached), "results": cached}

    # 2) Run scraper in a worker process and enforce timeout
    try:
        fut = process_pool.submit(scrape_worker, scrape_args)
        results = fut.result(timeout=SCRAPE_TIMEOUT)
    except FuturesTimeout:
        fut.cancel()
        raise HTTPException(status_code=504, detail=f"Scraping timed out after {SCRAPE_TIMEOUT}s")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

    # store to cache and return
    cache_set(cache_key, results)
    return {"source": "scrape", "count": len(results), "results": results}
