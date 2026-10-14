"""Utilitaires BigQuery : client, MERGE, logs."""

import os
import json
import base64
import uuid
from datetime import datetime, timezone

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

from config.settings import PROJECT_ID, DATASET
from src.logger import get_logger

log = get_logger("bigquery")


def get_bq_client() -> bigquery.Client:
    key_b64 = os.environ.get("GCP_SA_KEY_B64")
    if not key_b64:
        log.warning("GCP_SA_KEY_B64 absent : utilisation des credentials par defaut.")
        return bigquery.Client(project=PROJECT_ID)

    key_json = base64.b64decode(key_b64).decode("utf-8")
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key_json)
    )
    return bigquery.Client(project=PROJECT_ID, credentials=creds)


def upsert(df: pd.DataFrame, table: str, key_cols: list, bq: bigquery.Client):
    if df.empty:
        log.warning(f"DataFrame vide pour {table}, rien a charger.")
        return

    staging = f"{PROJECT_ID}.{DATASET}.{table}_staging"
    target = f"{PROJECT_ID}.{DATASET}.{table}"

    job = bq.load_table_from_dataframe(
        df, staging,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
    )
    job.result()

    on_clause = " AND ".join([f"T.{c} = S.{c}" for c in key_cols])
    cols = list(df.columns)
    set_clause = ", ".join([f"T.{c} = S.{c}" for c in cols if c not in key_cols])
    insert_cols = ", ".join(cols)
    insert_vals = ", ".join([f"S.{c}" for c in cols])

    merge_sql = f"""
    MERGE `{target}` T
    USING `{staging}` S
    ON {on_clause}
    WHEN MATCHED THEN UPDATE SET {set_clause}
    WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """
    bq.query(merge_sql).result()
    log.info(f"MERGE termine pour {table} ({len(df)} lignes).")


def log_run(bq: bigquery.Client, source: str, statut: str, nb: int, msg: str = ""):
    """Enregistre une execution dans execution_log."""
    # IMPORTANT : utiliser un datetime tz-aware pour BigQuery (TIMESTAMP)
    now_utc = datetime.now(timezone.utc)
    row = [{
        "run_id": str(uuid.uuid4()),
        "date_run": now_utc,
        "source": source,
        "statut": statut,
        "nb_lignes": nb,
        "message": msg,
    }]
    df = pd.DataFrame(row)
    df["date_run"] = pd.to_datetime(df["date_run"], utc=True)
    bq.load_table_from_dataframe(
        df, f"{PROJECT_ID}.{DATASET}.execution_log"
    ).result()