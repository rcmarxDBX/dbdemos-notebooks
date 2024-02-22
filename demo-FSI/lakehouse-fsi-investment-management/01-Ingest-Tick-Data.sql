-- Databricks notebook source
-- MAGIC %md
-- MAGIC #Medallion Architecture
-- MAGIC <div><img width="1000px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Medallion.png"/></div>

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC # Simplify ETL with Delta Live Table
-- MAGIC
-- MAGIC DLT makes Data Engineering accessible for all. Just declare your transformations in SQL or Python, and DLT will handle the Data Engineering complexity for you.
-- MAGIC
-- MAGIC <img style="float:right" src="https://github.com/QuentinAmbard/databricks-demo/raw/main/product_demos/dlt-golden-demo-loan-1.png" width="700"/>
-- MAGIC
-- MAGIC **Accelerate ETL development** <br/>
-- MAGIC Enable analysts and data engineers to innovate rapidly with simple pipeline development and maintenance 
-- MAGIC
-- MAGIC **Remove operational complexity** <br/>
-- MAGIC By automating complex administrative tasks and gaining broader visibility into pipeline operations
-- MAGIC
-- MAGIC **Trust your data** <br/>
-- MAGIC With built-in quality controls and quality monitoring to ensure accurate and useful BI, Data Science, and ML 
-- MAGIC
-- MAGIC **Simplify batch and streaming** <br/>
-- MAGIC With self-optimization and auto-scaling data pipelines for batch or streaming processing 
-- MAGIC
-- MAGIC ## Our Delta Live Table pipeline
-- MAGIC
-- MAGIC We'll be using as input a raw dataset containing information on our customers Loan and historical transactions. 
-- MAGIC
-- MAGIC Our goal is to ingest this data in near real time and build table for our Analyst team while ensuring data quality.
-- MAGIC
-- MAGIC <!-- Collect usage data (view). Remove it to disable collection. View README for more details.  -->
-- MAGIC <img width="1px" src="https://www.google-analytics.com/collect?v=1&gtm=GTM-NKQ8TT7&tid=UA-163989034-1&aip=1&t=event&ec=dbdemos&ea=VIEW&dp=%2F_dbdemos%2Fdata-engineering%2Fdlt-loans%2F01-DLT-Loan-pipeline-SQL&cid=1444828305810485&uid=4450680294222722">

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Bronze: Ingest Tick Trades
-- MAGIC This ingests data into a streaming table **Bronze Tick Trades**. This data represents the **actual transacted price** for a given trade during the specified time period.
-- MAGIC
-- MAGIC Data range filtered to Q3 2019
-- MAGIC
-- MAGIC
-- MAGIC  <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Bronze_Tick_Trades.png"/></div>
-- MAGIC

-- COMMAND ----------


CREATE OR REFRESH LIVE TABLE bronze_tick_trades
AS
SELECT * FROM LIVE.tick_trades where date between '2019-07-01' and '2019-10-01'

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Bronze: Ingest Corporate Actions
-- MAGIC This is a materialized view of a reference table of **Corporate Actions** data over a period of time.   **Corporate actions** are events initiated by a publicly traded company that can have an impact on trading price, volume and shareholder value.
-- MAGIC
-- MAGIC
-- MAGIC  <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Bronze_Corp_Actions.png"/></div>
-- MAGIC

-- COMMAND ----------


CREATE OR REFRESH LIVE TABLE bronze_corp_actions 
AS 
SELECT * FROM  LIVE.corporate_actions

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Bronze: Ingest Tick Quotes
-- MAGIC This ingests data into a streaming table **Bronze Tick Quotes**.  This data represents **BID** and **ASK** prices for various trades over a given time range.
-- MAGIC
-- MAGIC Data range is filtered to just quotes for the month of July 2019
-- MAGIC <!--- This is an HTML comment in Markdown -->
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Bronze_Tick_Quotes.png"/></div>
-- MAGIC
-- MAGIC
-- MAGIC

-- COMMAND ----------


CREATE OR REFRESH LIVE TABLE bronze_tick_quotes
AS SELECT * FROM LIVE.tick_quotes where date between '2019-07-01' and '2019-08-01'

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Silver: Tick Data Closings
-- MAGIC
-- MAGIC This creates a materialized view called **Tick Data Closings**, derived from **Bronze Tick Trades**, using a Windowing Function with **PRICE** for a given **TICKER** to calculate the distinct **HIGH**, **LOW**, **OPEN** and **CLOSE** for trade information.
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Tick_Data_Closings.png"/></div>

-- COMMAND ----------



         CREATE OR REFRESH  LIVE TABLE tick_data_closings
AS
        SELECT  TICKER, DATE, `Low`, `High`, `Close`, `Open`,`MINPRICE`, `MAXPRICE`, `LASTPRICE`, `FIRSTPRICE` 
        FROM
                (SELECT TICKER, 
                        DATE, 
                        MIN(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS MINPRICE,
                        MAX(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS MAXPRICE,
                        LAST(PRICE)  OVER(PARTITION BY TICKER, date order by datetime) AS LASTPRICE,
                        FIRST(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS FIRSTPRICE,
                        MIN(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS Low,
                        MAX(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS High,
                        LAST(PRICE)  OVER(PARTITION BY TICKER, date order by datetime) AS Close,
                        FIRST(PRICE) OVER(PARTITION BY TICKER, date order by datetime) AS Open,
                        row_number() over (partition by TICKER, date order by datetime) rn
                FROM LIVE.bronze_tick_trades )
                WHERE rn = 1 
        GROUP BY TICKER, DATE, `Low`, `High`, `Close`, `Open`,`MINPRICE`, `MAXPRICE`, `LASTPRICE`, `FIRSTPRICE`
    

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ##Silver: Quote Based Volatility
-- MAGIC This creates a materialized view **Quote Based Volatility** from Bronze Tick Quotes that
-- MAGIC calculates **Spread Volatility** - which is the degree of variation between the bid and ask price for a particular security
-- MAGIC
-- MAGIC <div><img width="1200px" src="https://raw.githubusercontent.com/databricks-demos/dbdemos-resources/main/images/fsi/investment-management/Quote_Based_Volatility.png"/></div>
-- MAGIC

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE quote_based_volatility ( 
    CONSTRAINT spread_volatility EXPECT (spread_volatility < 3) )
as 

        SELECT a.ticker, b.date, b.minute, ask_price, bid_Price, ask_price - bid_price spread, ((ask_price - bid_price) - avg_spread) / stddev_spread spread_volatility
        from
                LIVE.bronze_tick_quotes a 
                join 
                (SELECT TICKER, date, date_trunc("Minute", from_unixtime(datetime)) minute,
                        avg(ask_price - bid_price) avg_spread,
                        stddev_samp(ask_price - bid_price) stddev_spread
                FROM LIVE.bronze_tick_quotes 
                where date = '2019-08-01'
                group by ticker, date, date_trunc("Minute", from_unixtime(datetime))) b 
                on a.ticker = b.ticker 
                and date_trunc("Minute", from_unixtime(a.datetime)) = b.minute
                and a.date = b.date
                where a.date = '2019-08-01'

-- COMMAND ----------

-- MAGIC %sql select * from LIVE.tick_quotes where date = '2019-08-01'
