import machine
import ssd1306
import utime
import framebuf
import network
import _thread
import socket
import time
import struct

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

NTP_DELTA = 2208988800 + (3600 * 4)  # GMT-4 Santiago de Chile

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
        imprimir_pantalla(fecha_actual, "Certamenes:", "MAT070    18/06", "FIS100    16/06", "MAT060    21/06")
        
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
            toggle_screen_state(SCREEN_ON_1)

        last_button_state_1 = button_state_1

        button_state_2 = button_pin_2.value()

        if button_state_2 != last_button_state_2 and button_state_2 == 1:
            if current_screen == SCREEN_ON_2:
                toggle_screen_state(SCREEN_ON_5)
            else:
                toggle_screen_state(SCREEN_ON_2)

        last_button_state_2 = button_state_2

        button_state_3 = button_pin_3.value()
        
        button_state_4 = button_pin_4.value()
        
        if button_state_4 != last_button_state_4 and button_state_4 == 1:
            print("Botón 4 presionado")
            toggle_screen_state(SCREEN_ON_6)

        if button_state_3 != last_button_state_3 and button_state_3 == 1:
            toggle_screen_state(SCREEN_ON_3)

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

