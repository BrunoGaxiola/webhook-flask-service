from flask import Flask, request
from dotenv import load_dotenv
from messages import sendWebhooks, send_whatsapp_message, send_cita_confirmada, send_cita_cancelada, send_reagendar_cita
from connect import connectToDB
import os

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
connection = connectToDB(SERVER_DRIVER, SERVER_URL, SERVER_DATABASE, SERVER_USER, SERVER_PASSWORD)

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
        sendWebhooks(body, INTEGGRA_WEBHOOKS_ENDPOINT)
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
                    send_whatsapp_message(sender, "Por favor, elige una de las opciones enviadas previamente.")

                # Respuestas por medio de los botones de respuesta.
                elif msg_type == "button":
                    button_payload = msg["button"]["payload"]
                    button_text = msg["button"]["text"]

                    print(f"User pressed button: {button_text} | Payload: {button_payload}")

                    # Dependiendo del payload del botón presionado por el usuario, 
                    # se sigue el flujo de mensajería.
                    if button_payload == "Si, confirmo la cita.":
                        send_cita_confirmada(sender)
                    elif button_payload == "No, cancelo la cita.":
                        send_cita_cancelada(sender)
                    elif button_payload == "Deseo reagendar.":
                        send_reagendar_cita(sender)
                    else:
                        send_whatsapp_message(sender, "Esa respuesta no es válida. Seleccione una opción válida.")
        except Exception as e:
            print("Error handling webhook:", e)

        return "EVENT_RECEIVED", 200

# Programa principal.
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
