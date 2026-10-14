"""Point d'entree du pipeline TransLog."""

from dotenv import load_dotenv
load_dotenv()

from src.api_carburant import fetch_fuel_prices
from src.api_meteo import fetch_weather
from src.bigquery_utils import get_bq_client, upsert, log_run
from src.logger import get_logger

log = get_logger("pipeline")


def main():
    bq = get_bq_client()

    # --- Carburant ---
    try:
        df_fuel = fetch_fuel_prices(max_records=10000)
        upsert(df_fuel, "fuel_prices",
               ["date_collecte", "id_station", "carburant"], bq)
        try:
            log_run(bq, "fuel", "OK", len(df_fuel))
        except Exception:
            log.exception("Impossible d'ecrire le log fuel")
    except Exception as e:
        log.exception("Echec collecte carburant")
        try:
            log_run(bq, "fuel", "ERROR", 0, str(e))
        except Exception:
            log.exception("Impossible d'ecrire le log d'erreur fuel")

    # --- Meteo ---
    try:
        df_weather = fetch_weather()
        upsert(df_weather, "weather_daily",
               ["date_collecte", "hub", "date_prevision"], bq)
        try:
            log_run(bq, "weather", "OK", len(df_weather))
        except Exception:
            log.exception("Impossible d'ecrire le log weather")
    except Exception as e:
        log.exception("Echec collecte meteo")
        try:
            log_run(bq, "weather", "ERROR", 0, str(e))
        except Exception:
            log.exception("Impossible d'ecrire le log d'erreur weather")


if __name__ == "__main__":
    main()