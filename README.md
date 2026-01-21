# Medical Telegram Warehouse

End-to-end data pipeline to analyse Ethiopian medical and cosmetics products marketed via Telegram channels.  
The project ingests messages and images, builds a star-schema warehouse with dbt, enriches images with YOLOv8, serves analytics via FastAPI, and orchestrates everything with Dagster.

---

## Project Overview

This project focuses on two Telegram channels:

- `lobelia4cosmetics`
- `tikvahpharma`

The pipeline:

1. Scrapes messages and media from Telegram into a local data lake.
2. Loads raw JSON data into PostgreSQL.
3. Transforms raw data into a dimensional model with dbt.
4. Runs YOLOv8 object detection on images and stores detections.
5. Exposes analytical endpoints via FastAPI.
6. Orchestrates the steps with Dagster.

---

## Architecture

High-level flow:

```text
Telegram -> Telethon scraper (src/scraper.py)
         -> JSON files in data/raw/telegram_messages
         -> Postgres raw tables (src/load_raw_to_postgres.py)
         -> dbt staging + marts (medical_warehouse/)
         -> YOLOv8 image detections (src/yolo_detect.py, src/load_yolo_to_postgres.py)
         -> Star schema (fct_messages, fct_image_detections, dim_dates, dim_channels)
         -> FastAPI analytics API (api/)
         -> Dagster job (scripts/pipeline.py)
Core warehouse tables:

dim_dates: Calendar dimension.

dim_channels: Telegram channels with basic metrics.

fct_messages: One row per Telegram message.

fct_image_detections: YOLO detections + image categories (product_display, lifestyle, other).

Tech Stack
Python 3.13

PostgreSQL 18

dbt (Postgres adapter)

Telethon for Telegram scraping

YOLOv8 / ultralytics for image detection

FastAPI + Uvicorn for API

Dagster for orchestration

Docker Compose for local services (Postgres, etc.)

Setup Instructions
1. Clone and create virtual environment
bash
git clone https://github.com/<your-username>/medical-telegram-warehouse.git
cd medical-telegram-warehouse/medical-telegram-warehouse

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Environment variables
Create a .env file in the project root:

text
TELEGRAM_API_ID=xxxx
TELEGRAM_API_HASH=xxxx
TELEGRAM_SESSION_NAME=medical_telegram_session

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=telegram_db
.env is ignored by Git.

3. Start Postgres with Docker (optional)
bash
docker-compose up -d
This starts a local Postgres instance configured for the project.

Running the Pipeline
1. Scrape Telegram data
bash
python src/test_telegram_connection.py   # one-time test
python src/scraper.py                    # collects messages + images
Raw JSON and images are stored under data/raw/.

2. Load raw data into Postgres
bash
python src/load_raw_to_postgres.py
This populates the raw schema in telegram_db.

3. Run dbt transformations
bash
cd medical_warehouse
dbt run
dbt test
dbt docs generate
cd ..
Key models:

models/staging/stg_telegram_messages.sql

models/marts/dim_dates.sql

models/marts/dim_channels.sql

models/marts/fct_messages.sql

models/marts/fct_image_detections.sql

4. Run YOLO image detection
bash
python src/yolo_detect.py
python src/load_yolo_to_postgres.py
cd medical_warehouse
dbt run -s fct_image_detections
cd ..
YOLO uses yolov8n.pt (not committed to Git).

5. Start the FastAPI server
bash
uvicorn api.main:app --reload
Open:

Swagger UI: http://127.0.0.1:8000/docs

Available endpoints:

GET /api/reports/top-products

GET /api/channels/{channel_name}/activity

GET /api/search/messages

GET /api/reports/visual-content

6. Run Dagster UI
bash
dagster dev -f scripts/pipeline.py
Open:

Dagster UI: http://127.0.0.1:3000

You can trigger the full_pipeline job, which calls:

scrape_telegram_data

load_raw_to_postgres

run_dbt_transformations

run_yolo_enrichment

Repository Structure
text
medical-telegram-warehouse/
└── medical-telegram-warehouse/
    ├── api/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── main.py
    │   └── schemas.py
    ├── src/
    │   ├── __init__.py
    │   ├── scraper.py
    │   ├── test_telegram_connection.py
    │   ├── db_utils.py
    │   ├── load_raw_to_postgres.py
    │   ├── yolo_detect.py
    │   └── load_yolo_to_postgres.py
    ├── scripts/
    │   └── pipeline.py
    ├── medical_warehouse/
    │   ├── dbt_project.yml
    │   ├── models/
    │   │   ├── staging/
    │   │   │   └── stg_telegram_messages.sql
    │   │   └── marts/
    │   │       ├── dim_dates.sql
    │   │       ├── dim_channels.sql
    │   │       ├── fct_messages.sql
    │   │       ├── fct_image_detections.sql
    │   │       └── schema.yml
    │   └── tests/
    │       └── assert_no_future_messages.sql
    ├── data/           # raw + intermediate data (ignored by git)
    ├── logs/           # log files (ignored by git)
    ├── docker-compose.yml
    ├── requirements.txt
    ├── .gitignore
    └── README.md
Notes and Limitations
The pipeline is designed for local development and small-scale analysis, not production-scale volumes.

YOLO categorisation rules are simple heuristics based on detected classes and can be improved.

Dagster job currently runs the four main steps as separate ops; more advanced scheduling/partitioning is possible in future work.
