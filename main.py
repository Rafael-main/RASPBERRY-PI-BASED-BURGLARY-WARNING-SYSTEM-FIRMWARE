import signal
import time
import requests
from gpiozero import MotionSensor

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

def open_lock():
    lock_pin = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(lock_pin, GPIO.OUT)

    # Activate the solenoid lock
    GPIO.output(lock_pin, GPIO.HIGH)
    time.sleep(5)  # Adjust the delay as needed

    # Deactivate the solenoid lock
    GPIO.output(lock_pin, GPIO.LOW)
    GPIO.cleanup()

# Function to control the buzzer
def buzz_buzzer(num_times, interval):
    # Configure the GPIO pin for the buzzer
    buzzer_pin = 23
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer_pin, GPIO.OUT)

    # Buzz the buzzer the specified number of times with the given interval
    for _ in range(num_times):
        GPIO.output(buzzer_pin, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(buzzer_pin, GPIO.LOW)
        time.sleep(interval)

    GPIO.cleanup()

def read_rfid():
    while True:
        try:
            # Read the RFID tag
            tag_id, tag_data = reader.read()

            # Validate the RFID tag and control the solenoid lock
            if tag_id in rfid_tags:
                # Open the solenoid lock
                open_lock()
                # Activate the buzzer twice with an interval of 2 seconds
                buzz_buzzer(2, 2)
            else:
                # Activate the buzzer three times with a one-second interval
                buzz_buzzer(3, 1)

            # Send RFID data to the Flask server
            payload = {'tag_id': tag_id, 'tag_data': tag_data}
            requests.post('http://localhost:5000/rfid', data=payload)

        except KeyboardInterrupt:
            GPIO.cleanup()
            break

# Function to handle PIR motion events
def handle_motion():
    while True:
        if motion_sensor.motion_detected:
            # Motion detected, take appropriate action here
            print("Motion detected")
        time.sleep(0.1)

# Create an instance of MotionSensor
motion_sensor = MotionSensor(4)

# Run the RFID reading function in a separate thread
import threading
rfid_thread = threading.Thread(target=read_rfid)
rfid_thread.start()

# Run the PIR motion handling function in a separate thread
motion_thread = threading.Thread(target=handle_motion)
motion_thread.start()


# Clean up GPIO on exit
def exit_handler(signal, frame):
    GPIO.cleanup()

signal.signal(signal.SIGINT, exit_handler)