 import paho.mqtt.client as mqtt
import ssl
import time
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# 📌 Certificados
CA_PATH = "certificados/AmazonRootCA1.pem"
CERT_PATH = "certificados/device-certificate.pem.crt"
KEY_PATH = "certificados/device-private.pem.key"

# 📌 AWS IoT & DynamoDB
ENDPOINT = "aqxgrnd15rd74-ats.iot.us-east-2.amazonaws.com"
TOPIC = "iot/data"
TABLE_NAME = "iot_network"

# 🧪 Mensaje simulado
payload = {
    "device_id": "0001",
    "temperature": 24,
    "humidity": 50,
    "valve_state": "on",
    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
}

# 🛡️ Validación y sanitización del payload
def is_valid_payload(data):
    try:
        # Campos requeridos
        required_fields = ["device_id", "temperature", "humidity", "valve_state", "date"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Faltante el campo: {field}")
                return False

        # Tipos y formatos
        if not isinstance(data["device_id"], str) or not data["device_id"].isdigit():
            return False
        if not isinstance(data["temperature"], (int, float)):
            return False
        if not isinstance(data["humidity"], (int, float)):
            return False
        if data["valve_state"] not in ["on", "off"]:
            return False

        # Sanitización básica (no se permite código malicioso)
        for value in data.values():
            if isinstance(value, str) and any(c in value for c in [';', '$', '{', '}']):
                print("⚠️ Valor potencialmente malicioso detectado")
                return False

        return True

    except Exception as e:
        print("❌ Error en validación:", e)
        return False

# 🚀 Publicación si el payload es válido
if is_valid_payload(payload):
    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=payload)
        print("🗃️ Insertado en DynamoDB correctamente.")
    except ClientError as e:
        print("⚠️ Error al insertar en DynamoDB:", e)
else:
    print("🚫 Payload inválido. No se envía.")

# --- MQTT: Configuración y callbacks ---
def on_connect(client, userdata, flags, rc):
    print("🔎 Código de conexión:", rc)
    if rc == 0:
        print("✅ Conectado a AWS IoT con éxito")
        if is_valid_payload(payload):
            client.publish(TOPIC, json.dumps(payload), qos=1)
            print("📨 Mensaje publicado al tópico:", TOPIC)
        else:
            print("🚫 Payload inválido. No se publica.")
    else:
        print("❌ Error al conectar:", rc)

def on_publish(client, userdata, mid):
    print("✅ Mensaje publicado exitosamente")

# --- MQTT Client ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(
    ca_certs=CA_PATH,
    certfile=CERT_PATH,
    keyfile=KEY_PATH,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

print("Conectando a AWS IoT...")
client.connect(ENDPOINT, port=8883)
client.loop_start()
time.sleep(4)
client.loop_stop()