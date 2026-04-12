from dagster import Definitions, ScheduleDefinition
from dagster_dbt import DbtCliResource
from taxi_orchestrator.assets import clean_taxi_data, taxi_dbt_assets, DBT_PROJECT_DIR

daily_schedule = ScheduleDefinition(
    name="daily_taxi_pipeline",
    target="*",
    cron_schedule="0 6 * * *",
)

defs = Definitions(
    assets=[clean_taxi_data, taxi_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=str(DBT_PROJECT_DIR))
    },
    schedules=[daily_schedule]
)