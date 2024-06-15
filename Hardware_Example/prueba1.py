from machine import Pin, I2C
import ssd1306
import utime

# Configura los pines I2C
i2c = I2C(1, scl=Pin(19), sda=Pin(18))

# Inicializa la pantalla OLED
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Limpia la pantalla
oled.fill(0)
oled.show()

# Muestra texto en la pantalla
oled.text("Hello, World!", 0, 0)
oled.show()

# Mantén el mensaje en la pantalla por un tiempo
utime.sleep(5)
