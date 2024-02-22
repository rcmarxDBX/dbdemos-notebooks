# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Get data we will be uising to generate analysis

# COMMAND ----------

# MAGIC %pip install yfinance backtesting

# COMMAND ----------

# MAGIC %run ./_resources/00-setup $reset_all_data=false $catalog=dbdemos $db=fsi_capm_data

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

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    DoubleType,
    ArrayType, IntegerType
)

schema = StructType(
    [   StructField("index", IntegerType(), True), 
        StructField("TICKER", StringType(), True),
        StructField("Equity", DoubleType(), True)
    ]
)

df = spark.read.table("dbdemos.fsi_capm_data.tick_positions")

df2 = df.select("DATE", "PORTFOLIO_ID", "INSTRUMENT", "LASTPRICE")
df2 = df2.withColumnRenamed("LASTPRICE", "Close")
df2 = df2.withColumnRenamed("INSTRUMENT", "Symbol")
df2 = df2.withColumnRenamed("PORTFOLIO_ID", "PortfolioID")
df2 = df2.withColumnRenamed("DATE", "Date")

# Define Smooth Average Cross Strategy
class SmaCross(Strategy):
    n1 = 5
    n2 = 7

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


class BuyAndHoldStrategy(Strategy):
    def init(self):
        self.buy_signal = self.signal_close
        self.set_signal(self.buy_signal)
    def next(self):
        pass

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Using sample strategy to calculate returns with Smooth Average - long SM = 20, short SM = 10

# COMMAND ----------

# Run backtest for each symbol
def backtest_sma(symbol):
  import pandas as pd
  
  symbol = symbol.sort_values(by="DATE")
  # Run backtest
  bt = Backtest(data = symbol, strategy = SmaCross, cash=10000, commission = 0.01, exclusive_orders = True)

  # Transform data
  stats = bt.run()
  stats_pdf = stats.to_frame()
  stats_t = stats_pdf.transpose()
  stats_t.index.name = "index"

  return(pd.concat([symbol['TICKER'], stats_t['_equity_curve'][0].reset_index()[['index', 'Equity']]], axis=1))
  # return(stats_t.filter(items=['Start','End','Duration','Exposure Time [%]','Equity Final [$]','Equity Peak [$]','Return [%]','Buy & Hold Return [%]', 'Return (Ann.) [%]','Volatility (Ann.) [%]','Sharpe Ratio','Sortino Ratio','Calmar Ratio','Max. Drawdown [%]','Avg. Drawdown [%]','Max. Drawdown Duration','Avg. Drawdown Duration','# Trades','Win Rate [%]','Best Trade [%]','Worst Trade [%]','Avg. Trade [%]','Max. Trade Duration','Avg. Trade Duration','Profit Factor','Expectancy [%]', 'SQN','TICKER', 'trades', 'strategy','equity_curve']))

# COMMAND ----------

# Run backtest for each symbol
def backtest_buy_and_hold(symbol):
  import pandas as pd
  
  symbol = symbol.sort_values(by="DATE")
  # Run backtest
  bt = Backtest(data = symbol, strategy = BuyAndHoldStrategy, cash=10000, commission = 0.01, exclusive_orders = True)

  # Transform data
  stats = bt.run()
  stats_pdf = stats.to_frame()
  stats_t = stats_pdf.transpose()
  stats_t.index.name = "index"


  return(pd.concat([symbol['TICKER'], stats_t['_equity_curve'][0].reset_index()[['index', 'Equity']]], axis=1))
  # return(stats_t.filter(items=['Start','End','Duration','Exposure Time [%]','Equity Final [$]','Equity Peak [$]','Return [%]','Buy & Hold Return [%]', 'Return (Ann.) [%]','Volatility (Ann.) [%]','Sharpe Ratio','Sortino Ratio','Calmar Ratio','Max. Drawdown [%]','Avg. Drawdown [%]','Max. Drawdown Duration','Avg. Drawdown Duration','# Trades','Win Rate [%]','Best Trade [%]','Worst Trade [%]','Avg. Trade [%]','Max. Trade Duration','Avg. Trade Duration','Profit Factor','Expectancy [%]', 'SQN','TICKER', 'trades', 'strategy','equity_curve']))


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

# MAGIC %sql select * from dbdemos.fsi_capm_data.portfolio_ohlc

# COMMAND ----------

portfolio_stock_info = spark.table("dbdemos.fsi_capm_data.portfolio_ohlc")
# Run portofolio backtest in spark
sma_backtest = portfolio_stock_info.groupBy("TICKER").applyInPandas(backtest_sma, schema)

min_prices = spark.sql("""select ticker, 10000/first_close number_of_shares from (select distinct ticker, first(close) over (partition by ticker order by date) first_close from dbdemos.fsi_capm_data.portfolio_ohlc) foo""")

sma_backtest = sma_backtest.repartition(10)

sma_backtest.withColumn("strategy", lit("SMA")).write.option("mergeSchema", "true").mode('overwrite').saveAsTable("dbdemos.fsi_capm_data.ticker_backtests") 
display(spark.table("fsi_capm_data.ticker_backtests"))

# COMMAND ----------

portfolio_stock_info.join(min_prices, ['ticker']).selectExpr('row_number() over (partition by ticker order by date) index', 'ticker', 'number_of_shares*Close equity').withColumn("strategy", lit("HOLD")).write.insertInto("dbdemos.fsi_capm_data.ticker_backtests")

# COMMAND ----------

# MAGIC %sql select * from dbdemos.fsi_capm_data.ticker_backtests where ticker = 'NVDA' and index >=1 and index <= 64
