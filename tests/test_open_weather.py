import json, pathlib
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

from airflow.dags.open_weather.utils import download_weather_data


def test_download_files_with_mock():
    # Mocking the templates_dict
    templates_dict = {
        "api_key": "mock_api_key",
        "date": "2024-04-08",
        "target_path": "./data/weather_data.json",
        "cities": ["London", "Paris"]
    }

    # Mocking the response from the weather API
    mock_weather_data = {
        "name": "Mock City",
        "main": {
            "temp": 25.5,
            "pressure": 1015,
            "humidity": 60,
            "temp_min": 22,
            "temp_max": 28
        },
        "dt": 1649481600  # Mock timestamp
    }
    mock_json_response = json.dumps(mock_weather_data)

    # Mocking the urlopen function
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mocking the behavior of urlopen
        mock_urlopen.return_value.read.return_value = mock_json_response

        # Mocking the open function to capture file write
        with patch('builtins.open', mock_open()) as mock_file:
            # Execute the function
            download_weather_data(templates_dict=templates_dict)

            # Assert that the file was opened and written to
            mock_file.assert_called()

            # Assert that the expected weather data was written to the file
            expected_weather_data = [
                {
                    "city_name": "Mock City",
                    "temp": 25.5,
                    "pressure": 1015,
                    "humidity": 60,
                    "temp_min": 22,
                    "temp_max": 28,
                    "dt": 1649481600,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
            real_data = json.load("./data/weather_data.json")
            assert(real_data == expected_weather_data)

def test_download_weather_data():
    # TEST without mocking functionality for requests and open

    # Mocking the templates_dict
    current_file_path = pathlib.Path(__file__).resolve()
    root_folder = current_file_path.parents[1].resolve()
    proj_config_path = root_folder.joinpath('airflow/dags/open_weather/config').resolve()
    api_key_path = proj_config_path.joinpath('weather_api_key.txt').resolve()
    file = open(api_key_path, "r")
    content = file.read()
    templates_dict = {
        "api_key": content,
        "date": "2024-04-08",
        "target_path": "./data/weather_data.json",
        "cities": ["London", "Paris"]
    }
    download_weather_data(templates_dict=templates_dict)

    expected_weather_data = [
      {
        "city_name": "London",
        "temp": 283.85,
        "pressure": 999,
        "humidity": 83,
        "temp_min": 281.96,
        "temp_max": 285.37,
        "dt": 1712615110,
        "date": "2024-04-08"
      },
      {
        "city_name": "Paris",
        "temp": 286.45,
        "pressure": 1007,
        "humidity": 74,
        "temp_min": 285.35,
        "temp_max": 288.02,
        "dt": 1712615095,
        "date": "2024-04-08"
      }
    ]
    f = open("./data/weather_data.json")
    real_data = json.load(f)
    print(real_data)
    assert(real_data == expected_weather_data)
