import omni
import urllib3
import json

from enum import IntEnum

# Sun Study!
from omni.kit.environment.core.sunstudy_player.player import SunstudyPlayer

from .manipulationsuite import ManipulationSuite

# Enumerator defining the different weather profiles
class WeatherOptions(IntEnum):
    TEST = 0
    SUN = 1
    RAIN = 2
    SNOW = 3
    STORM = 4


class WeatherSuite:
    """
    All Weather Effect capabilities that can be used within a scene.
    """

    _weather_dict = {}
    _weather_desc = ""
    _weather_effect = None
    _effect_path = ""

    def __init__(self, path="omnitools/Weather/", lat=None, lon=None):
        print("Initialized Weather Suite.")
        self._effect_path = str(path)
        self.lat = lat
        self.lon = lon

        # Explicitly state weather bindings
        # TODO: Can we define these better?
        self._weather_dict[WeatherOptions.TEST] = self._effect_path + "test.usd"
        self._weather_dict[WeatherOptions.SUN] = None
        self._weather_dict[WeatherOptions.RAIN] = self._effect_path + "rain.usd"
        self._weather_dict[WeatherOptions.SNOW] = self._effect_path + "snow.usd"
        self._weather_dict[WeatherOptions.STORM] = self._effect_path + "thunder.usd"

        # SunStudy variables
        SunstudyPlayer().latitude = lat
        SunstudyPlayer().longitude = lon

        self.manip = ManipulationSuite()

    # Retrieve current weather effect
    def get_weather_effect_path(self):
        return self._weather_dict[self._weather_effect]

    def get_weather_effect(self):
        return self._weather_effect

    # Assign current weather effect
    def set_weather_effect(self, value):
        self._weather_effect = value

    # Fetch data from an API, with key, lat, and lon values
    def fetch_from_api(self, api_key, lat, lon):
        # Make URL request with URLLib3
        url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (
            lat,
            lon,
            api_key,
        )

        http = urllib3.PoolManager()
        response = http.request("GET", url)

        # Decode data into JSON format
        data = json.loads(response.data.decode("utf-8"))

        # Get description of current weather; needed to show real-time
        weather_desc = data["current"]["weather"][0]["description"]

        print("Current Weather: " + str(weather_desc))

        if weather_desc is not None:
            return weather_desc
        else:
            print("Could not fetch weather data! Please check that your configuration is correct.")
            raise

    def configure_weather(
        self,
        stage=None,
        prefix="/Weather/Effect",
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        weather_desc=None,
        test_mode=False,
    ):
        # Put effect in non-caps as a safety precaution
        weather_desc = weather_desc.lower()
        weather = None

        print(weather_desc)

        if test_mode:
            weather = self.test_weather(stage, position, rotation)
        else:
            if "sun" in weather_desc or "cloud" in weather_desc:
                if self.get_weather_effect() != WeatherOptions.SUN:
                    self.set_weather_effect(WeatherOptions.SUN)
                    self.clear_weather(weather)
                    weather = self.sunny_weather(stage, prefix, position, rotation, cloud_type="cumulus")

            elif "rain" in weather_desc or "drizzle" in weather_desc:
                if self.get_weather_effect() != WeatherOptions.RAIN:
                    self.set_weather_effect(WeatherOptions.RAIN)
                    self.clear_weather(weather)
                    weather = self.rainy_weather(stage, prefix, position, rotation, rain_intensity=0.1)

            elif "snow" in weather_desc or "sleet" in weather_desc:
                if self.get_weather_effect() != WeatherOptions.SNOW:
                    self.set_weather_effect(WeatherOptions.SNOW)
                    self.clear_weather(weather)
                    weather = self.snowy_weather(stage, prefix, position, rotation, snow_intensity=0.1)

            elif "thunder" in weather_desc in weather_desc:
                if self.get_weather_effect() != WeatherOptions.STORM:
                    self.set_weather_effect(WeatherOptions.STORM)
                    self.clear_weather(weather)
                    weather = self.storm_weather(stage, prefix, position, rotation, storm_intensity=0.1)

        return weather

    def clear_weather(self, stage=None, weather_effects=[]):
        if len(weather_effects) > 0:
            for effect in weather_effects:
                self.manip.delete_object(stage, effect)

    def get_available_effects(self):
        # Return everything except the 'TEST' Option
        return [member.name.lower().capitalize() for member in WeatherOptions]

    ##############################
    # WEATHER PROFILES & CONFIGS #
    ##############################

    def test_weather(
        self, stage, prefix, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), test_effect=WeatherOptions.RAIN
    ):
        self.set_weather_effect(test_effect)

        effect_layer1 = self.manip.create_object(
            stage,
            prefix=prefix,
            path=self.get_weather_effect_path(),
            position=position,
            rotation=rotation,
        )

        weather = [effect_layer1]

        return weather

    def sunny_weather(self, stage, prefix, position, rotation, cloud_type="cumulus"):
        # TODO: Cloud behaviour?
        print("Activating Sunny Weather!")

    def rainy_weather(self, stage, prefix, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), rain_intensity=0.1):
        # TODO: IMPLEMENT MORE RAIN BEHAVIOUR
        effect_layer1 = self.manip.create_object(
            stage,
            prefix=prefix,
            path=self.get_weather_effect_path(),
            position=position,
            rotation=rotation,
        )

        weather = [effect_layer1]

        print("Activating Rainy Weather!")

        return weather

    def snowy_weather(self, stage, prefix, position, rotation, snow_intensity=0.1):
        # TODO: IMPLEMENT MORE SNOW BEHAVIOUR

        effect_layer1 = self.manip.create_object(
            stage,
            prefix=prefix,
            path=self.get_weather_effect_path(),
            position=position,
            rotation=rotation,
        )

        weather = [effect_layer1]

        print("Activating Snowy Weather!")

        return weather

    def storm_weather(self, stage, prefix, position, rotation, storm_intensity=0.1):
        # TODO: IMPLEMENT FULL THUNDER BEHAVIOUR
        print("Activating Stormy Weather!")

    #################
    # SUN BEHAVIOUR #
    #################

    def configure_time_of_day(self, new_hr):
        # Note: new_hr must be between 0 and 23

        # Configure sun study with new times
        SunstudyPlayer().start_time = new_hr
        SunstudyPlayer().end_time = new_hr

        # Start/Stop to register new time
        SunstudyPlayer().start()
        SunstudyPlayer().stop()

    def configure_lat(self, lat_val):
        SunstudyPlayer().latitude = lat_val

    def configure_lon(self, lon_val):
        SunstudyPlayer().longitude = lon_val

    #######################
    # PUT IT ALL TOGETHER #
    #######################
    def get_weather(
        self,
        stage=None,
        prefix=None,
        position=(),
        rotation=(),
        use_api=True,
        api_key=None,
        weather_desc=None,
        test_mode=False,
    ):
        # Initial checks
        if use_api and (api_key is None):
            print("API Key Error! Cannot set weather via API without a valid API Key.")
            raise
        elif (use_api and self.lat is None) or (use_api and self.lon is None):
            print("LATITUDE or LONGITUDE parameters are missing! Cannot set weather via API without these parameters.")
            raise
        elif (not use_api) and (weather_desc is None):
            print("Cannot fetch any weather attributes without at least a description or a valid API configuration.")
            raise

        # Identify processing means
        if use_api:
            weather_desc = self.fetch_from_api(api_key, self.lat, self.lon)
            weather_effect = self.configure_weather(stage, prefix, position, rotation, weather_desc, test_mode)

        elif weather_desc is not None:
            # TODO: INTEGRATE OTHER WEATHER FETCHERS (e.g. MDX)
            print("MDX Support coming soon!")

        else:
            print("Please define a data retrieval schema in your weather class definition.")
            raise

        return weather_effect
