import machine
import utime

button = machine. Pin(14,machine.Pin.IN, machine.Pin.PULL_DOWN)

while True:
    if button.value() :
        print("Presionaste el Boton")
        utime.sleep (2)
