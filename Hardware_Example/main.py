from machine import Pin, I2C, ADC
from utime import sleep_ms
from ssd1306 import SSD1306_I2C
import framebuf
import network
from time import sleep
import ntptime
from images import logo

#############################################
# Provide your Wifi connection details here #
#############################################

WIFI_SSID = "VTR-8135116"
WIFI_PASSWORD = "y8yfQcpvgbmf"

#############################################

sleep(1) # Without this, the USB handshake seems to break this script and then fail sometimes.

led = Pin("LED", Pin.OUT, value=1)

wlan = None
while not wlan or wlan.status() != 3:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Blink LED slowly until the Wifi is connected.

    while True:
        print(wlan)
        led.toggle()
        sleep(0.2)
        if wlan.status() in [-1, -2, 3]:
            break

# Set the RTC to the current time
for i in range(10):
    try:
        print("Setting system time...")
        ntptime.settime()
        print(f"System time set to {ntptime.time()}")
        break
    except Exception as e:
        print(f"Failed to set system time: {e}")
        sleep(1)

# Solid LED means we're connected and ready to go
led.on()
print(wlan)

def plot_time(yp, t, x, y, var=[0.0, 3.3], vpts=[25, 16, 40], hpts=[25, 55, 112]):
    # Axis
    oled.vline(vpts[0], vpts[1], vpts[2], 1)  # x, y, h
    oled.hline(hpts[0], hpts[1], hpts[2], 1)  # x, y, w
    oled.text(str(round(var[0], 1)), vpts[0] - 25, hpts[1] - 5)
    oled.text(str(round(var[1], 1)), vpts[0] - 25, vpts[1])
    # y - axis
    y[1] = int((yp - var[0]) / (var[1] - var[0]) * (vpts[1] - hpts[1]) + hpts[1])  # Interpolation
    if t < hpts[2] - hpts[0]:
        x[1] = x[0] + 1
    else:
        x[1] = hpts[2]

    # Plot the line
    oled.line(x[0], y[0], x[1], y[1], 1)
    oled.show()

    # Update past values
    y[0] = y[1]
    x[0] = x[1]

    # If you have already reached the end of the graph then ...
    if t > hpts[2] - hpts[0]:
        # Erases the first few pixels of the graph and the y-axis.
        oled.fill_rect(vpts[0], vpts[1], 2, vpts[2], 0)
        # Clears the entire y-axis scale
        oled.fill_rect(vpts[0] - 25, vpts[1], vpts[0], vpts[2] + 5, 0)
        # shifts the graph one pixel to the left
        oled.scroll(-1, 0)
        # Axis
        oled.vline(vpts[0], vpts[1], vpts[2], 1)  # x, y, h
        oled.hline(hpts[0], hpts[1], hpts[2], 1)  # x, y, w
        oled.text(str(round(var[0], 1)), vpts[0] - 25, hpts[1] - 5)
        oled.text(str(round(var[1], 1)), vpts[0] - 25, vpts[1])
    else:
        t += 1

    return t, x, y

if __name__ == '__main__':
    WIDTH = 128
    HEIGHT = 64
    FACTOR = 3.3 / 65535

    PLACA = True  # True: Raspberry Pi Pico, False: ESP8266

    if PLACA:
        i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=200000)
        pot = ADC(26)
    else:
        i2c = I2C(scl=Pin(5), sda=Pin(4))
        pot = ADC(0)

    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

    buffer = bytearray(logo)

    fb = framebuf.FrameBuffer(buffer, WIDTH, HEIGHT, framebuf.MONO_HLSB)

    # Configuración de los botones
    button1 = Pin(XX, Pin.IN)  # Reemplaza XX con el número de pin del botón 1
    button2 = Pin(XX, Pin.IN)  # Reemplaza XX con el número de pin del botón 2
    button3 = Pin(XX, Pin.IN)  # Reemplaza XX con el número de pin del botón 3

    # Estado inicial de los botones
    button1_state = button1.value()
    button2_state = button2.value()
    button3_state = button3.value()

    # Variable para controlar la interfaz actual
    current_interface = 1

    while True:
        # Verifica el estado de los botones
        new_button1_state = button1.value()
        new_button2_state = button2.value()
        new_button3_state = button3.value()

        # Si se presiona el botón 1, cambia a la interfaz 1
        if new_button1_state != button1_state and new_button1_state == 0:
            current_interface = 1

        # Si se presiona el botón 2, cambia a la interfaz 2
        if new_button2_state != button2_state and new_button2_state == 0:
            current_interface = 2

        # Si se presiona el botón 3, cambia a la interfaz 3
        if new_button3_state != button3_state and new_button3_state == 0:
            current_interface = 3

        # Actualiza el estado de los botones
        button1_state = new_button1_state
        button2_state = new_button2_state
        button3_state = new_button3_state

        # Lógica para mostrar la interfaz actual
        if current_interface == 1:
            oled.fill(0)
            oled.text("Interfaz 1", 30, 30)
            oled.show()
        elif current_interface == 2:
            oled.fill(0)
            oled.blit(fb, 0, 0)
            oled.show()
        elif current_interface == 3:
            volts = pot.read_u16() * FACTOR
            t, x, y = plot_time(volts, t, x, y)
            oled.show()

        # Espera un corto tiempo para evitar lecturas rápidas de los botones
        sleep_ms(100)

