"""Collecte des prix des carburants via l'API Opendatasoft."""

import requests
import pandas as pd
from datetime import date

from config.settings import FUEL_API_URL, CARBURANTS, PRIX_MIN, PRIX_MAX
from src.logger import get_logger

log = get_logger("fuel")


def fetch_fuel_prices(limit: int = 100) -> pd.DataFrame:
    """Récupère les prix des carburants et renvoie un DataFrame nettoyé.

    Aucun filtre côté API : on récupère les enregistrements puis on filtre
    côté Python sur le type de carburant.
    """
    rows = []
    params = {
        "limit": limit,
    }
    try:
        resp = requests.get(FUEL_API_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"Erreur API carburant : {e}")
        return pd.DataFrame()

    data = resp.json()
    for rec in data.get("results", []):
        carb = rec.get("carburant")
        if carb not in CARBURANTS:
            continue

        geom = rec.get("geom") or {}
        rows.append({
            "date_collecte": date.today().isoformat(),
            "id_station": rec.get("id"),
            "nom_station": rec.get("adresse"),
            "adresse": rec.get("adresse"),
            "ville": rec.get("ville"),
            "code_postal": rec.get("cp") or rec.get("code_postal"),
            "departement": rec.get("departement"),
            "region": rec.get("region"),
            "latitude": geom.get("lat"),
            "longitude": geom.get("lon"),
            "carburant": carb,
            "prix": rec.get("prix"),
            "date_maj": rec.get("date_maj"),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        log.warning("Aucune donnée carburant récupérée.")
        return df

    df = df.dropna(subset=["id_station", "prix"])
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df = df[(df["prix"] >= PRIX_MIN) & (df["prix"] <= PRIX_MAX)]
    df = df.drop_duplicates(subset=["date_collecte", "id_station", "carburant"])
    df["ingestion_timestamp"] = pd.Timestamp.utcnow()
    log.info(f"{len(df)} lignes carburant prêtes.")
    return df