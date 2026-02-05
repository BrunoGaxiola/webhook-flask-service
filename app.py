from flask import Flask, request
from dotenv import load_dotenv
from messages import send_whatsapp_message, send_cita_confirmada, send_cita_cancelada, send_reagendar_cita
from connect import connectToDB
import os
import requests

# Cargar variables de entorno.
load_dotenv()
# Inicializar aplicación de Flask.
app = Flask(__name__)

# Variables de entorno.
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
SERVER_DRIVER = os.getenv("DRIVER")
SERVER_URL = os.getenv("SERVER")
SERVER_DATABASE = os.getenv("DATABASE")
SERVER_USER = os.getenv("USER")
SERVER_PASSWORD = os.getenv("PASSWORD")
INTEGGRA_WEBHOOKS_ENDPOINT = os.getenv("INTEGGRA_WEBHOOKS_ENDPOINT")

# Establecer conexión con la base de datos, asignar a una variable para contruir un cursor.
connection = connectToDB(SERVER_URL, SERVER_USER, SERVER_PASSWORD, SERVER_DATABASE)

# Función para enviar los webhooks al endpoint InteGGra.
def sendWebhooks(body, url):
    headers = {"Content-Type": "application/json"}
    data = body
    try:
        response = requests.post(url, json=data, headers=headers, verify=False)
        print("Webhook successfully sent to endpoint:", response.json())
    except Exception as e:
        print("Error while sending webhook to endpoint,", e)

# Ruta principal del servicio web.
@app.route("/", methods=["GET", "POST", "HEAD"])
def webhook():

    # Request de HEAD para checar estado activo del servicio.
    if request.method == "HEAD":
        return "", 200

    # Request GET para verificar el enlace entre Meta y el servicio.
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid token", 403
    
    # Request POST para leer los webhooks entrantes.
    if request.method == "POST":
        body = request.get_json()
        print("Webhook received:")
        print(request) # Borrar esto lol.
        print(body)

        # Extraer display_phone_number del webhook
        display_phone_number = None
        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            
            # Obtener el display_phone_number del metadata
            if "metadata" in value and "display_phone_number" in value["metadata"]:
                display_phone_number = value["metadata"]["display_phone_number"]
                print(f"Display phone number found: {display_phone_number}")
        except Exception as e:
            print(f"Error extracting display_phone_number: {e}")
        
        # Buscar el EndPoint en la base de datos usando el display_phone_number
        endpoint_to_use = INTEGGRA_WEBHOOKS_ENDPOINT  # Valor por defecto
        
        if display_phone_number and connection:
            try:
                # Crear un cursor para ejecutar consultas
                cursor = connection.cursor()
                
                # Buscar el registro con el display_phone_number
                # Asumo que hay una tabla con una columna para el número de teléfono
                # Ajusta el nombre de la tabla y columnas según tu esquema
                query = "SELECT EndPoint FROM EndPoints WHERE Tel_WAB = %s"
                cursor.execute(query, (display_phone_number,))
                
                result = cursor.fetchone()
                if result:
                    endpoint_to_use = result[0]
                    print(f"EndPoint found in DB: ", endpoint_to_use)
                else:
                    print(f"No record found for phone number.")
                
                cursor.close()
            except Exception as e:
                print(f"Error querying database: {e}")
        
        # Usar el endpoint encontrado o el por defecto.
        sendWebhooks(body, endpoint_to_use)
        print("\n") # Leer mejor cada webhook.

        # Por cada Webhook entrante recopila datos como el sender y el contenido del mensaje
        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages")

            if messages:
                msg = messages[0]
                sender = msg["from"]

                msg_type = msg["type"]

                # Respuesta en caso de que el cliente responda con un mensaje de texto.
                if msg_type == "text":
                    user_text = msg["text"]["body"]
                    print(f"User wrote: {user_text}")
                    send_whatsapp_message(sender, "Por favor, elige una de las opciones enviadas previamente.", PHONE_NUMBER_ID, ACCESS_TOKEN)

                # Respuestas por medio de los botones de respuesta.
                elif msg_type == "button":
                    button_payload = msg["button"]["payload"]
                    button_text = msg["button"]["text"]

                    print(f"User pressed button: {button_text} | Payload: {button_payload}")

                    # Dependiendo del payload del botón presionado por el usuario, 
                    # se sigue el flujo de mensajería.
                    if button_payload == "Si, confirmo la cita.":
                        send_cita_confirmada(sender, PHONE_NUMBER_ID, ACCESS_TOKEN)
                    elif button_payload == "No, cancelo la cita.":
                        send_cita_cancelada(sender, PHONE_NUMBER_ID, ACCESS_TOKEN)
                    elif button_payload == "Deseo reagendar.":
                        send_reagendar_cita(sender, PHONE_NUMBER_ID, ACCESS_TOKEN)
                    else:
                        send_whatsapp_message(sender, "Esa respuesta no es válida. Seleccione una opción válida.", PHONE_NUMBER_ID, ACCESS_TOKEN)
        except Exception as e:
            print("Error handling webhook:", e)

        return "EVENT_RECEIVED", 200

# Programa principal.
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
