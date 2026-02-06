import requests
"""
This is a file of Python functions to send webhooks and send WhatsApp messages.
The environment variables needed are located in the app.py file.
"""

# Función para enviar los webhooks al endpoint InteGGra.
def sendWebhooks(body, url):
    headers = {"Content-Type": "application/json"}
    data = body
    try:
        response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
        print("Webhook successfully sent to endpoint:", response.json())
    except Exception as e:
        print("Error while sending webhook to endpoint,", e)

# Enviar mensaje de texto de WhatsApp.
def send_whatsapp_message(to, message, phoneNumberID, accessToken):
    url = f"https://graph.facebook.com/v22.0/{phoneNumberID}/messages"
    headers = {
        "Authorization": f"Bearer {accessToken}",
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

# Enviar la primera plantilla cita_taller_buena.
def send_confirmacion_cita_taller(to, phoneNumberID, accessToken):
    url = f"https://graph.facebook.com/v22.0/{phoneNumberID}/messages"
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",    
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "confirmacion_cita_taller",
            "language": {"code": "es_MX"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "parameter_name": "nombrecliente",
                            "text": "Fredi Gaxiola Gutierrez"
                        },
                        {
                            "type": "text",
                            "parameter_name": "nomsucemp",
                            "text": "Econollantas Quiroga"
                        },
                        {
                            "type": "text",
                            "parameter_name": "fechacita",
                            "text": "miércoles 26 de noviembre"
                        },
                        {
                            "type": "text",
                            "parameter_name": "horacita",
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

# Enviar mensaje de plantilla cita_confirmada.
def send_cita_confirmada(to, phoneNumberID, accessToken):
    url = f"https://graph.facebook.com/v22.0/{phoneNumberID}/messages"
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "cita_confirmada",
            "language": {"code": "es_MX"},
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar mensaje de plantilla cita_cancelada.
def send_cita_cancelada(to, phoneNumberID, accessToken):
    url = f"https://graph.facebook.com/v22.0/{phoneNumberID}/messages"
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "cita_cancelada",
            "language": {"code": "es_MX"},
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

# Enviar mensaje de plantilla reagendar_cita.
def send_reagendar_cita(to, phoneNumberID, accessToken):
    url = f"https://graph.facebook.com/v22.0/{phoneNumberID}/messages"
    headers = {
        "Authorization": f"Bearer {accessToken}",
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
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "parameter_name": "telefono",
                            "text": "6621228925"
                        },
                    ]
                }
            ]
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()