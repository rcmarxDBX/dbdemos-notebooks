# Databricks notebook source
# MAGIC %md
# MAGIC ### Ingest Tick data from external location - DBFS

# COMMAND ----------

# MAGIC %md
# MAGIC ##Setting Context to use dbdemos catalog

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Tick Trade data. (from parquet files)

# COMMAND ----------

import dlt

@dlt.table
def tick_trades():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "parquet")
      .option("cloudFiles.schemaEvolutionMode", "none")
      .load("/dbdemos/fsi/investment-management/tick_trades_parq.parquet/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Tick Quote data (from parquet files)

# COMMAND ----------

@dlt.table
def tick_quotes():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "parquet")
      .option("cloudFiles.schemaEvolutionMode", "none")
      .load("/dbdemos/fsi/investment-management/tick_quotes_parq.parquet/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Positions data

# COMMAND ----------

@dlt.table
def positions():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/dbdemos/fsi/investment-management/positions/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Corporate Actions data

# COMMAND ----------

@dlt.table
def corporate_actions():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/dbdemos/fsi/investment-management/corporate_actions/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Clustered Tickers data

# COMMAND ----------

@dlt.table
def clustered_tickers():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/dbdemos/fsi/investment-management/clustered_tickers/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting Sectors data

# COMMAND ----------

@dlt.table
def sectors():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/dbdemos/fsi/investment-management/sectors/")
  )

# COMMAND ----------

# MAGIC %md
# MAGIC ####Ingesting list of FINRA firms

# COMMAND ----------

@dlt.table
def finra_firms():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/dbdemos/fsi/investment-management/finra_firms/")
  )
