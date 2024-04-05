from airflow.models import Variable
import yaml


def create_variable_from_file(file_path):
    with open(file_path, 'r') as file:
        api_key = file.read().strip()
        Variable.set("weather-api-key", api_key)


if __name__ == "__main__":
    create_variable_from_file("weather_api_key.txt")