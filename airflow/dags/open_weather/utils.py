
import json, urllib.request


def download_weather_data(**kwargs):
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
