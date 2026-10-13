"""Point d'entrée du pipeline TransLog."""

from src.api_carburant import fetch_fuel_prices
from src.api_meteo import fetch_weather
from src.bigquery_utils import get_bq_client, upsert, log_run
from src.logger import get_logger

log = get_logger("pipeline")


def main():
    bq = get_bq_client()

    # --- Carburant ---
    try:
        df_fuel = fetch_fuel_prices()
        upsert(df_fuel, "fuel_prices",
               ["date_collecte", "id_station", "carburant"], bq)
        log_run(bq, "fuel", "OK", len(df_fuel))
    except Exception as e:
        log_run(bq, "fuel", "ERROR", 0, str(e))
        log.exception("Echec collecte carburant")

    # --- Météo ---
    try:
        df_weather = fetch_weather()
        upsert(df_weather, "weather_daily",
               ["date_collecte", "hub", "date_prevision"], bq)
        log_run(bq, "weather", "OK", len(df_weather))
    except Exception as e:
        log_run(bq, "weather", "ERROR", 0, str(e))
        log.exception("Echec collecte météo")


if __name__ == "__main__":
    main()