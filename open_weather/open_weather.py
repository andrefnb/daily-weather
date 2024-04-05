import os
import pathlib, json, urllib.request
from airflow import DAG
from datetime import timedelta, datetime
#from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
#from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.utils.log.secrets_masker import mask_secret
from airflow import settings
from airflow.models import Connection


config_file_name = "open-weather.json"
current_file_path = pathlib.Path(__file__).resolve()
config_path = current_file_path.parents[1].joinpath('config').resolve()
data_path = current_file_path.parents[1].joinpath('data').resolve()
config_file_path = config_path.joinpath(config_file_name).resolve()
with open(config_file_path) as config_file:
    weather_config = json.load(config_file)


def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 5),
    'email': ['*******@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'on_failure_callback': on_failure_callback
}


def create_variable_from_file(var_name, file_path):
    with open(file_path, 'r') as file:
        api_key = file.read().strip()
        Variable.set(var_name, api_key)


def download_file(**kwargs):
    templates_dict = kwargs["templates_dict"]
    print("templates_dict", templates_dict)
    with urllib.request.urlopen(templates_dict["uri"]) as file:
        with open(templates_dict["target_path"], "wb") as new_file:
            new_file.write(file.read())


def connection_exists(conn_id):
    """
    Check if a connection with the given ID already exists.
    """
    return Connection.get_connection(conn_id=conn_id) is not None


def create_connection_if_not_exists(conn_id, conn_type, host, login, password):
    """
    Create a connection if it does not already exist.
    """
    if not connection_exists(conn_id):
        conn = Connection(
            conn_id=conn_id,
            conn_type=conn_type,
            host=host,
            login=login,
            password=password
        )
        conn.add()


# Create api key variable for the weather api TODO put this in a init file?
api_var_name = "weather-api-key"
create_variable_from_file(api_var_name, "weather_api_key.txt")
# Mask api key
mask_secret(Variable.get(api_var_name))

city_name = weather_config["country_list"][1]  # In the current API there is no way to get multiple cities TODO
api_key = Variable.get("weather-api-key")
weather_endpoint = f"/data/2.5/weather?q={city_name}&appid={api_key}"
weather_uri = f"https://api.openweathermap.org{weather_endpoint}"
target_path = f"{data_path}/weather_data_{city_name}_"+"{{ ds }}.json"

# Create connection if does not exist
#conn_id = "weather_data"
#create_connection_if_not_exists(conn_id, conn_type, host, login, password)


with DAG('open_weather_app',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:


    get_weather = PythonOperator(
        task_id="get_daily_data",
        python_callable=download_file,
        templates_dict={
            "uri": weather_uri,
            "target_path": target_path
        }
    )



    # Dependencies
    #check_data_availability >> get_weather
