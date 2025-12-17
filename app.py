from flask import Flask, request
from dotenv import load_dotenv
import requests
import os

# Cargar variables de entorno.
load_dotenv()
# Inicializar aplicación de Flask.
app = Flask(__name__)

# Variables de entorno.
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Enviar mensaje de texto de WhatsApp.
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": { "body": message }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar el primer mensaje de cita.
def send_cita_taller(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",    
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "cita_taller",
            "language": {"code": "es_MX"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "parameter_name": "nombre_apellido",
                            "text": "Fredi Gaxiola"
                        },
                        {
                            "type": "text",
                            "parameter_name": "taller",
                            "text": "Yokohama Colosio"
                        },
                        {
                            "type": "text",
                            "parameter_name": "fecha",
                            "text": "miércoles 26 de noviembre"
                        },
                        {
                            "type": "text",
                            "parameter_name": "hora",
                            "text": "17:00"
                        }
                    ]
                }
            ]
        }
    }
    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar mensaje de confirmación de elección.
def send_confirmation_message(to, payload):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "opcion_seleccionada",
            "language": {"code": "es_MX"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                           "type": "text",
                           "parameter_name": "opcion_seleccionada",
                           "text": f"{payload}" 
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar mensaje de plantilla cancelar_reagendar_cita.
def send_cancelar_reagendar_cita(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "cancelar_reagendar_cita",
            "language": {"code": "es_MX"},
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar mensaje de plantilla reagendar_cita.
def send_reagendar_cita(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "reagendar_cita",
            "language": {"code": "es_MX"},
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()
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
        print(request.headers) # Borrar esto también lol.
        print(body)

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
                        send_whatsapp_message(sender, "Perfecto, su cita ha sido confirmada. Nos vemos pronto.")
                    elif button_payload == "No, cancelo la cita.":
                        send_cancelar_reagendar_cita(sender)
                    elif button_payload == "Cancelar cita.":
                        send_whatsapp_message(sender, "Su cita ha sido cancelada. Que tenga un excelente día.")
                    elif button_payload == "Reagendar cita.":
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
