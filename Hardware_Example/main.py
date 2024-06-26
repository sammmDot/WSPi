import network  # Para gestionar la conexión a la red
import gc       # Para recolección de basura
import urequests as requests   # Para realizar solicitudes HTTP
import framebuf                # Para trabajar con imágenes
import json                    # Manipular archivos Json
import ssd1306  # Controla el display oled
import machine    # Configuración de pines y comunicación i2c
from time import sleep           # Manejar tiempos
import utime
import _thread
import socket
import struct

# Limpiar la memoria
gc.collect()

SSID = 'VTR-8135116'            # Nombre de la red WiFi
PASSWORD = 'y8yfQcpvgbmf'    # Contraseña de la red WiFi

# URL de la API que estás utilizando
URL_BASE = "https://api.coingecko.com/api/v3"

# Tu clave API
API_KEY = "CG-jRDMyKai9Nnq6kBp9khhgSrd"

NTP_DELTA = 2208988800 + (3600 * 4)  # GMT-4 Santiago de Chile
host = "pool.ntp.org"
button_pin_1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_2 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_3 = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_pin_4 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)

SCREEN_OFF = 0
SCREEN_ON_1 = 1
SCREEN_ON_2 = 2
SCREEN_ON_3 = 3
SCREEN_ON_4 = 4
SCREEN_ON_5 = 5
SCREEN_ON_6 = 6

current_screen = SCREEN_OFF
last_button_state_1 = 0
last_button_state_2 = 0
last_button_state_3 = 0
last_button_state_4 = 0

coin_info = {"coins": ["bitcoin", "ethereum","cardano"],
             "coin_vs": "usd",
             "include_market_cap": False,
             "include_24hr_change": True,
             "include_24hr_vol": False,
             }

def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA
    tm = time.gmtime(t)
    machine.RTC().datetime(
        (tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    print("Hora configurada: ", machine.RTC().datetime())

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
    return fecha_actual

def imprimir_pantalla(fecha_actual, texto_linea_1="", texto_linea_2="", texto_linea_3="", texto_linea_4="", mostrar_logo=False):
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

def mostrar_icono_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        icono = Icono_WIFI("sin-senal.pbm", 56, 112)
    else:
        icono = Icono_WIFI("wifii.pbm", 56, 112)
    oled.blit(icono, 56, 0)
    oled.show()

    
def connectWifi(oled, ssid, password, timeout=15):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    oled.fill(0)
    oled.show()

    oled.text("Conectando", 10, 0)
    oled.show()
    dot = 10

    timeout_connect = 0

    while not station.isconnected():
        print('conectando')

        oled.text(".", dot, 20)
        oled.show()
        sleep(1)

        timeout_connect += 1
        dot += 6

        if timeout_connect >= timeout:
            oled.fill(0)
            oled.text("No se pudo", 10, 20)
            oled.text(f"conectar a {ssid}", 10, 30)
            oled.show()

            raise Exception(f"No se pudo conectar a {ssid}")

    print(f'Conexión exitosa a {ssid}')

    oled.fill(0)
    oled.text("Conectado", 10, 0)
    oled.show()


def fetch_api_simple_price(url_base: str, api_key: str, coin_info_list: dict, timeout=15):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    url = url_base + "/simple/price?ids="
    for index, coin in enumerate(coin_info_list['coins']):
        if index == 0:
            url += coin.lower()
        else:
            url += f'%2C{coin.lower()}'
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
            print('Error en la solicitud. Código de respuesta HTTP:', response.status_code)
            return None
    except Exception as e:
        print('Error en la solicitud:', str(e))
        return None



def infoIcon(icon_id):
    with open(f'icons/{icon_id}.pbm', "rb") as file:
        file.readline()
        xy = file.readline()
        x = int(xy.split()[0])
        y = int(xy.split()[1])
        icon = bytearray(file.read())
        icon_array = framebuf.FrameBuffer(icon, x, y, framebuf.MONO_HLSB)
    return [x, y, icon_array]



def showInOled(oled, data_coins, coin_search, vs_coin):
    info_coin = data_coins[coin_search]
    icon_data = infoIcon(coin_search)
    valor = info_coin[vs_coin]
    if valor < 100:
        valor = f'{valor:0.2f}'
    change_24h = info_coin[f'{vs_coin}_24h_change']
    change_24h = f'{change_24h:0.2f}'
    def center_coin_name(name_coin, x_icon_pos):
        x = (oled.width + icon_data[0] + x_icon_pos - len(name_coin)*8)//2
        y = (icon_data[1]//2)+2
        name = name_coin.upper()
        oled.text(name, x, y)
        oled.hline(x, y+9, len(name_coin)*8, 1)
    def centerText(text, y):
        x = (oled.width - len(text)*8)//2
        oled.text(text, x, y)
    oled.fill(0)
    oled.blit(icon_data[2], 10, 5)
    center_coin_name(coin_search, 8)
    centerText(f'{valor} {vs_coin}', icon_data[1]+8)
    centerText(f'{change_24h} %', icon_data[1]+20)
    oled.show()



def showUpdate2(oled):
    oled.fill(0)
    oled.text("Consultando", 5, 30)
    oled.show()

def toggle_screen_state(screen):
    global current_screen
    print("Cambiando estado de la pantalla a:", screen)
    if screen == SCREEN_ON_1:
        current_screen = SCREEN_ON_1
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual, "WSPI", "Ingenieria Civil", "Telematica")
    elif screen == SCREEN_ON_2:
        current_screen = SCREEN_ON_2
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual)
    elif screen == SCREEN_ON_3:
        current_screen = SCREEN_ON_3
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual)
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
        imprimir_pantalla(fecha_actual)
    elif screen == SCREEN_ON_6:
        current_screen = SCREEN_ON_6
        fecha_actual = obtener_fecha()
        imprimir_pantalla(fecha_actual)


