from machine import ADC, Pin
import utime

sound_pin = machine.ADC(26)
led = Pin('LED', Pin.OUT)
led(1)

while True:
    read_value = sound_pin.read_u16()
    decibels = 30 + ((read_value/63353)*90)
    print(decibels)
    utime.sleep(0.1)
