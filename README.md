# daily-weather
A simple daily weather pipeline that retrieves daily data from the openweathermap API to local json files and inserts it into a mongodb database, finally the local staging files are deleted 

## Intro
This project is comprised of the following structure:
```bash
.
├── airflow
│   ├── config
│   ├── dags
│   │   └── open_weather
│   │       ├── config
│   │       │   ├── open-weather.json
│   │       │   └── weather_api_key.txt
│   │       ├── data
│   │       ├── utils.py
│   │       └── open_weather.py
│   ├── Dockerfile
│   ├── logs
│   └── plugins
├── docker-compose.yaml
├── .env
├── mongo
│   └── mongo-init.js
├── tests
│   ├── data
│   ├── __init__.py
│   └── test_open_weather.py
└── README.md
```

In a nutshell, the bulk of this project is inside the "airflow" directory.

This is where airflow is mapped to go fetch what it needs: both the needed folders, such as config, dags, logs, and plugins, as well as the pipeline code that's needed for creating the DAGs themselves.

A database is important to store the weather data after being ingested, and since it's in a document-like structure, a non-relational database is being used - in this case, mongoDB.

A docker-compose file makes sure that all the required images are created and configured correctly to interact with each other for the needed operations. That way, all a user needs to do is build the images, start the containers and not worry about anything else. They can now just go ahead and use airflow on their browser.

The `.env` file defines needed airflow variables like the airflow user id and airflow project directory.

In the tests folder there are python files that test the pipeline functions. 
Currently there is a test without mocking that runs successfully for a given expected data. There is also another with mocking, but still needs development.
Mock is important because the public API is being updated regularly, so without mocking we need to update the expected data.

## Setup
To run the project, one needs to execute the following commands in the project root:
`docker compose up --build -d`

To select which cities the data is to be retrieved from, the property `country_list` in the `./airflow/dags/open_weather/config/open-weather.json` file must be edited.
Add, edit, or remove whatever cities you want.

In order to make open weather API requests, the file `./airflow/dags/open_weather/config/weather_api_key.txt` must be 
created with the API key to be usethat was added d - it's enough to have just its value, nothing else is needed.

To access the airflow client go to http://localhost:8080/.
The user and password for airflow are the same: `airflow` - this can be changed on the `docker-compose` file.
Search for the DAG named `open_weather_app` and turn it on to start the pipeline.

This is comprised of 3 tasks, one that downloads the files according to configuration, one that inserts in the mongo database, and another that removes the files from the staging area.
All these tasks are sequentially dependant, and run daily.

## Next steps
- Fix the test with mocking and add more tests (high priority)
- Add a Logger to report information
- Add error handling for lack of keys
- Add mongo secrets for docker
- Change airflow username and password for a real configuration
