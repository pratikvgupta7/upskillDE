import dagster as dg
import sys
from pathlib import Path
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

# add phase1 to the path so we can import from it
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'phase1'))
DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent / "taxi_analytics"
dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)

from clean import run_cleaning, CLEAN_DIR

@dg.asset
def clean_taxi_data():
    """Reads raw NYC taxi Parquet files and writes cleaned partitioned Parquet."""
    row_count = run_cleaning()

    return dg.MaterializeResult(
    metadata={
        "row_count": row_count,
        "clean_dir": str(CLEAN_DIR)
    }
    
    )

@dbt_assets(manifest=dbt_project.manifest_path)
def taxi_dbt_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