# Configura oled ssd1306 en puerto I2C 0
ANCHO = 128
ALTO = 64
i2c = machine.I2C(1, scl=machine.Pin(19), sda=machine.Pin(18))
oled = ssd1306.SSD1306_I2C(ANCHO,ALTO, i2c)
# Conectar a la red WiFi
connectWifi(oled, SSID, PASSWORD)

showUpdate2(oled)

data = fetch_api_simple_price(URL_BASE, API_KEY, coin_info)

# Imprimir la respuesta
print(data)

def Main():
    print("Iniciando bucle principal")
    while True:
        global button_state_1
        global button_state_2
        global button_state_3
        global button_state_4
        global last_button_state_1
        global last_button_state_2
        global last_button_state_3
        global last_button_state_4
        
        button_state_1 = button_pin_1.value()

        if button_state_1 != last_button_state_1 and button_state_1 == 1:
            toggle_screen_state(SCREEN_ON_1)  # Pasar la instancia de la pantalla OLED como argumento
        last_button_state_1 = button_state_1

        button_state_2 = button_pin_2.value()

        if button_state_2 != last_button_state_2 and button_state_2 == 1:
            if current_screen == SCREEN_ON_2:
                toggle_screen_state(SCREEN_ON_5)
            else:
                toggle_screen_state(SCREEN_ON_2)
                showInOled(oled, data, "bitcoin", coin_info["coin_vs"])


        last_button_state_2 = button_state_2

        button_state_3 = button_pin_3.value()
        
        button_state_4 = button_pin_4.value()
        
        if button_state_4 != last_button_state_4 and button_state_4 == 1:
            print("Botón 4 presionado")
            toggle_screen_state(SCREEN_ON_6)
            showInOled(oled, data, "cardano", coin_info["coin_vs"])


        if button_state_3 != last_button_state_3 and button_state_3 == 1:
            toggle_screen_state(SCREEN_ON_3)
            showInOled(oled, data, "ethereum", coin_info["coin_vs"])


        last_button_state_3 = button_state_3

        if button_state_1 == 1 and button_state_2 == 0 and button_state_3 == 1:
            toggle_screen_state(SCREEN_ON_4)

        if button_state_1 == 0 and button_state_2 == 0 and button_state_3 == 0 and current_screen == SCREEN_ON_4:
            toggle_screen_state(SCREEN_ON_1)
    
        if current_screen != SCREEN_OFF:
            fecha_actual = obtener_fecha()
            mostrar_icono_wifi()
            oled.show()
        utime.sleep(0.1)

        
_thread.start_new_thread(Main, ())
