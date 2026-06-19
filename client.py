import network
import time
import dht
import json
from machine import Pin, ADC
from umqtt.simple import MQTTClient

SSID = "porprivacidadheborradoesto"
PASSWORD = "porprivacidadheborradoesto" 

MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = b"smartplant/IDC/data"

DRY_VALUE = 45000
WET_VALUE = 20000

dht_sensor = dht.DHT22(Pin(16))
soil_sensor = ADC(26)

def soil_percent(raw):
    percent = (DRY_VALUE - raw) * 100 / (DRY_VALUE - WET_VALUE)
    percent = max(0, min(100, percent))
    return round(percent, 1)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting WiFi...")
    time.sleep(1)

print("WiFi connected:", wlan.ifconfig()[0])

client = MQTTClient(
    "pico_smartplant_IDC_111",
    MQTT_BROKER
)

client.connect()
print("MQTT connected")

while True:
    try:
        dht_sensor.measure()

        temp = round(dht_sensor.temperature(), 1)
        humidity = round(dht_sensor.humidity(), 1)

        raw = soil_sensor.read_u16()
        moisture = soil_percent(raw)

        payload = {
            "temperature": temp,
            "humidity": humidity,
            "soil": moisture
        }

        message = json.dumps(payload)

        client.publish(MQTT_TOPIC, message)

        print("Published:", message)

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)