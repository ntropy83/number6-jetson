#!/usr/bin/env python3

import Jetson.GPIO as GPIO
from pyPS4Controller.controller import Controller
import os
from rplidar import RPLidar

GPIO.setwarnings(False)
motor_right_a = 11
motor_right_b = 12
motor_left_a = 15
motor_left_b = 16
motor_right_en = 32
motor_left_en = 33
enable_tft = 31

speed = 40

print("Initializing...")

LIDAR_REV_PORT_NAME = '/dev/ttyUSB0'

lidar = RPLidar(LIDAR_REV_PORT_NAME)
lidar.motor_speed=0
print("Initialized 360° Lidar, went idling...")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_right_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_en, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(motor_left_en, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(enable_tft, GPIO.OUT, initial=GPIO.LOW)
p = GPIO.PWM(motor_right_en, 50)
w = GPIO.PWM(motor_left_en, 50)
print("Initialized 2 PWM Pins on Enable and 4 Motor Pins")

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_up_arrow_press(self):
        p.start(speed)
        w.start(speed)
        GPIO.output(motor_right_a, GPIO.HIGH)
        GPIO.output(motor_right_b, GPIO.LOW)
        GPIO.output(motor_left_a, GPIO.LOW)
        GPIO.output(motor_left_b, GPIO.HIGH)

    def on_down_arrow_press(self):
        p.start(speed)
        w.start(speed)
        GPIO.output(motor_right_a, GPIO.LOW)
        GPIO.output(motor_right_b, GPIO.HIGH)
        GPIO.output(motor_left_a, GPIO.HIGH)
        GPIO.output(motor_left_b, GPIO.LOW)

    def on_up_down_arrow_release(self):
        p.stop()
        w.stop()
        GPIO.output(motor_right_a, GPIO.LOW)
        GPIO.output(motor_left_b, GPIO.LOW)
        GPIO.output(motor_right_b, GPIO.LOW)
        GPIO.output(motor_left_a, GPIO.LOW)

    def on_left_arrow_press(self):
        p.start(speed)
        w.start(speed)
        GPIO.output(motor_right_a, GPIO.LOW)
        GPIO.output(motor_right_b, GPIO.HIGH)
        GPIO.output(motor_left_a, GPIO.LOW)
        GPIO.output(motor_left_b, GPIO.HIGH)

    def on_right_arrow_press(self):
        p.start(speed)
        w.start(speed)
        GPIO.output(motor_right_a, GPIO.HIGH)
        GPIO.output(motor_right_b, GPIO.LOW)
        GPIO.output(motor_left_a, GPIO.HIGH)
        GPIO.output(motor_left_b, GPIO.LOW)
   
    def on_left_right_arrow_release(self):
        p.stop()
        w.stop()
        GPIO.output(motor_right_b, GPIO.LOW)
        GPIO.output(motor_left_b, GPIO.LOW)
        GPIO.output(motor_right_a, GPIO.LOW)
        GPIO.output(motor_left_a, GPIO.LOW)

    def on_L1_press(self):
        global speed
        if speed < 99:
    	    speed = speed + 10

    def on_R1_press(self):
        global speed
        if speed > 21:
            speed = speed - 10
    
    def on_square_press(self):
        if GPIO.input(enable_tft):
            GPIO.output(enable_tft, GPIO.LOW)
        else:    
            GPIO.output(enable_tft, GPIO.HIGH)
            os.system("$HOME/Pogramme/robot_ctl/sensors/battery_mon/stats.py &")
    
    def on_circle_press(self):
        os.system("python3 $HOME/Programme/robot_ctl/sensors/Lidar/360Lidar.py &")


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen(timeout=600)