import network  # Para gestionar la conexión a la red
import gc       # Para recolección de basura
import urequests as requests   # Para realizar solicitudes HTTP
import json                    # Manipular archivos Json
from time import sleep         # Manejar tiempos


# Limpiar la memoria
gc.collect()

SSID = 'VTR-8135116'            # Nombre de la red WiFi
PASSWORD = 'y8yfQcpvgbmf'    # Contraseña de la red WiFi

# URL de la API que estás utilizando
URL_BASE = "https://api.coingecko.com/api/v3"

# Tu clave API
API_KEY = "CG-jRDMyKai9Nnq6kBp9khhgSrd"


def connectWifi(ssid, password, timeout=15):

    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    timeout_connect = 0

    while not station.isconnected():
        print('conectando')

        sleep(1)
        timeout_connect += 1

        if timeout_connect >= timeout:

            raise Exception(f"No se pudo conectar a {ssid}")

    print(f'Conexión exitosa a {ssid}')


def fetch_api_simple_price(url_base: str, api_key: str, coin_info_list: dict, timeout=15):

    # Encabezados de la solicitud con la clave API
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + api_key
               }

    # URL base para este tipo de splicitud
    url = url_base + "/simple/price?ids="

    # Agregaa las monedas a consultar
    for index, coin in enumerate(coin_info_list['coins']):
        if index == 0:
            url += coin.lower()
        else:
            url += f'%2C{coin.lower()}'

    # Incluye la comparación (Por el momento solo admite una comparación)
    url += f'&vs_currencies={coin_info_list["coin_vs"].lower()}'

    parameters = coin_info_list.items()

    for key, value in parameters:
        if isinstance(value, bool):
            if value:
                url += f'&{key}={str(value).lower()}'

    try:
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Error en la solicitud. Código de respuesta HTTP:',
                  response.status_code)
            return None

    except Exception as e:
        print('Error en la solicitud:', str(e))
        return None


coin_info = {"coins": ["bitcoin", "ethereum","cardano"],
             "coin_vs": "usd",
             "include_market_cap": False,
             "include_24hr_change": True,
             "include_24hr_vol": False,
             }

# Conectar a la red WiFi
connectWifi(SSID, PASSWORD)

data = fetch_api_simple_price(URL_BASE, API_KEY, coin_info)

# Imprimir la respuesta
print(data)
