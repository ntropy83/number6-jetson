#!/usr/bin/python3

import time
import subprocess
import digitalio
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import adafruit_rgb_display.st7789 as st7789        # pylint: disable=unused-import
import adafruit_rgb_display.hx8357 as hx8357        # pylint: disable=unused-import
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
import adafruit_rgb_display.ssd1351 as ssd1351      # pylint: disable=unused-import
import adafruit_rgb_display.ssd1331 as ssd1331      # pylint: disable=unused-import

import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# pylint: disable=line-too-long
# Create the display:
#disp = st7789.ST7789(spi, rotation=90                             # 2.0" ST7789
#disp = st7789.ST7789(spi, height=240, y_offset=80, rotation=90    # 1.3", 1.54" ST7789
#disp = st7789.ST7789(spi, rotation=90, width=135, height=240, x_offset=53, y_offset=40, # 1.14" ST7789
#disp = hx8357.HX8357(spi, rotation=180,                           # 3.5" HX8357
disp = st7735.ST7735R(spi, rotation=90, x_offset=2, y_offset=2,                          # 1.8" ST7735R
#disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,   # 1.44" ST7735R
#disp = st7735.ST7735R(spi, rotation=90, bgr=True,                 # 0.96" MiniTFsudoT ST7735R
#disp = ssd1351.SSD1351(spi, rotation=180,                         # 1.5" SSD1351
#disp = ssd1351.SSD1351(spi, height=96, y_offset=32, rotation=180, # 1.27" SSD1351
#disp = ssd1331.SSD1331(spi, rotation=180,                         # 0.96" SSD1331
#disp = ili9341.ILI9341(spi, rotation=90,                           # 2.2", 2.4", 2.8", 3.2" ILI9341
                      cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)
# pylint: enable=line-too-long

# Get the ADS values

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

# factor voltage divider
v_divider = 5.54546

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width   # we swap height/width to rotate it to landscape!sudo apt-get install libfreetype6-dev
    width = disp.height
else:
    width = disp.width   # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = -2
x = 0

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long
    Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

    bat = chan.voltage - 1.81 
    bat_percent = bat * 100
    bat_percent = "Batt Remaining: {:1.2f} %".format(bat_percent)

    curr_wattage = bat * 52
    curr_wattage = "Watts: {:2.0f} / 52 WH".format(curr_wattage)

    curr_voltage = v_divider * chan.voltage
    curr_voltage = "Batt Voltage: {:2.1f} V".format(curr_voltage)


    # Write eight lines of text.
    y = padding
    draw.text((x, y), IP, font=font, fill="#FFFFFF")
    y += font.getsize(IP)[1]
    draw.text((x, y), CPU, font=font, fill="#FFFF00")
    y += font.getsize(CPU)[1]
    draw.text((x, y), MemUsage, font=font, fill="#00FF00")
    y += font.getsize(MemUsage)[1]
    draw.text((x, y), Disk, font=font, fill="#0000FF")
    y += font.getsize(Disk)[1]
    draw.text((x, y), Temp, font=font, fill="#FF00FF")
    y += font.getsize(Temp)[1]
    draw.text((x, y), str(bat_percent), font=font, fill="#FF0000")
    y += font.getsize(str(bat_percent))[1]
    draw.text((x, y), str(curr_wattage), font=font, fill="#00FFFF")
    y += font.getsize(str(curr_wattage))[1]
    draw.text((x, y), str(curr_voltage), font=font, fill="#FFFF00")
    y += font.getsize(str(curr_voltage))[1]       

    # Display image.
    disp.image(image)
    time.sleep(.1)
