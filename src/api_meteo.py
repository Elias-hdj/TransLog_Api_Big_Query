"""Collecte des prévisions météo via Open-Meteo."""

import requests
import pandas as pd
from datetime import date

from config.settings import WEATHER_API_URL, HUBS
from src.logger import get_logger

log = get_logger("weather")


def fetch_weather(forecast_days: int = 7) -> pd.DataFrame:
    """Récupère les prévisions météo pour chaque hub logistique."""
    rows = []
    for h in HUBS:
        params = {
            "latitude": h["lat"],
            "longitude": h["lon"],
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "precipitation_sum,wind_speed_10m_max,snowfall_sum"
            ),
            "timezone": "Europe/Paris",
            "forecast_days": forecast_days,
        }
        try:
            resp = requests.get(WEATHER_API_URL, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            log.error(f"Erreur API météo pour {h['hub']} : {e}")
            continue

        data = resp.json()
        daily = data.get("daily", {})
        for i, d in enumerate(daily.get("time", [])):
            rows.append({
                "date_collecte": date.today(),
                "hub": h["hub"],
                "latitude": h["lat"],
                "longitude": h["lon"],
                "date_prevision": pd.to_datetime(d).date(),
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precipitation": daily["precipitation_sum"][i],
                "vent_max": daily["wind_speed_10m_max"][i],
                "neige": daily.get("snowfall_sum", [0] * len(daily["time"]))[i],
            })

    df = pd.DataFrame(rows)
    log.info(f"{len(df)} lignes météo prêtes.")

    df["date_collecte"] = pd.to_datetime(df["date_collecte"]).dt.date
    df["date_prevision"] = pd.to_datetime(df["date_prevision"]).dt.date
    return df