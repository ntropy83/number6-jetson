#!/usr/bin/python3

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from tkinter import Tk,Label
from digitalio import DigitalInOut, Direction, Pull

led_red = DigitalInOut(board.D20)
led_green = DigitalInOut(board.D26)

led_red.direction = Direction.OUTPUT
led_green.direction = Direction.OUTPUT

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

# draw GUI

root = Tk()
root.title('Robot_No6_BatMon')

w = 150 # width for the Tk root
h = 50 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = ws - (w)
y = 0

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

Label(root, text="Battery Percentage Left:", font=("Arial", 25)).pack()

def update_text():

    # Calculate bat_percent bar 

    bat_percent = chan.voltage - 1.9
    curr_wattage = bat_percent * 52    
    bat_percent = bat_percent * 100
    curr_voltage = v_divider * chan.voltage


    if (bat_percent > 100):
        l.config(text="100 % / 16.8 Volt\n52 Wh")
    else:
        l.config(text="{:.0f} % / {:.1f} Volt\n{:.0f} Wh (52 Wh Design)".format(bat_percent, curr_voltage, curr_wattage))
        if(bat_percent < 50):
            led_green.value = True
        elif(bat_percent < 20):
            led_green.value = False
            led_red.value = True
    root.after(10000, update_text)

l = Label(root,
      text="",
      font=("Arial", 25)
      )
l.pack()

update_text()
root.mainloop()

GPIO.cleanup()