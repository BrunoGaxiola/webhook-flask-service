import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# Declarar variables de entorno.
SERVER_DRIVER = os.getenv("DRIVER")
SERVER_URL = os.getenv("SERVER")
SERVER_DATABASE = os.getenv("DATABASE")
SERVER_USER = os.getenv("USER")
SERVER_PASSWORD = os.getenv("PASSWORD")

try:
    connection = pyodbc.connect(f"DRIVER={SERVER_DRIVER};SERVER={SERVER_URL};DATABASE={SERVER_DATABASE};UID={SERVER_USER};PWD={SERVER_PASSWORD}")
    print("Se ha conectado con la base de datos con éxito.")
    connection.close()
except Exception as e:
    print("Hubo error conectándose con la base de datos.", e)