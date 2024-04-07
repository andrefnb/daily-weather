import logging
import pathlib, json, urllib.request
from airflow import DAG
from datetime import timedelta, datetime

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.log.secrets_masker import mask_secret
from airflow import settings
from airflow.models import Connection
from airflow.providers.mongo.hooks.mongo import MongoHook


config_file_name = "open-weather.json"
current_file_path = pathlib.Path(__file__).resolve()
dag_folder = current_file_path.parents[0].resolve()
proj_config_path = dag_folder.joinpath('config').resolve()
data_path = dag_folder.joinpath('data').resolve()
config_file_path = proj_config_path.joinpath(config_file_name).resolve()
with open(config_file_path) as config_file:
    weather_config = json.load(config_file)


def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 3),
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


def download_files(**kwargs):
    templates_dict = kwargs["templates_dict"]
    api_key = templates_dict["api_key"]
    date = templates_dict["date"]
    target_path = templates_dict["target_path"]

    with open(target_path, "w") as new_file:
        all_cities_list = []

        # Ideally I would have a single endpoint to consume that would retrieve the data for a list of city names, but there is no such endpoint
        for city_name in templates_dict["cities"]:
            weather_endpoint = f"/data/2.5/weather?q={city_name}&appid={api_key}"
            weather_uri = f"https://api.openweathermap.org{weather_endpoint}"

            with urllib.request.urlopen(weather_uri) as file:
                    city_json = json.loads(file.read())
                    to_write_city_json = {
                        "city_name": city_json["name"],
                        "temp": city_json["main"]["temp"],
                        "pressure": city_json["main"]["pressure"],
                        "humidity": city_json["main"]["humidity"],
                        "temp_min": city_json["main"]["temp_min"],
                        "temp_max": city_json["main"]["temp_max"],
                        "dt": city_json["dt"],
                        "date": date

                    }
                    all_cities_list.append(to_write_city_json)
        json.dump(all_cities_list, new_file)


def create_connection_if_not_exists(conn_id, conn_type, host, port, login, password, schema):
    """
    Create a connection if it does not already exist.
    """
    #logger.info("Will attempt connection creation")
    #logger.log(7, "Will attempt connection creation")
    print("Will attempt connection creation")
    conn = Connection(
        conn_id=conn_id,
        conn_type=conn_type,
        host=host,
        port=port,
        login=login,
        password=password,
        schema=schema
    )
    session = settings.Session()
    conn_name = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()
    if str(conn_name) == str(conn.conn_id):
        #logger.warning(f"Connection {conn.conn_id} already exists") TODO
        print(f"Connection {conn.conn_id} already exists")
        return None

    session.add(conn)
    session.commit()
    #logger.info(Connection.log_info(conn)) TODO
    print(Connection.log_info(conn))
    #logger.info(f'Connection {conn_id} is created') TODO
    print(f'Connection {conn_id} is created')
    return conn


def insert_data_mongo(**kwargs):
    templates_dict = kwargs["templates_dict"]
    data_path = templates_dict["data_path"]
    json_data = json.load(open(data_path))

    hook = MongoHook(mongo_conn_id='mongodb_con')
    client = hook.get_conn()

    try:
        print(client.server_info())
    except Exception as e:
        print(e, "Unable to connect to the server.")

    hook.insert_many("city_weather", json_data, "weatherdb")



# Create api key variable for the weather api TODO put this in a init file?
api_var_name = "weather-api-key"
api_key_path = proj_config_path.joinpath('weather_api_key.txt').resolve()
create_variable_from_file(api_var_name, api_key_path)
# Mask api key
mask_secret(Variable.get(api_var_name))

cities = weather_config["country_list"]
weather_api_key = Variable.get("weather-api-key")

# Create connection if does not exist
create_connection_if_not_exists("mongodb_con", "MongoDB", "mongo", "27017", "mongo", "mongo", "weatherdb")

target_path = f"{data_path}/weather_data_" + "{{ ds }}.json"

with DAG('open_weather_app',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=True,
         max_active_runs=1) as dag:

    get_weather = PythonOperator(
        task_id="get_daily_data",
        python_callable=download_files,
        templates_dict={
            "cities": cities,
            "api_key": weather_api_key,
            "date": "{{ ds }}",
            "target_path": target_path
        }
    )

    insert_weather = PythonOperator(
        task_id="insert_daily_data_mongodb",
        python_callable=insert_data_mongo,
        templates_dict={
            "data_path": target_path
        }
    )

    delete_staging_data = BashOperator(
        task_id="delete_staging_data",
        bash_command=f'rm {target_path}',
    )

    # Dependencies
    get_weather >> insert_weather >> delete_staging_data


