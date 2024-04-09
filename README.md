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
├── testing_requirements.txt
└── README.md
```

In a nutshell, the bulk of this project is inside the "airflow" directory.

This is where airflow is mapped to go fetch what it needs: both the needed folders, such as config, dags, logs, and plugins, as well as the pipeline code that's needed for creating the DAGs themselves.

A database is important to store the weather data after being ingested, and since it's in a document-like structure, a non-relational database is being used - in this case, mongoDB.

A docker-compose file makes sure that all the required images are created and configured correctly to interact with each other for the needed operations. That way, all a user needs to do is build the images, start the containers and not worry about anything else. They can now just go ahead and use airflow on their browser.

The `.env` file defines needed airflow variables like the airflow user id and airflow project directory.

In the tests folder there are python files that test the pipeline functions. 
Currently there is one unit test that and mocks the weather API and other system functions like the open command and tests the `download_weather_data` core functionality. The creation of more tests is in the next steps section.
To test it run pytest in the tests file. A local `venv` with the required packages installed is required, for the tests only (this is more detailed in the Testing section further down). 

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

## Testing
Should have a docker container for the tests (it's in the next steps). For now a `testing_requirements.txt` file was created for a venv creation.
To test make sure you have virtualenv installed and run `virtualenv venv`. Source the venv with `source venv/bin/activate` and install the requirements with `pip install -r requirements.txt`.
Then, execute `pytest` within the tests folder.

## Next steps
- Create docker container for tests
- Add a Logger to report information
- Add the airflow config code in an equivalent to a `__init__.py` file for a standard python project
- Add mongodb db and collection configuration in a config file
- Add more tests
- Separate to be tested functions from DAG file
- Add error handling for lack of keys
- Add mongo secrets for docker
- Change airflow username and password for a real configuration
- Add CICD with tests whenever a pull request is made

