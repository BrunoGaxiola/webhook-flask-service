import pymssql

def connectToDB(url, user, password, database):
    try:
        connection = pymssql.connect(server=url, user=user, password=password, database=database)
        print("Se ha conectado con la base de datos con éxito.")
        return connection
    except Exception as e:
        print("Hubo error conectándose con la base de datos.", e)
        return None