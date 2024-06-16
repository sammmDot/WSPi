import network
from time import sleep

def ConnectNetwork(SSID, PASSWORD):
    timeout = 15
    timeout_connect = 0
    
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(SSID, PASSWORD)

    while not station.isconnected():
        print('Conectando...')
        sleep(1)
        timeout_connect += 1

        if timeout_connect >= timeout:
            print(f"No se pudo conectar a {SSID}")
            raise Exception(f"No se pudo conectar a {SSID}")

    print(f'Conexión exitosa a {SSID}')