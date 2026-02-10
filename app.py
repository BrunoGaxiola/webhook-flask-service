from flask import Flask, request
from dotenv import load_dotenv
from messages import sendWebhooks, send_whatsapp_message, send_cita_confirmada, send_cita_cancelada, send_reagendar_cita
from connect import connectToDB
import os
from urllib3 import disable_warnings

# Cargar variables de entorno.
load_dotenv()
# Inicializar aplicación de Flask.
app = Flask(__name__)
# Ignorar advertencias.
disable_warnings()

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

# Función para consultar endpoint en BD
def get_endpoint_from_database(phone_number):
    try:
        cursor = connection.cursor()
        query = "SELECT EndPoint FROM EndPoints WHERE Tel_WAB = %s"
        cursor.execute(query, (phone_number,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error BD para {phone_number}: {e}")
        return None

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
        # Imprime todos los Webhooks en consola.
        body = request.get_json()
        print("Webhook recibido:", body)
        print('\n')

        # Analiza cada webhook entrante accediendo a sus propiedades.
        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages")
            # Obtiene el ID del número emisor para seguir consumiendo la API.
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            # SOLO PROCESA Y ENVÍA WEBHOOKS SI HAY MENSAJES (evita webhooks de estado)
            if messages:
                msg = messages[0]
                sender = msg["from"]
                msg_type = msg["type"]

                # ENVÍO DE WEBHOOKS A ENDPOINT PARA MENSAJES DE TEXTO Y BOTÓN
                try:
                    metadata = value.get("metadata", {})
                    display_phone_number = metadata.get("display_phone_number")
                    
                    if display_phone_number:
                        endpoint_url = get_endpoint_from_database(display_phone_number)
                        if endpoint_url:
                            endpoint_url = endpoint_url.rstrip()
                            sendWebhooks(body, endpoint_url) # El Webhook es enviado a su EndPoint.
                            print(f"Webhook de {msg_type} enviado a endpoint para {display_phone_number}")
                        else:
                            print(f"No se consiguió endpoint en BD para este número emisor: {display_phone_number}")
                    else:
                        print(f"No se encontró un 'display_phone_number' en el webhook.")
                except Exception as e:
                    print(f"Error procesando webhook de {msg_type}: {e}")

                # Si el mensaje es de tipo texto, se le pide responder con alguna de las opciones anteriores.
                if msg_type == "text":
                    user_text = msg["text"]["body"]
                    print(f"Texto recibido: {user_text}")
                    send_whatsapp_message(sender, "Por favor, elige una de las opciones enviadas previamente.", phone_number_id, ACCESS_TOKEN)

                # El usuario ha contestado el mensaje con los botones de la plantilla.
                elif msg_type == "button":
                    button_payload = msg["button"]["payload"]
                    button_text = msg["button"]["text"]
                    print(f"Botón presionado: {button_text}") # Imprime la respuesta del usuario.

                    # Dependiendo de la respuesta del usuario, se envía su siguiente plantilla.
                    if button_payload == "Si, confirmo la cita.":
                        send_cita_confirmada(sender, phone_number_id, ACCESS_TOKEN)
                    elif button_payload == "No, cancelo la cita.":
                        send_cita_cancelada(sender, phone_number_id, ACCESS_TOKEN)
                    elif button_payload == "Deseo reagendar.":
                        send_reagendar_cita(sender, phone_number_id, ACCESS_TOKEN)
                    else:
                        send_whatsapp_message(sender, "Respuesta no válida.", phone_number_id, ACCESS_TOKEN)
            else:
                # Este es un webhook de estado (enviado, recibido, leído) - solo se imprime, no se procesa
                print("Webhook de estado recibido - no se procesa ni envía a endpoint")
                
        except Exception as e:
            print("Error en flujo de WhatsApp:", e)

        return "EVENT_RECEIVED", 200
    
# Programa principal.
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
