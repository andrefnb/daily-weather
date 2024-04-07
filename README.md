# daily-weather
A simple daily weather pipeline that retrieves daily data from the openweathermap API to local json files and inserts it into a mongodb database, finally the local staging files are deleted 

To run the project, one needs to execute the following commands in the project root:
docker compose up --build -d

To config the cities which to retrieve data from, the property country_list in the dags/open_weather/config/open-weather.json must be edited
In order to make open weather API requests, the key must be added as the following file: dags/open_weather/config/weather_api_key.txt

To access the airflow client go to http://localhost:8080/.
The user and pass for airflow are both: airflow
Search for the dag named open_weather_app and turn it on to start the pipeline.
