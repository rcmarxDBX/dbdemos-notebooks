# Databricks notebook source
# MAGIC %run ./_resources/00-setup $reset_all_data=false $catalog=dbdemos $db=fsi_capm_data

# COMMAND ----------

tickers = spark.sql("""select ticker, count(1) ct from dbdemos.fsi_capm_data.tick_data_closings
group by ticker
having ct = 65""")

portfolio_ohlc = spark.table("dbdemos.fsi_capm_data.tick_data_closings").join(tickers, ['ticker'])
portfolio_ohlc.write.mode('overwrite').saveAsTable("dbdemos.fsi_capm_data.portfolio_ohlc")

# COMMAND ----------

# MAGIC  %sql
# MAGIC
# MAGIC -- join portfolio with tick_data for backtesting
# MAGIC CREATE OR REPLACE table dbdemos.fsi_capm_data.tick_backtest AS
# MAGIC SELECT port.PORTFOLIO_ID,
# MAGIC        clos.TICKER,
# MAGIC        clos.DATE,
# MAGIC        clos.MINPRICE as Low,
# MAGIC        clos.MAXPRICE as High,
# MAGIC        clos.LASTPRICE as Close,
# MAGIC        clos.FIRSTPRICE as Open
# MAGIC FROM fdbdemos.fsi_capm_data.tick_data_closings clos
# MAGIC JOIN dbdemos.fsi_capm_data.positions port
# MAGIC ON clos.TICKER = port.INSTRUMENT
