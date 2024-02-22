# Databricks notebook source
# MAGIC %md
# MAGIC ## Get data we will be using to generate analysis

# COMMAND ----------

# MAGIC %pip install yfinance

# COMMAND ----------

# MAGIC %pip install backtesting

# COMMAND ----------

# MAGIC %run ./_resources/00-setup $reset_all_data=false $catalog=dbdemos $db=fsi_capm_data

# COMMAND ----------

df = spark.read.table("dbdemos.fsi_capm_data.tick_positions")

df2 = df.select("DATE", "PORTFOLIO_ID", "INSTRUMENT", "LASTPRICE")
df2 = df2.withColumnRenamed("LASTPRICE", "Close")
df2 = df2.withColumnRenamed("INSTRUMENT", "Symbol")
df2 = df2.withColumnRenamed("PORTFOLIO_ID", "PortfolioID")
df2 = df2.withColumnRenamed("DATE", "Date")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Using sample strategy to calculate returns with Smooth Average - long SM = 20, short SM = 10

# COMMAND ----------

from pyspark.sql import functions
from pyspark.sql.functions import col
import yfinance as yf
import warnings 
warnings.filterwarnings("ignore")

# Backtesting Lib
from backtesting import Backtest, Strategy
from backtesting.test import SMA
from backtesting.lib import crossover

# Control plotting
from bokeh.embed import components, file_html
from bokeh.resources import CDN

from pyspark.sql.functions import lit
from functools import reduce
from pyspark.sql import DataFrame

# Define Smooth Average Cross Strategy
class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Run backtest for each symbol
def backtest(symbol):
  
  # Run backtest
  bt = Backtest(data = symbol, strategy = SmaCross, cash=10000, commission = 0.01, exclusive_orders = True)

  # Transform data
  stats = bt.run()
  stats_pdf = stats.to_frame()
  stats_t = stats_pdf.transpose()
  stats_t["TICKER"] = symbol["TICKER"]
  
  # return summary
  return(stats_t.filter(items=['Start','End','Duration','Exposure Time [%]','Equity Final [$]','Equity Peak [$]','Return [%]','Buy & Hold Return [%]', 'Return (Ann.) [%]','Volatility (Ann.) [%]','Sharpe Ratio','Sortino Ratio','Calmar Ratio','Max. Drawdown [%]','Avg. Drawdown [%]','Max. Drawdown Duration','Avg. Drawdown Duration','# Trades','Win Rate [%]','Best Trade [%]','Worst Trade [%]','Avg. Trade [%]','Max. Trade Duration','Avg. Trade Duration','Profit Factor','Expectancy [%]', 'SQN','TICKER']))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run backtesting on portfolio 1 taking into consideration date stock was added to portfolio

# COMMAND ----------

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    DoubleType,
    ArrayType
)

schema = StructType(
    [ 
        StructField("Start", DoubleType(), True),
        StructField("End", DoubleType(), True),
        StructField("Duration", DoubleType(), True),
        StructField("Exposure Time [%]", DoubleType(), True),
        StructField("Equity Final [$]", DoubleType(), True),
        StructField("Equity Peak [$]", DoubleType(), True),
        StructField("Return [%]", DoubleType(), True),
        StructField("Buy & Hold Return [%]", DoubleType(), True),
        StructField("Return (Ann.) [%]", DoubleType(), True),
        StructField("Volatility (Ann.) [%]", DoubleType(), True),
        StructField("Sharpe Ratio", DoubleType(), True),
        StructField("Sortino Ratio", DoubleType(), True),
        StructField("Calmar Ratio", DoubleType(), True),
        StructField("Max. Drawdown [%]", DoubleType(), True),
        StructField("Avg. Drawdown [%]", DoubleType(), True),
        StructField("Max. Drawdown Duration", DoubleType(), True),
        StructField("Avg. Drawdown Duration", DoubleType(), True),
        StructField("# Trades", DoubleType(), True),
        StructField("Win Rate [%]", DoubleType(), True),
        StructField("Best Trade [%]", DoubleType(), True),
        StructField("Worst Trade [%]", DoubleType(), True),
        StructField("Avg. Trade [%]", DoubleType(), True),
        StructField("Max. Trade Duration", DoubleType(), True),
        StructField("Avg. Trade Duration", DoubleType(), True),
        StructField("Profit Factor", DoubleType(), True),
        StructField("Expectancy [%]", DoubleType(), True),
        StructField("SQN", DoubleType(), True),
        StructField("TICKER", StringType(), True)
    ]
)

