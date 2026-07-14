from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "mta",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}



with DAG(
    dag_id="mta_dbt_pipeline",
    default_args=default_args,
    description="Run dbt transformations for MTA analytics",
    schedule="*/15 * * * *",   # every 15 minutes
    start_date=datetime(2026, 7, 1),
    catchup=False,
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
        cd /opt/airflow/mta_dbt &&
        dbt run
        """,
    )

    # dbt_test = BashOperator(
    #     task_id="dbt_test",
    #     bash_command="""
    #     cd /opt/airflow/mta_dbt &&
    #     dbt test
    #     """,
    # )
    dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command="""
    cd /opt/airflow/mta_dbt &&
    ls -la /home/airflow/.dbt &&
    dbt test
    """
)

    dbt_run >> dbt_test