import json, pathlib
from unittest.mock import patch, mock_open
from datetime import datetime

from airflow.dags.open_weather.open_weather import download_weather_data


def test_download_files_with_mock():
    """
    Test download_weather_data core functionality. Mocks weather API and system function executions.
    """

    # Mocking the templates_dict
    templates_dict = {
        "api_key": "mock_api_key",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "target_path": ".data/weather_data.json",
        "cities": ["London"]
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
        mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_json_response

        # Mocking the open function to capture file write
        with patch('builtins.open', mock_open()) as mock_file:
            # Execute the function
            download_weather_data(templates_dict=templates_dict)

            # Assert that the file was opened and written to
            mock_file.assert_called_once_with(".data/weather_data.json", "w")

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
            mock_file.return_value.write.assert_called_once_with(json.dumps(expected_weather_data))
