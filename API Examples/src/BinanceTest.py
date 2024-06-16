import urequests as requests
import time
from env import URL_BASE

def TestConnectivity():
    ENDPOINT = '/api/v3/ping'
    print('Probando la conexión con la API Rest')
    response = requests.get(URL_BASE + ENDPOINT)
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data == {}:
                print('Conexión exitosa, código 200')
            else:
                print('La respuesta no es la esperada: ', data)
        except ValueError:
            print('No se pudo parsear la respuesta como JSON')
    else:
        print(f'Error en la conexión: {response.status_code}')
    response.close()