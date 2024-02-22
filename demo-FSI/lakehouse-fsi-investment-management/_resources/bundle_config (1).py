# Databricks notebook source
# MAGIC %md 
# MAGIC ## Demo bundle configuration
# MAGIC Please ignore / do not delete, only used to prep and bundle the demo

# COMMAND ----------

{
  "name": "lakehouse-fsi-im",
  "category": "lakehouse",
  "title": "Capital Markets - Investment Management",
  "description": "Track and measure portfolio performance.",
  "fullDescription": "The Databricks Lakehouse Platform is an open architecture that combines the best elements of data lakes and data warehouses. In this demo, we'll show you how to build ... ADD HERE...</li><li>Leverage Databricks DBSQL and the warehouse endpoints to build dashboards to analyze the ingested data and understand the Portfolio Investments</li><li>Orchestrate all these steps with Databricks Workflow</li></ul>",
  "usecase": "Lakehouse Platform",
  "products": ["Delta Live Tables", "Databricks SQL", "Unity Catalog"],
  "related_links": [
      {"title": "View all Product demos", "url": "<TBD: LINK TO A FILTER WITH ALL DBDEMOS CONTENT>"}, 
      {"title": "Databricks for Financial Services", "url": "https://www.databricks.com/solutions/industries/financial-services"}],
  "recommended_items": ["lakehouse-iot-platform", "lakehouse-fsi-credit", "lakehouse-retail-c360"],
  "demo_assets": [
      {"title": "Delta Live Table pipeline", "url": "https://www.dbdemos.ai/assets/img/dbdemos/lakehouse-fsi-im-dlt-0.png"},
      {"title": "Databricks SQL Dashboard: Investment Management", "url": "https://www.dbdemos.ai/assets/img/dbdemos/lakehouse-fsi-im-dashboard-0.png"}],     
  "bundle": True,
  "tags": [{"dlt": "Delta Live Table"},  {"uc": "Unity Catalog"}, {"dbsql": "BI/DW/DBSQL"}],
  "notebooks": [
    {
      "path": "_resources/00-setup", 
      "pre_run": False, 
      "publish_on_website": False, 
      "add_cluster_setup_cell": False,
      "title":  "Prep data", 
      "description": "Helpers & setup."
    },
    {
      "path": "_resources/00-Data-Preparation", 
      "pre_run": False, 
      "publish_on_website": False, 
      "add_cluster_setup_cell": False,
      "title":  "Prep data", 
      "description": "Helpers & setup."
    },
    {
      "path": "/01-Ingest-Tick_data", 
      "pre_run": False, 
      "publish_on_website": False, 
      "add_cluster_setup_cell": False,
      "title":  "Ingest Tick Data", 
      "description": "Ingest Tick Data Description"
    },
    {
      "path": "02-Enrich-Corporate-Actions", 
      "pre_run": False, 
      "publish_on_website": False, 
      "add_cluster_setup_cell": False,
      "title":  "Enrich Corporate Actions", 
      "description": "Enrich Corporate Actions"
    },
    {
      "path": "03-Position-Data", 
      "pre_run": False,
      "publish_on_website": True, 
      "add_cluster_setup_cell": False,
      "title":  "Position Data", 
      "description": "Position Data Description"
    },
    {
      "path": "04-Prune-Backtesting-Data", 
      "pre_run": True, 
      "publish_on_website": True, 
      "add_cluster_setup_cell": False,
      "title":  "Prune Backtesting Data", 
      "description": "Prune Backtesting Data description"
    },
    {
      "path": "05-BacktestingA", 
      "pre_run": True, 
      "publish_on_website": True, 
      "add_cluster_setup_cell": True,
      "title":  "BacktestingA", 
      "description": "Backtesting A Description"
    },
    {
      "path": "05-BacktestingB", 
      "pre_run": False, 
      "publish_on_website": True, 
      "add_cluster_setup_cell": False,
      "title":  "BacktestingB", 
      "description": "Backtesting B Description"
    },
    {
      "path": "06-Tempo-Slippage", 
      "pre_run": True, 
      "publish_on_website": True, 
      "add_cluster_setup_cell": True,
      "title":  "Tempo Slippage", 
      "description": "Tempo Slippage Description"
    },
    {
      "path": "08-KPIs",
      "pre_run": True, 
      "publish_on_website": True, 
      "add_cluster_setup_cell": True,
      "title":  "KPIs", 
      "description": "KPIs Description"
    }
  ],
  "init_job": {
    "settings": {
        "name": "dbdemos_lakehouse_fsi_im_init_{{CURRENT_USER_NAME}}",
        "email_notifications": {
            "no_alert_for_skipped_runs": False
        },
        "timeout_seconds": 0,
        "max_concurrent_runs": 1,
        "tasks": [
            {
                "task_key": "init_data",
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/_resources/00-Data-Preparation",
                    "source": "WORKSPACE"
                },
                "job_cluster_key": "Shared_job_cluster",
                "timeout_seconds": 0,
                "email_notifications": {}
            },
            {
                "task_key": "start_dlt_pipeline",
                "pipeline_task": {
                    "pipeline_id": "{{DYNAMIC_DLT_ID_dlt-fsi-im}}",
                    "full_refresh": false
                },
                "timeout_seconds": 0,
                "email_notifications": {},
                "depends_on": [
                    {
                        "task_key": "init_data"
                    }
                ]
            },
            {
               "task_key": "tick_position_data",
               "depends_on": [
                    {
                        "task_key": "start_dlt_pipeline"
                    }
                    ],
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/03-Position-Data",
                    "source": "WORKSPACE"
                },
                "run_if": "ALL_SUCCESS",
                "new_cluster": {
                    "num_workers": 1,
                    "cluster_name": "",
                    "spark_version": "12.2.x-scala2.12",
                    "spark_conf": {},
                    "spark_env_vars": {
                      "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
                    },
                    "cluster_source": "JOB",
                    "init_scripts": [],
                    "data_security_mode": "USER_ISOLATION",
                    "runtime_engine": "STANDARD"
                },
                "timeout_seconds": 0,
                "email_notifications": {}
            },
            {
                "task_key": "prune_backtesting",
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/04-Prune-Backtesting-Data",
                    "source": "WORKSPACE"
                },
                "job_cluster_key": "Shared_job_cluster",
                "timeout_seconds": 0,
                "email_notifications": {},
                "depends_on": [
                      {
                          "task_key": "03-tick-position-data"
                      }
                  ]
            },
            {
                "task_key": "backtesting_a",
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/05-BacktestingA",
                    "source": "WORKSPACE"
                },
                "base_parameters": {"shap_enabled": "false"},
                "job_cluster_key": "Shared_job_cluster",
                "timeout_seconds": 0,
                "email_notifications": {},
                "depends_on": [
                      {
                          "task_key": "prune_backtesting"
                      }
                  ]
            },
            {
                "task_key": "backtesting_b",
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/05_BacktestingB",
                    "source": "WORKSPACE"
                },
                "base_parameters": {"shap_enabled": "false"},
                "job_cluster_key": "Shared_job_cluster",
                "timeout_seconds": 0,
                "email_notifications": {},
                "depends_on": [
                      {
                          "task_key": "prune_backtesting"
                      }
                  ]
            },
            {
                "task_key": "tempo_slippage",
                "notebook_task": {
                    "notebook_path": "{{DEMO_FOLDER}}/06-Tempo-Slippage",
                    "source": "WORKSPACE"
                },
                "base_parameters": {"shap_enabled": "false"},
                "job_cluster_key": "Shared_job_cluster",
                "timeout_seconds": 0,
                "email_notifications": {},
                "depends_on": [
                      {
                          "task_key": "backtesting_a"
                      }
                  ]
            }
        ],
        "job_clusters": [
            {
                "job_cluster_key": "Shared_job_cluster",
                "new_cluster": {
                    "spark_version": "12.2.x-cpu-ml-scala2.12",
                    "spark_conf": {
                        "spark.master": "local[*, 4]",
                        "spark.databricks.cluster.profile": "singleNode"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "spark_env_vars": {
                        "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
                    },
                    "enable_elastic_disk": True,
                    "data_security_mode": "SINGLE_USER",
                    "runtime_engine": "STANDARD",
                    "num_workers": 0
                }
            }
        ],
        "format": "MULTI_TASK"
    }
  },
  "cluster": {
      "spark_conf": {
        "spark.master": "local[*]",
        "spark.databricks.cluster.profile": "singleNode"
    },
    "custom_tags": {
        "ResourceClass": "SingleNode"
    },
    "single_user_name": "{{CURRENT_USER}}",
    "data_security_mode": "SINGLE_USER",
    "num_workers": 0
  }, 
  "pipelines": [
    {
      "id": "dlt-fsi-im",
      "run_after_creation": False,
      "definition": {
        "clusters": [
            {
                "label": "default",
                "autoscale": {
                    "min_workers": 1,
                    "max_workers": 2,
                    "mode": "LEGACY"
                }
            }
        ],
        "development": True,
        "continuous": False,
        "channel": "PREVIEW",
        "edition": "ADVANCED",
        "photon": True,
        "libraries": [
            {
                 "notebook": {
                    "path": "{{DEMO_FOLDER}}/_resources/00-Data-Preparation"
                },               
                "notebook": {
                    "path": "{{DEMO_FOLDER}}/01-Ingest-Tick-Data"
                },
                "notebook": {
                    "path": "{{DEMO_FOLDER}}/02-Enrich-Corporate-Actions"
                },
                "notebook": {
                    "path": "{{DEMO_FOLDER}}/08-KPIs"
                }
            }
        ],
        "name": "dbdemos-fsi-im",
        "catalog": "dbdemos",
        "target": "fsi_capm_data"
      }
    }
  ]
}
