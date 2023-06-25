import sqlite3
import random
import requests
from bs4 import BeautifulSoup

class SensorsValues:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_ext_values(self): #Funkcija kojom se dohvaćaju vrijednosti za temperaturu i vlažnost zraka sa interneta
        url = "https://weather.com/hr-HR/vrijeme/satu/l/Zagreb+Zagreb?canonicalCityId=c4db47e558cfc06fb93968a6fcaeecb092e3ae2da0de71ec1824681d0e22a51d"

        response = requests.get(url)
        content = response.content

        soup = BeautifulSoup(content, "html.parser")
        temperature_value = soup.find("span", {"data-testid": "TemperatureValue", "class": "DetailsSummary--tempValue--jEiXE"}).text
        humidity_value = soup.find("span", {"data-testid": "PercentageValue", "class" : "DetailsTable--value--2YD0-" }).text

        temperature_value = ''.join(filter(str.isdigit, temperature_value))
        humidity_value = ''.join(filter(str.isdigit, humidity_value))

        return int(temperature_value), int(humidity_value)


    def get_ideal_values(self, plant_id): #Funkcija da dobivanje vrijednosti pohranjenih u tabeli o biljkama na osnovu id-a odabrane bijke
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT light, substrate, temperature, humidity, path FROM plant_table WHERE plant_id=?", (plant_id,))
            result = c.fetchone()
            conn.close()
            if result is None:
                return None, None, None, None, None  
            else:
                light, substrate, temperature, humidity, path = result
                return light, substrate, temperature, humidity, path
        except Exception as e:
            print("Error in get_ideal_values: ", e)
            return None, None, None, None, None  


    def get_sensor_values(self):
        # Simulator senzora
        sensor_light = random.randint(0, 100)
        sensor_substrate = random.randint(0, 100)
        
        return sensor_light, sensor_substrate


    def generate_actions(self, plant_id):
        #Generira se akcija uskoredbom eksternih i simuliranih vrijednosti senzora sa idealnim vrijednostima koje su pohranjene o biljci
        ext_temperature, ext_humidity = self.get_ext_values()
        ideal_light, ideal_substrate, ideal_temperature, ideal_humidity, _ = self.get_ideal_values(plant_id)
        sensor_light, sensor_substrate = self.get_sensor_values()

        #print(f"plant_id: {plant_id}, ideal values: {ideal_light, ideal_substrate, ideal_temperature, ideal_humidity}")

        actions = {}

        if sensor_light < ideal_light:
            actions["light"] = (sensor_light, "Turn on light")
        elif sensor_light > ideal_light:
            actions["light"] = (sensor_light, "Turn off light")

        if sensor_substrate < ideal_substrate:
            actions["substrate"] = (sensor_substrate, "Water plant")
        elif sensor_substrate > ideal_substrate:
            actions["substrate"] = (sensor_substrate, "Drain water")

        if ext_temperature < ideal_temperature:
            actions["temperature"] = (ext_temperature, "Increase room temperature")
        elif ext_temperature > ideal_temperature:
            actions["temperature"] = (ext_temperature, "Decrease room temperature")

        if ext_humidity < ideal_humidity:
            actions["humidity"] = (ext_humidity, "Increase room humidity")
        elif ext_humidity > ideal_humidity:
            actions["humidity"] = (ext_humidity, "Decrease room humidity")

        return actions

