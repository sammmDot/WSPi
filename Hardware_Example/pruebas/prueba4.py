import machine
import ssd1306
import utime
import framebuf
import network
import _thread
import socket
import time
import struct
import urequests as requests
import json
from imagen_bitcoin import logo

buffer = bytearray(logo)
ANCHO = 128
ALTO = 64
fb = framebuf.FrameBuffer(buffer, ANCHO, ALTO, framebuf.MONO_HLSB)

print("Inicializando I2C")
i2c = machine.I2C(1, scl=machine.Pin(19), sda=machine.Pin(18))

print("Inicializando pantalla OLED")
oled = ssd1306.SSD1306_I2C(ANCHO, ALTO, i2c)
oled.fill(1)
oled.show()
utime.sleep(1)
oled.fill(0)
oled.show()

button_pin_1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_2 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_3 = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_4 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)

SCREEN_OFF = 0
SCREEN_ON_1 = 1
SCREEN_ON_2 = 2
SCREEN_ON_3 = 3

current_screen = SCREEN_OFF
last_button_state_1 = 0
last_button_state_2 = 0
last_button_state_3 = 0
last_button_state_4 = 0

ssid = 'VTR-8135116'
password = 'y8yfQcpvgbmf'

URL_BASE = "https://api.coingecko.com/api/v3"
API_KEY = "CG-jRDMyKai9Nnq6kBp9khhgSrd"

coin_info = {"coins": ["bitcoin", "ethereum", "cardano"],
             "coin_vs": "usd",
             "include_market_cap": False,
             "include_24hr_change": True,
             "include_24hr_vol": False,
             }

def connectWifi(ssid, password, timeout=15):
    print("Conectando a WiFi")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        utime.sleep(1)
        print("Esperando conexión WiFi...")
    print("Conectado a WiFi: ", wlan.ifconfig())

def fetch_api_simple_price(coin_list, coin_vs, api_key, url_base=URL_BASE, timeout=15):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

    url = url_base + "/simple/price?ids="

    for index, coin in enumerate(coin_list):
        if index == 0:
            url += coin.lower()
        else:
            url += f'%2C{coin.lower()}'

    url += f'&vs_currencies={coin_vs.lower()}'

    parameters = coin_info.items()

    for key, value in parameters:
        if isinstance(value, bool):
            if value:
                url += f'&{key}={str(value).lower()}'

    try:
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Error en la solicitud. Código de respuesta HTTP:', response.status_code)
            return None

    except Exception as e:
        print('Error en la solicitud:', str(e))
        return None

