# Databricks notebook source
# MAGIC %pip install dbl-tempo

# COMMAND ----------

# MAGIC %md
# MAGIC ### Calculate Tick Metrics

# COMMAND ----------

# MAGIC %md
# MAGIC ### Join tick data with positions data

# COMMAND ----------

# MAGIC %run ../_resources/00-setup $reset_all_data=false $catalog=dbdemos $db=fsi_capm_data

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS dbdemos;
# MAGIC USE CATALOG dbdemos;
# MAGIC SELECT CURRENT_CATALOG();

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS fsi_capm_data;
# MAGIC USE fsi_capm_data;
# MAGIC SHOW TABLES IN fsi_capm_data;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE TABLE dbdemos.fsi_capm_data.tick_positions AS 
# MAGIC   SELECT  p.DATE,
# MAGIC           UNIX_TIMESTAMP(p.DATE) as DATE_NUM,
# MAGIC           p.PORTFOLIO_ID,
# MAGIC           p.INSTRUMENT,
# MAGIC           p.NUMBER_OF_SHARES,
# MAGIC           t.LASTPRICE,
# MAGIC           t.MINPRICE,
# MAGIC           t.MAXPRICE,
# MAGIC           (MAXPRICE - MINPRICE ) AS SPREAD,
# MAGIC           ((MAXPRICE - MINPRICE ) * p.NUMBER_OF_SHARES) AS GAINS
# MAGIC   FROM dbdemos.fsi_capm_data.positions p
# MAGIC   JOIN dbdemos.fsi_capm_data.tick_data_closings t
# MAGIC   ON p.INSTRUMENT = t.TICKER 
# MAGIC   AND p.DATE = t.DATE

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calculate Positions Metrics

# COMMAND ----------

# MAGIC %md
# MAGIC We should have have an overal PnL field and rolling 30-60-90 day returns, high, lows, yes.

# COMMAND ----------

# %python
# !pip install dbl-tempo

# COMMAND ----------

<<<<<<< Updated upstream
%python

from tempo import *
from pyspark.sql.functions import *
from pyspark import SparkFiles

import numpy as np
import pandas as pd

tsdf_positions = TSDF(spark.table("cap_markets.capm_data.tick_positions"), partition_cols=['PORTFOLIO_ID'], ts_col="DATE_NUM")

# 2628288 seconds in a month
rolling_stats3 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (3 * 2628288))
rolling_stats2 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (2 * 2628288))
rolling_stats1 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (1 * 2628288))

# Calculate 3/2/1 months 

rolling_stats1 = rolling_stats1.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")
rolling_stats2 = rolling_stats2.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")
rolling_stats3 = rolling_stats3.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")

# Now join data into one table
joined_30_60 = rolling_stats1.asofJoin(rolling_stats2, right_prefix="60")
joined_30_60_90 = joined_30_60.asofJoin(rolling_stats3, right_prefix="90")
returns_30_to_90 = joined_30_60_90.df.select("PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "MEAN_GAINS", "60_MEAN_GAINS", "90_MEAN_GAINS")
display(returns_30_to_90)

# Save final table to UC
returns_30_to_90.write.format("delta").mode("overwrite").saveAsTable("dbdemos.fsi_capm_data.port_rolling")
=======

from tempo import *
from pyspark.sql.functions import *
from pyspark import SparkFiles

import numpy as np
import pandas as pd

tsdf_positions = TSDF(spark.table("cap_markets.capm_data.tick_positions"), partition_cols=['PORTFOLIO_ID'], ts_col="DATE_NUM")

# 2628288 seconds in a month
rolling_stats3 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (3 * 2628288))
rolling_stats2 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (2 * 2628288))
rolling_stats1 = tsdf_positions.withRangeStats(colsToSummarize=["GAINS"], rangeBackWindowSecs = (1 * 2628288))

# Calculate 3/2/1 months 

rolling_stats1 = rolling_stats1.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")
rolling_stats2 = rolling_stats2.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")
rolling_stats3 = rolling_stats3.select("DATE_NUM","DATE","PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "COUNT_GAINS", "MEAN_GAINS")

# Now join data into one table
joined_30_60 = rolling_stats1.asofJoin(rolling_stats2, right_prefix="60")
joined_30_60_90 = joined_30_60.asofJoin(rolling_stats3, right_prefix="90")
returns_30_to_90 = joined_30_60_90.df.select("PORTFOLIO_ID", "INSTRUMENT", "NUMBER_OF_SHARES", "LASTPRICE", "MINPRICE", "MAXPRICE", "GAINS", "MEAN_GAINS", "60_MEAN_GAINS", "90_MEAN_GAINS")
display(returns_30_to_90)

# Save final table to UC
returns_30_to_90.write.format("delta").mode("overwrite").saveAsTable("cap_markets.capm_data.port_rolling")
>>>>>>> Stashed changes

# COMMAND ----------

# MAGIC %md
# MAGIC ### Join sector and portfolio tables

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC USE CATALOG dbdemos;
# MAGIC USE SCHEMA fsi_capm_data;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE dbdemos.fsi_capm_data.port_rolling_sector
# MAGIC COMMENT "Portfolio rolling calculations for 1,2, and 3 months with sector data" 
# MAGIC AS
# MAGIC   SELECT a.*, b.*
# MAGIC   FROM dbdemos.fsi_capm_data.port_rolling AS a
# MAGIC   LEFT JOIN dbdemos.fsi_capm_data.sectors b
# MAGIC   ON a.INSTRUMENT = b.Symbol
