import subprocess
from dagster import job, op


@op
def scrape_telegram_data():
    subprocess.check_call(["python", "src/scraper.py"])


@op
def load_raw_to_postgres():
    subprocess.check_call(["python", "src/load_raw_to_postgres.py"])


@op
def run_dbt_transformations():
    subprocess.check_call(["dbt", "run"], cwd="medical_warehouse")


@op
def run_yolo_enrichment():
    subprocess.check_call(["python", "src/yolo_detect.py"])
    subprocess.check_call(["python", "src/load_yolo_to_postgres.py"])
    subprocess.check_call(["dbt", "run", "-s", "fct_image_detections"], cwd="medical_warehouse")


@job
def full_pipeline():
    # No explicit dependencies; ops can be triggered individually from the UI.
    scrape_telegram_data()
    load_raw_to_postgres()
    run_dbt_transformations()
    run_yolo_enrichment()
