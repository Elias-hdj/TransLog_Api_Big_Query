-- ============================================
-- TransLog - Creation des tables BigQuery
-- Dataset : logistics
-- ============================================

CREATE TABLE IF NOT EXISTS `translog-pipeline.logistics.fuel_prices` (
  date_collecte        DATE      NOT NULL,
  id_station           STRING    NOT NULL,
  nom_station          STRING,
  adresse              STRING,
  ville                STRING,
  code_postal          STRING,
  departement          STRING,
  region               STRING,
  latitude             FLOAT64,
  longitude            FLOAT64,
  carburant            STRING    NOT NULL,
  prix                 FLOAT64,
  date_maj             DATETIME,
  ingestion_timestamp  TIMESTAMP
)
PARTITION BY date_collecte
CLUSTER BY carburant, departement;

CREATE TABLE IF NOT EXISTS `translog-pipeline.logistics.weather_daily` (
  date_collecte    DATE      NOT NULL,
  hub              STRING    NOT NULL,
  latitude         FLOAT64,
  longitude        FLOAT64,
  date_prevision   DATE      NOT NULL,
  temp_max         FLOAT64,
  temp_min         FLOAT64,
  precipitation    FLOAT64,
  vent_max         FLOAT64,
  neige            FLOAT64
)
PARTITION BY date_collecte
CLUSTER BY hub;

CREATE TABLE IF NOT EXISTS `translog-pipeline.logistics.execution_log` (
  run_id      STRING,
  date_run    TIMESTAMP,
  source      STRING,
  statut      STRING,
  nb_lignes   INT64,
  message     STRING
)
PARTITION BY DATE(date_run);

CREATE TABLE IF NOT EXISTS `translog-pipeline.logistics.hubs` (
  hub        STRING NOT NULL,
  ville      STRING,
  latitude   FLOAT64,
  longitude  FLOAT64
);

INSERT INTO `translog-pipeline.logistics.hubs` (hub, ville, latitude, longitude)
VALUES
  ('Paris',     'Paris',     48.8566,  2.3522),
  ('Lyon',      'Lyon',      45.7640,  4.8357),
  ('Lille',     'Lille',     50.6292,  3.0573),
  ('Bordeaux',  'Bordeaux',  44.8378, -0.5792),
  ('Marseille', 'Marseille', 43.2965,  5.3698);