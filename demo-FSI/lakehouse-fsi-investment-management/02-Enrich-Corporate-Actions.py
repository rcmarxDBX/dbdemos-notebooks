# Databricks notebook source
# MAGIC %pip install dbl-tempo

# COMMAND ----------

# MAGIC %md
# MAGIC # (Above) Install DBL-Tempo library      
# MAGIC ### *[Tempo](https://databrickslabs.github.io/tempo/)*
# MAGIC ### Tempo provides a set of Time Series Utilities for Data Teams Using Databricks
# MAGIC ##### The purpose of this project is to make time series manipulation with Spark simpler. Operations covered under this package include AS OF joins, rolling statistics with user-specified window lengths, featurization of time series using lagged values, and Delta Lake optimization on time and partition fields.

# COMMAND ----------

# MAGIC %md
# MAGIC ##Trade Corp Actions
# MAGIC Derived from table Bronze Corp Actions
# MAGIC
# MAGIC This materialized view will join records from bronze_tick_trades and bronze_corp_actions using an AsOfJoin as a function of the Tempo library.  Here we are using a Skew join optimized to obtain the latest corp_actions date for a particular ticker.
# MAGIC
# MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Trade_Corp_Actions.png"/></div>

# COMMAND ----------

import dlt 

from pyspark.sql.functions import * 
from tempo import *

@dlt.table(name="trade_corp_actions")
def asof_corp_actions():
  trades_df = dlt.read("bronze_tick_trades")
  corp_actions_df = dlt.read("bronze_corp_actions")
  
  trades_tsdf = TSDF(trades_df.withColumn("DATE", col("DATE").cast("date")), partition_cols = ['TICKER'], ts_col = 'DATE')
  corp_actions_tsdf = TSDF(corp_actions_df.withColumnRenamed("identifier", "TICKER").withColumnRenamed("effective_dt", "DATE").withColumn("DATE", col("DATE").cast("date")), partition_cols = ['TICKER'], ts_col = 'DATE')

  joined_df = trades_tsdf.asofJoin(corp_actions_tsdf, right_prefix="corp_actions_asof").df
  return(joined_df)
