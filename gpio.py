import RPi.GPIO as GPIO
import time

PIN = 2

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT, initial=0)

def enable():
    GPIO.output(PIN, GPIO.LOW)

def disable():
    GPIO.output(PIN, GPIO.HIGH)