def showInOled(data_coins, coin_search, vs_coin):
    info_coin = data_coins[coin_search]
    icon_data = infoIcon(coin_search)

    valor = info_coin[vs_coin]

    if valor < 100:
        valor = f'{valor:0.2f}'

    change_24h = info_coin[f'{vs_coin}_24h_change']
    change_24h = f'{change_24h:0.2f}'

    def center_coin_name(name_coin, x_icon_pos):
        x = (oled.width + icon_data[0] + x_icon_pos - len(name_coin)*8)//2
        y = (icon_data[1]//2)-6

        name = name_coin.upper()
        oled.text(name, x, y)
        oled.hline(x, y+9, len(name_coin)*8, 1)

    def centerText(text, y):
        x = (oled.width - len(text)*8)//2
        oled.text(text, x, y)

    oled.fill(0)
    oled.blit(icon_data[2], 10, 0)
    center_coin_name(coin_search, 10)

    centerText(f'{valor} {vs_coin}', icon_data[1]+8)
    centerText(f'{change_24h} %', icon_data[1]+20)

    oled.show()

def Icono_WIFI(ruta, x, y):
    print("Cargando icono desde archivo:", ruta)
    doc = open(ruta, "rb")
    doc.readline()
    xy = doc.readline()
    x_size = int(xy.split()[0])
    y_size = int(xy.split()[1])
    icono = bytearray(doc.read())
    doc.close()
    return framebuf.FrameBuffer(icono, x_size, y_size, framebuf.MONO_HLSB)

def obtener_fecha():
    print("Obteniendo fecha y hora actual")
    rtc = machine.RTC()
    tm = rtc.datetime()
    year = tm[0]
    month = tm[1]
    day = tm[2]
    hour = tm[4]
    minute = tm[5]
    second = tm[6] 
    fecha_actual = "{:02}:{:02}      {:02d}/{:02d}".format(hour, minute, day, month)
    oled.fill_rect(0, 0, 128, 8, 0)  
    oled.text(fecha_actual, 0, 0)
    print("Fecha y hora obtenida:", fecha_actual)
    return fecha_actual

def imprimir_pantalla(fecha_actual, texto_linea_1="", texto_linea_2="", texto_linea_3="", texto_linea_4="", mostrar_logo=False):
    print("Imprimiendo pantalla")
    oled.fill(0)
    if mostrar_logo:
        oled.blit(fb, 0, 0)  # Ajusta la posición según sea necesario
    else:
        oled.text(fecha_actual, 0, 0)
        mostrar_icono_wifi()
        oled.text(texto_linea_1, int((ANCHO - len(texto_linea_1) * 8) / 2), int((ALTO - 32) / 2))
        oled.text(texto_linea_2, int((ANCHO - len(texto_linea_2) * 8) / 2), int((ALTO - 32) / 2) + 12)
        oled.text(texto_linea_3, int((ANCHO - len(texto_linea_3) * 8) / 2), int((ALTO - 32) / 2) + 24)
        oled.text(texto_linea_4, int((ANCHO - len(texto_linea_3) * 8) / 2), int((ALTO - 32) / 2) + 36)
    oled.show()

def toggle_screen_state(screen):
    global current_screen
    print("Cambiando estado de la pantalla a:", screen)

    if screen == SCREEN_OFF:
        current_screen = SCREEN_OFF
        oled.poweroff()
        oled.fill(0)
        oled.show()
        
    elif screen == SCREEN_ON_1:
        current_screen = SCREEN_ON_1
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual, "WSPI", "Ingenieria Civil", "Telematica")
        
    elif screen == SCREEN_ON_2:
        current_screen = SCREEN_ON_2
        fecha_actual = obtener_fecha()
        oled.fill(0)
        oled.show()
        icono = Icono_WIFI("bitcoin.pbm", 2, 12)  # Cambiar a nombre correcto del logo de Bitcoin
        oled.invert(0)
        oled.blit(icono, 2, 12)
        mostrar_icono_wifi()
        oled.show()
        utime.sleep(2)  # Pausa para mostrar el logo
        data = fetch_api_simple_price(coin_info["coins"], coin_info["coin_vs"], API_KEY)
        showInOled(data, "bitcoin", coin_info["coin_vs"])
        
    elif screen == SCREEN_ON_3:
        current_screen = SCREEN_ON_3
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual, "PROXIMA CLASE", "IWG101", "PC08")
        
    elif screen == SCREEN_ON_4:
        current_screen = SCREEN_ON_4
        fecha_actual = obtener_fecha()
        icono = Icono_WIFI("soso.pbm", 2, 12)
        oled.fill(0)
        oled.invert(0)
        oled.blit(icono, 2, 12)
        oled.text(fecha_actual, 0, 0)
        mostrar_icono_wifi()
        oled.show()
        
    elif screen == SCREEN_ON_5:
        current_screen = SCREEN_ON_5
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual, "Controles:", "MAT070    26/06", "TEL101    28/06", "FIS100    20/06")
        
    elif screen == SCREEN_ON_6:
        current_screen = SCREEN_ON_6
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual, mostrar_logo=True)    


def fetch_data_and_show(screen):
    data = fetch_api_simple_price(coin_info["coins"], coin_info["coin_vs"], API_KEY)
    if screen == SCREEN_ON_1:
        showInOled(data, "bitcoin", coin_info["coin_vs"])
    elif screen == SCREEN_ON_2:
        showInOled(data, "ethereum", coin_info["coin_vs"])
    elif screen == SCREEN_ON_3:
        showInOled(data, "cardano", coin_info["coin_vs"])

def mostrar_icono_wifi():
    print("Mostrando icono WiFi")
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        icono = Icono_WIFI("sin-senal.pbm", 56, 112)
    else:
        icono = Icono_WIFI("wifii.pbm", 56, 112)
    oled.blit(icono, 56, 0)
    oled.show()

def Main():
    print("Iniciando bucle principal")
    while True:
        global last_button_state_1
        global last_button_state_2
        global last_button_state_3
        
        button_state_1 = button_pin_1.value()

        if button_state_1 != last_button_state_1 and button_state_1 == 1:
            toggle_screen_state(SCREEN_ON_1)

        last_button_state_1 = button_state_1

        button_state_2 = button_pin_2.value()

        if button_state_2 != last_button_state_2 and button_state_2 == 1:
            toggle_screen_state(SCREEN_ON_2)

        last_button_state_2 = button_state_2

        button_state_3 = button_pin_3.value()

        if button_state_3 != last_button_state_3 and button_state_3 == 1:
            toggle_screen_state(SCREEN_ON_3)

        last_button_state_3 = button_state_3

        if current_screen != SCREEN_OFF:
            fecha_actual = obtener_fecha()
            mostrar_icono_wifi()
            oled.show()
        utime.sleep(0.1)


print("Iniciando hilo principal")
_thread.start_new_thread(Main, ())
connectWifi(ssid, password)
