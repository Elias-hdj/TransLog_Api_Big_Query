"""Collecte des prix des carburants via l'API Opendatasoft."""

import requests
import pandas as pd
from datetime import date

from config.settings import FUEL_API_URL, PRIX_MIN, PRIX_MAX
from src.logger import get_logger

log = get_logger("fuel")

# Correspondance entre nos noms et les champs de l'API
FUEL_FIELDS = {
    "Gazole": ("gazole_prix", "gazole_maj"),
    "SP95":   ("sp95_prix",   "sp95_maj"),
    "SP98":   ("sp98_prix",   "sp98_maj"),
    "E10":    ("e10_prix",    "e10_maj"),
    "E85":    ("e85_prix",    "e85_maj"),
}


def fetch_fuel_prices(limit: int = 100) -> pd.DataFrame:
    """Recupere les prix des carburants et renvoie un DataFrame nettoye.

    L'API renvoie une ligne par station, avec un champ de prix par carburant.
    On transforme cela en une ligne par (station, carburant).
    """
    rows = []
    params = {"limit": limit}
    try:
        resp = requests.get(FUEL_API_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"Erreur API carburant : {e}")
        return pd.DataFrame()

    data = resp.json()
    for rec in data.get("results", []):
        geom = rec.get("geom") or {}
        base = {
            "date_collecte": date.today().isoformat(),
            "id_station": str(rec.get("id")),
            "nom_station": rec.get("adresse"),
            "adresse": rec.get("adresse"),
            "ville": rec.get("ville"),
            "code_postal": rec.get("cp"),
            "departement": rec.get("code_departement") or rec.get("departement"),
            "region": rec.get("region"),
            "latitude": geom.get("lat"),
            "longitude": geom.get("lon"),
        }

        for carb, (price_field, maj_field) in FUEL_FIELDS.items():
            prix = rec.get(price_field)
            if prix is None:
                continue
            base_row = base.copy()
            base_row["carburant"] = carb
            base_row["prix"] = prix
            base_row["date_maj"] = rec.get(maj_field)
            rows.append(base_row)

    df = pd.DataFrame(rows)
    if df.empty:
        log.warning("Aucune donnee carburant recuperee.")
        return df

    df = df.dropna(subset=["id_station", "prix"])
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df = df[(df["prix"] >= PRIX_MIN) & (df["prix"] <= PRIX_MAX)]
    df = df.drop_duplicates(subset=["date_collecte", "id_station", "carburant"])
    df["ingestion_timestamp"] = pd.Timestamp.utcnow()
    log.info(f"{len(df)} lignes carburant pretes.")
    return df