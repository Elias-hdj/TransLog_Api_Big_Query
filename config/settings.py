"""Configuration centrale du pipeline TransLog."""

import os
from pathlib import Path

# ---------- CHEMINS ----------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"

# ---------- GCP ----------
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "translog-pipeline")
DATASET = "logistics"

# ---------- APIs ----------
FUEL_API_URL = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/records"
)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

CARBURANTS = ["Gazole", "SP95", "SP98", "E10", "E85"]

# ---------- HUBS LOGISTIQUES ----------
HUBS = [
    {"hub": "Paris",     "lat": 48.8566, "lon": 2.3522},
    {"hub": "Lyon",      "lat": 45.7640, "lon": 4.8357},
    {"hub": "Lille",     "lat": 50.6292, "lon": 3.0573},
    {"hub": "Bordeaux",  "lat": 44.8378, "lon": -0.5792},
    {"hub": "Marseille", "lat": 43.2965, "lon": 5.3698},
]

# ---------- REGLES QUALITE ----------
PRIX_MIN = 0.5   # €/L
PRIX_MAX = 3.0   # €/L

# ---------- LOGS ----------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")