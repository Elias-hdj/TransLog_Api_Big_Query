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

# L'API Opendatasoft limite chaque requete a 100 enregistrements
PAGE_SIZE = 100


def fetch_fuel_prices(max_records: int = 000) -> pd.DataFrame:
    """Recupere les prix des carburants via pagination.

    L'API renvoie une ligne par station, avec un champ de prix par carburant.
    On transforme cela en une ligne par (station, carburant).
    """
    rows = []
    offset = 0
    total_fetched = 0

    while total_fetched < max_records:
        params = {"limit": PAGE_SIZE, "offset": offset}
        try:
            resp = requests.get(FUEL_API_URL, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            log.error(f"Erreur API carburant (offset={offset}) : {e}")
            break

        data = resp.json()
        results = data.get("results", [])
        if not results:
            break

        for rec in results:
            geom = rec.get("geom") or {}
            base = {
                "date_collecte": date.today(),
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
                row = base.copy()
                row["carburant"] = carb
                row["prix"] = prix
                row["date_maj"] = rec.get(maj_field)
                rows.append(row)

        total_fetched += len(results)
        offset += PAGE_SIZE
        log.info(f"Page recuperee : {len(results)} stations (total {total_fetched})")

        if len(results) < PAGE_SIZE:
            break

    df = pd.DataFrame(rows)
    if df.empty:
        log.warning("Aucune donnee carburant recuperee.")
        return df

    df = df.dropna(subset=["id_station", "prix"])
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df = df[(df["prix"] >= PRIX_MIN) & (df["prix"] <= PRIX_MAX)]
    df = df.drop_duplicates(subset=["date_collecte", "id_station", "carburant"])
    df["date_collecte"] = pd.to_datetime(df["date_collecte"]).dt.date
    df["date_maj"] = pd.to_datetime(df["date_maj"], errors="coerce", utc=True).dt.tz_localize(None)
    df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")

    log.info(f"{len(df)} lignes carburant pretes.")
    return df