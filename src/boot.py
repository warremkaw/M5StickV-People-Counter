import lcd
import image
import time
import uos
import sys
import os
from pmu import axp192

pmu = axp192()
pmu.enablePMICSleepMode(True)

def lcd_init():
  lcd.init(type=3)
  lcd.register(0x3A, 0x05)
  lcd.register(0xB2, [0x05, 0x05, 0x00, 0x33, 0x33])
  lcd.register(0xB7, 0x23)
  lcd.register(0xBB, 0x22)
  lcd.register(0xC0, 0x2C)
  lcd.register(0xC2, 0x01)
  lcd.register(0xC3, 0x13)
  lcd.register(0xC4, 0x20)
  lcd.register(0xC6, 0x0F)
  lcd.register(0xD0, [0xA4, 0xA1])
  lcd.register(0xD6, 0xA1)
  lcd.register(0xE0, [0x23, 0x70, 0x06, 0x0C, 0x08, 0x09, 0x27, 0x2E, 0x34, 0x46, 0x37, 0x13, 0x13, 0x25, 0x2A])
  lcd.register(0xE1,[0x70, 0x04, 0x08, 0x09, 0x07, 0x03, 0x2C, 0x42, 0x42, 0x38, 0x14, 0x14, 0x27, 0x2C])
lcd_init()
lcd.rotation(2) #Rotate the lcd 180deg

try:
    img = image.Image("/flash/startup.jpg") 
    lcd.display(img)
except:
    lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find start.jpg", lcd.WHITE, lcd.RED)

from Maix import GPIO
from fpioa_manager import *

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.LED_W, fm.fpioa.GPIO3)
led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
led_w.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1) #RGBW LEDs are Active Low

if "main.py" in os.listdir("/sd"):
    exec(open("/sd/main.py").read())
else:
    print("Error: /sd/main.py does not exist.")
