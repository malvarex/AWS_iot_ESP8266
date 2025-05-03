import serial
import ssl
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuración del puerto serial
ser = serial.Serial('COM6', 115200, timeout=10) 

# Configuración MQTT
ENDPOINT = "arr1y1mp4w4n2-ats.iot.us-east-2.amazonaws.com"
PORT = 8883
TOPIC = "iot/data"
CA_PATH = "certificados/AmazonRootCA1.pem"
CERT_PATH = "certificados/66266cd0365382110760d21328006f987aa258bf11caf68bbc6a14da7e705a63-certificate.pem.crt"
KEY_PATH = "certificados/66266cd0365382110760d21328006f987aa258bf11caf68bbc6a14da7e705a63-private.pem.key"

client = mqtt.Client()
client.tls_set(ca_certs=CA_PATH,
               certfile=CERT_PATH,
               keyfile=KEY_PATH,
               tls_version=ssl.PROTOCOL_TLSv1_2)

def on_connect(client, userdata, flags, rc):
    print("Conectado con código:", rc)

client.on_connect = on_connect
client.connect(ENDPOINT, PORT)
client.loop_start()

# Leer datos del puerto y publicarlos
while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if "Temperatura" in line:
            parts = line.split()
            temperature = float(parts[1])
            humidity = float(parts[-2])

            payload = {
                "device_id": "0001",
                "temperature": temperature,
                "humidity": humidity,
                "valve_state": "on",
                "date": datetime.now().isoformat()
            }

            client.publish(TOPIC, json.dumps(payload), qos=1)
            print("Enviado:", payload)
    except Exception as e:
        print("Error:", e)
    time.sleep(10)