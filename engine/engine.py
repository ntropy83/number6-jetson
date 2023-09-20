#!/usr/bin/env python3

import Jetson.GPIO as GPIO
import time
import keyboard

GPIO.setwarnings(False)

motor_right_a = 11
motor_right_b = 12

motor_left_a = 15
motor_left_b = 16

motor_right_en = 32
motor_left_en = 33

speed = 40

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_right_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_a, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_left_b, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_right_en, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(motor_left_en, GPIO.OUT, initial=GPIO.HIGH)
p = GPIO.PWM(motor_right_en, 50)
w = GPIO.PWM(motor_left_en, 50)
print("Initializing...")
print("Initialized 2 PWM Pins on Enable and 4 Motor Pins")

def w_forward(e):
	p.start(speed)
	w.start(speed)
	GPIO.output(motor_right_a, GPIO.HIGH)
	GPIO.output(motor_right_b, GPIO.LOW)
	GPIO.output(motor_left_a, GPIO.LOW)
	GPIO.output(motor_left_b, GPIO.HIGH)
	time.sleep(.02)
	p.stop()
	w.stop()
	GPIO.output(motor_right_a, GPIO.LOW)
	GPIO.output(motor_left_b, GPIO.LOW)	

def s_backward(e):
	p.start(speed)
	w.start(speed)
	GPIO.output(motor_right_a, GPIO.LOW)
	GPIO.output(motor_right_b, GPIO.HIGH)
	GPIO.output(motor_left_a, GPIO.HIGH)
	GPIO.output(motor_left_b, GPIO.LOW)
	time.sleep(.02)
	p.stop()
	w.stop()
	GPIO.output(motor_right_b, GPIO.LOW)
	GPIO.output(motor_left_a, GPIO.LOW)

def a_left(e):
	p.start(speed)
	w.start(speed)
	GPIO.output(motor_right_a, GPIO.LOW)
	GPIO.output(motor_right_b, GPIO.HIGH)
	GPIO.output(motor_left_a, GPIO.LOW)
	GPIO.output(motor_left_b, GPIO.HIGH)
	time.sleep(.02)
	p.stop()
	w.stop()
	GPIO.output(motor_right_b, GPIO.LOW)
	GPIO.output(motor_left_b, GPIO.LOW)

def d_right(e):
	p.start(speed)
	w.start(speed)
	GPIO.output(motor_right_a, GPIO.HIGH)
	GPIO.output(motor_right_b, GPIO.LOW)
	GPIO.output(motor_left_a, GPIO.HIGH)
	GPIO.output(motor_left_b, GPIO.LOW)
	time.sleep(.02)
	p.stop()
	w.stop()
	GPIO.output(motor_right_a, GPIO.LOW)
	GPIO.output(motor_left_a, GPIO.LOW)

def e_inc(e):
	global speed
	if speed < 99:
		speed = speed + 10

def q_dec(e):
	global speed
	if speed > 21:
		speed = speed - 10

keyboard.on_press_key("w", w_forward)
keyboard.on_press_key("s", s_backward)
keyboard.on_press_key("a", a_left)
keyboard.on_press_key("d", d_right)
keyboard.on_press_key("e", e_inc)
keyboard.on_press_key("q", q_dec)

keyboard.wait('esc')

GPIO.cleanup()