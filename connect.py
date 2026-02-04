import pyodbc

def connectToDB(driver, url, database, user, password):
    try:
        connection = pyodbc.connect(f"DRIVER={driver};SERVER={url};DATABASE={database};UID={user};PWD={password}")
        print("Se ha conectado con la base de datos con éxito.")
        return connection
    except Exception as e:
        print("Hubo error conectándose con la base de datos.", e)
        return None