# COMMAND ----------

from pyspark.sql.functions import col

SeriesAppend=[]
portfolios = spark.read.table("dbdemos.fsi_capm_data.tick_backtest").select("PORTFOLIO_ID").distinct().collect()
portfolio_info = spark.read.table("dbdemos.fsi_capm_data.tick_backtest")
# Run backtest for all portfolio stocks:
for ind in portfolios:
  
  port_id = ind["PORTFOLIO_ID"]
  portfolio_stock_info = portfolio_info.filter(col("PORTFOLIO_ID") == port_id).select("TICKER", "Low", "High", "Close", "Open")
  
  # Run portofolio backtest in spark
  b = portfolio_stock_info.groupBy("TICKER").applyInPandas(backtest, schema)
  b = b.withColumn("PORTFOLIO_ID", lit(port_id))
  SeriesAppend.append(b)


# COMMAND ----------

# MAGIC %md
# MAGIC ### Write results back to Unity Catalog (gold)

# COMMAND ----------

backtest_results = reduce(DataFrame.unionAll, SeriesAppend)
display(backtest_results)

# COMMAND ----------

backtest_results = backtest_results.withColumnRenamed("# Trades", "num_trades") \
                                    .withColumnRenamed("Avg. Drawdown Duration", "avg_drawdown_duration") \
                                    .withColumnRenamed("Avg. Drawdown [%]", "avg_drawdown_pctg") \
                                    .withColumnRenamed("Avg. Trade Duration", "avg_trade_duration") \
                                    .withColumnRenamed("Avg. Trade [%]", "avg_trade_pctg") \
                                    .withColumnRenamed("Best Trade [%]", "best_trade_pctg") \
                                    .withColumnRenamed("Buy & Hold Return [%]", "buy_and_hold_return_pctg") \
                                    .withColumnRenamed("Calmar Ratio", "calmar_ratio") \
                                    .withColumnRenamed("Duration", "duration") \
                                    .withColumnRenamed("End", "end") \
                                    .withColumnRenamed("Equity Final [$]", "equity_final_dllrs") \
                                    .withColumnRenamed("Equity Peak [$]", "equity_peak_dollrs") \
                                    .withColumnRenamed("Expectancy [%]", "expectancy_pctg") \
                                    .withColumnRenamed("Exposure Time [%]", "exposure_time_pctg") \
                                    .withColumnRenamed("Max. Drawdown Duration", "max_drawdown_duration") \
                                    .withColumnRenamed("Max. Drawdown [%]", "max_drawdown_pctg") \
                                    .withColumnRenamed("Max. Trade Duration", "max_trade_duration") \
                                    .withColumnRenamed("Profit Factor", "profit_factor") \
                                    .withColumnRenamed("Return (Ann.) [%]", "return_annual_pctg") \
                                    .withColumnRenamed("Return [%]", "return_pctg") \
                                    .withColumnRenamed("Worst Trade [%]", "worst_trade_pctg") \
                                    .withColumnRenamed("SQN", "SQN") \
                                    .withColumnRenamed("Sharpe Ratio", "sharpe_ratio") \
                                    .withColumnRenamed("Sortino Ratio", "sortino_ratio") \
                                    .withColumnRenamed("Start", "start") \
                                    .withColumnRenamed("Volatility (Ann.) [%]", "volatility_annual_pctg") \
                                    .withColumnRenamed("Win Rate [%]", "win_rate_pctg")

# COMMAND ----------

backtest_results.write.format("delta").mode("overwrite").saveAsTable("dbdemos.fsi_capm_data.backtest_results")
