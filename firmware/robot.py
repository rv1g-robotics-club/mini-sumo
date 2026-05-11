from machine import Pin, PWM, ADC, I2C
import neopixel
from button import Button
import time

# NeoPixel LEDs
np = neopixel.NeoPixel(Pin(8), 6)

# Buttons
btns = [Button(47),
       Button(48),
       Button(0)]

# Buzzer
buzzer = PWM(Pin(21), duty_u16=0)

# Floor sensors
flrL = ADC(Pin(5))
flrR = ADC(Pin(2))
flrL.atten(ADC.ATTN_11DB)
flrR.atten(ADC.ATTN_11DB)

# Battery
battery = ADC(Pin(7))
battery.atten(ADC.ATTN_11DB)

# Opponent sensors
objSens = [
  Pin(6, Pin.IN),
  Pin(4, Pin.IN),
  Pin(1, Pin.IN),
  Pin(42, Pin.IN)]

irLed = PWM(Pin(18))
irLed.freq(38000)
irLed.duty_u16(0x8000)


def clearLeds():
  for i in range(6):
    np[i] = (0,0,0)
  np.write()

def showOneLed(idx, color):
  for i in range(6):
    if(i == idx):
      np[i] = color
    else:
      np[i] = (0,0,0)
  np.write()
    
def beep(freq, durationMs):
  buzzer.freq(freq)
  buzzer.duty_u16(10000)
  time.sleep_ms(durationMs)
  buzzer.duty_u16(0)
    
def waitButtonPress(btn):
  while(btn.getEvent() != Button.PRESS):
    time.sleep_ms(10)
        
def waitButtonRelease(btn):
  while(btn.getEvent() != Button.RELEASE):
    time.sleep_ms(10)
    
def calibrateFloorSensors():
  blackValue = [0, 0]
  whiteValue = [0, 0]
  
  # Read Black
  print("Put on Black surface and press BTN2")
  waitButtonPress(btns[1])
  for _ in range(100):
    blackValue[0] = blackValue[0] + flrL.read_u16()
    blackValue[1] = blackValue[1] + flrR.read_u16()
  blackValue[0] = blackValue[0] // 100
  blackValue[1] = blackValue[1] // 100
  
  # Read White
  print("Put on White surface and press BTN2")
  waitButtonPress(btns[1])
  for _ in range(100):
    whiteValue[0] = whiteValue[0] + flrL.read_u16()
    whiteValue[1] = whiteValue[1] + flrR.read_u16()
  whiteValue[0] = whiteValue[0] // 100
  whiteValue[1] = whiteValue[1] // 100
  
  return [blackValue[0] + (whiteValue[0] - blackValue[0]) / 2,
          blackValue[1] + (whiteValue[1] - blackValue[1]) / 2]
    
def readBattery():
  vot = battery.read_uv() / 1000000 * ((10 + 4.7) / 4.7)
  return vot
