# Databricks notebook source
dbutils.widgets.dropdown("reset_all_data", "false", ["true", "false"], "Reset all data")
dbutils.widgets.text('catalog', 'cap_markets', 'Catalog')
dbutils.widgets.text('db', 'capm_data', 'Database')

# COMMAND ----------

# MAGIC %run ../../../_resources/00-global-setup $reset_all_data=$reset_all_data $catalog=$catalog $db=$db

# COMMAND ----------

# MAGIC %run ./00-Data-preparation $reset_all_data=$reset_all_data

# COMMAND ----------

folder="/dbdemos/fsi/im"
if reset_all_data or is_folder_empty(folder):
  if reset_all_data and folder.startswith("/dbdemos/fsi"):
    dbutils.fs.rm(folder, True)
  download_file_from_git('/dbfs'+folder, "databricks-demos", "dbdemos-dataset", "/fsi/investment-management")
  ## Add n lines for each datasource
else:
  print("data already existing. Run with reset_all_data=true to force a data cleanup for your local demo.")


# COMMAND ----------

# Try to set all users as owner or full privilege
if catalog == 'dbdemos':
    spark.sql(f'alter schema {catalog}.{dbName} owner to `account users`')
    for t in spark.sql(f'SHOW TABLES in {catalog}.{dbName}').collect():
        try:
            spark.sql(f'GRANT ALL PRIVILEGES ON TABLE {catalog}.{dbName}.{t["tableName"]} TO `account users`')
            spark.sql(f'ALTER TABLE {catalog}.{dbName}.{t["tableName"]} OWNER TO `account users`')
        except Exception as e:
            if "NOT_IMPLEMENTED.TRANSFER_MATERIALIZED_VIEW_OWNERSHIP" not in str(e) and "STREAMING_TABLE_OPERATION_NOT_ALLOWED.UNSUPPORTED_OPERATION" not in str(e) :
                print(f'WARN: Couldn t set table {catalog}.{dbName}.{t["tableName"]} owner to account users, error: {e}')
