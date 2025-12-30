from fastapi import FastAPI, Query, HTTPException
from jobspy import scrape_jobs
import pandas as pd

app = FastAPI(title="JobSpy Global API (Scalable)")

# 🌍 Indeed-supported countries (normalized)
INDEED_COUNTRIES = {
    "argentina", "australia", "austria", "bahrain",
    "belgium", "brazil", "canada", "chile",
    "colombia", "costa rica", "czech republic",
    "denmark", "ecuador", "egypt", "finland",
    "france", "germany", "greece", "hong kong",
    "hungary", "india", "ireland", "israel",
    "italy", "japan", "kuwait", "luxembourg",
    "malaysia", "mexico", "netherlands",
    "new zealand", "norway", "oman", "pakistan",
    "panama", "peru", "philippines", "poland",
    "portugal", "qatar", "romania", "saudi arabia",
    "singapore", "south africa", "south korea",
    "spain", "sweden", "switzerland", "taiwan",
    "thailand", "turkey", "united arab emirates",
    "uk", "usa", "uruguay", "vietnam"
}

MAX_LIMIT = 100

@app.get("/jobs")
def get_jobs(
    role: str = Query(..., min_length=2),
    country: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=MAX_LIMIT),
    hours_old: int = Query(24, ge=1, le=168),
):
    role = role.strip()
    country_clean = country.strip().lower()

    # 🧠 Always supported globally
    sites = ["linkedin", "google"]

    # 🧠 Enable Indeed only if supported
    use_indeed = country_clean in INDEED_COUNTRIES
    if use_indeed:
        sites.append("indeed")

    # 🔍 Google Jobs needs explicit query
    google_search_term = f"{role} jobs in {country}"

    scrape_args = {
        "site_name": sites,
        "search_term": role,
        "google_search_term": google_search_term,
        "results_wanted": min(limit * 2, 200),
        "hours_old": hours_old,
        "verbose": 0
    }

    if use_indeed:
        scrape_args["country_indeed"] = country

    try:
        jobs_df = scrape_jobs(**scrape_args)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if jobs_df is None or jobs_df.empty:
        return []

    # 🧹 Normalize output for UI
    required_columns = [
        "site",
        "title",
        "company",
        "job_url",
        "date_posted",
        "is_remote"
    ]

    jobs_df = jobs_df[[c for c in required_columns if c in jobs_df.columns]]
    jobs_df = jobs_df.drop_duplicates(subset=["job_url"])
    jobs_df = jobs_df.head(limit)
    jobs_df = jobs_df.where(pd.notnull(jobs_df), None)

    return jobs_df.to_dict(orient="records")
