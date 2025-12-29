from fastapi import FastAPI, Query
from jobspy import scrape_jobs
import pandas as pd
import math

app = FastAPI(title="JobSpy API")

@app.get("/jobs")
def get_jobs(
    role: str = Query(...),
    location: str = Query("India"),
    limit: int = Query(20),
    hours_old: int = Query(24),
):
    jobs_df = scrape_jobs(
        site_name=["indeed", "linkedin", "google"],
        search_term=role,
        location=location,
        results_wanted=limit,
        hours_old=hours_old,
        country_indeed="India",
        verbose=0
    )

    # 🔴 IMPORTANT FIX: Replace NaN with None
    # to run the api - uvicorn jobspy_api:app --reload --port 8000
    jobs_df = jobs_df.where(pd.notnull(jobs_df), None)

    return jobs_df.to_dict(orient="records")
