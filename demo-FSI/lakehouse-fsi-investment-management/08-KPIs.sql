-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## Equity Returns
-- MAGIC
-- MAGIC This materialized view is derived from **Tick Data Closings**.  The resulting table calculates the percentage change in the closing price from one day to the next using the **LAG()** SQL Windowing function.
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Equity_Returns.png"/></div>
-- MAGIC

-- COMMAND ----------

create live table equity_returns AS 
    SELECT
        date,
        ticker,
        Close / LAG(Close) OVER (partition by ticker ORDER BY date) - 1 AS stock_return
    FROM
        live.tick_data_closings
;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Benchmark Returns
-- MAGIC
-- MAGIC This materialized view is derived from **Tick Data Closings**.  The resulting table calculates the percentage change in the closing price from one day to the next using the **LAG()** SQL Windowing function for the **Benchmark S&P500 Index (SPY)**
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Benchmark_Returns.png"/></div>

-- COMMAND ----------

create live table benchmark_returns AS
    SELECT
        date,
        ticker,
        Close / LAG(Close) OVER (partition by ticker ORDER BY date) - 1 AS benchmark_return
    FROM
        live.tick_data_closings where ticker = 'SPY'

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Return Statistics
-- MAGIC
-- MAGIC This materialized view is derived from **Equity Returns** and **Benchmark Returns**.  This table, for each Ticker, calcuates the **Average** and **Standard Deviation** for that security and the respective benchmark.  In this case, the benchmark is the **S&P500(SPY)**
-- MAGIC
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Return_Statistics.png"/></div>

-- COMMAND ----------

-- MAGIC %python 
-- MAGIC
-- MAGIC import pandas as pd 
-- MAGIC
-- MAGIC

-- COMMAND ----------

create live table 
return_statistics AS 
    SELECT
        a.ticker,
        AVG(stock_return) AS avg_stock_return,
        STDDEV(stock_return) AS stock_return_stddev,
        AVG(benchmark_return) AS avg_benchmark_return,
        STDDEV(benchmark_return) AS benchmark_return_stddev
    FROM
        live.equity_returns a
    JOIN
        live.benchmark_returns ON a.date = live.benchmark_returns.date 
    group by a.ticker
;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Beta
-- MAGIC
-- MAGIC This materialized view is calculating the **Beta** for each security, by using the **COVAR_POP()** function to calculate the population covariance between the stock return and the benchmark return.  Further dividing this by the **VARIANCE()** of the benchmark return, results in what is known as the **Beta Coefficient**, which is a measure of a stock's risk of sensitivity to market movements.
-- MAGIC
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Beta.png"/></div>

-- COMMAND ----------

create live table beta AS 
    SELECT a.ticker,
        COVAR_POP(stock_return, benchmark_return) / VARIANCE(benchmark_return) AS beta
    FROM
        live.equity_returns a
    JOIN
        live.benchmark_returns ON a.date = live.benchmark_returns.date
group by a.ticker;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Sharpe Ratio
-- MAGIC
-- MAGIC This materialized view is calculating the **Sharpe Ratio** of a particular security.   The **Sharpe Ratio** represents a **"risk-adjusted"** return for a particular security, in that it provides a way to compare the return that was generated, relative to its level of risk or volatility.
-- MAGIC
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Sharpe_Ratio.png"/></div>
-- MAGIC

-- COMMAND ----------

create live table sharpe_ratio AS
    SELECT ticker,
        avg_stock_return / stock_return_stddev AS sharpe_ratio
    FROM
        live.return_statistics
;
