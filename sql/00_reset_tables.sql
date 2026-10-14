-- ============================================================
-- ATTENTION : DESTRUCTIF
-- Ce script supprime TOUTES les tables du dataset logistics.
-- Il ne doit JAMAIS etre execute automatiquement.
-- Usage : maintenance manuelle uniquement (setup initial, reset).
-- ============================================================

DROP TABLE IF EXISTS `translog-pipeline.logistics.fuel_prices`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.fuel_prices_staging`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.weather_daily`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.weather_daily_staging`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.execution_log`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.execution_log_staging`;
DROP TABLE IF EXISTS `translog-pipeline.logistics.hubs`;