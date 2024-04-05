from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.dummy_operator import DummyOperator
#from airflow.utils.task_group import TaskGroup

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 12),
    'email': ['*******@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

with DAG('open_weather_app',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:
    start_pipeline = DummyOperator(
        task_id='start_pipeline'
    )

    # Dependencies
    #start_pipeline