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

            # response_curr_route = requests.get('http://localhost:5000/curr_route')
            send_tag = requests.post('http://localhost:5000/read_tag', data= {'tag_id' : tag_id})
            data_check_tag = send_tag.json()
            # data_curr_route = response_curr_route.json()  


            # payload = {'status':'ok','tag_id': tag_id, 'tag_data': tag_data}
            # if data_curr_route == 'http://127.0.0.1:5000/table':
            #     requests.post('http://127.0.0.1:5000/add_logs', payload)  
            # elif data_curr_route == 'http://127.0.0.1:5000/create':
            #     requests.post('http://127.0.0.1:5000/rfid', payload)

            # Validate the RFID tag and control the solenoid lock
            if data_check_tag['status'] == 'ok' and data_check_tag['message'] == 'RFID tag exists in the database' and data_check_tag['passage'] == 'committed':
                # Open the solenoid lock
                open_lock()
                # Activate the buzzer twice with an interval of 2 seconds
                buzz_buzzer(2, 2)
            else:
                # Activate the buzzer three times with a one-second interval
                buzz_buzzer(3, 1)

            # Send RFID data to the Flask server
            payload = {'status':'ok','tag_id': tag_id, 'tag_data': tag_data}
            requests.post('http://localhost:5000/rfidtag', data=payload)

        except KeyboardInterrupt:
            GPIO.cleanup()
            break

# Function to handle PIR motion events
def handle_motion():
    while True:
        if motion_sensor.motion_detected:
            print("Motion 0 detected")
            payload = {'message': 'Intruder Detected!'}
            requests.post('http://localhost:5000/motion', data=payload)
        time.sleep(0.2)
def handle_motion_1():
    while True:
        if motion_sensor.motion_detected:
            print("Motion 1 detected")
            payload = {'message': 'Intruder Detected!'}
            requests.post('http://localhost:5000/motion', data=payload)
        time.sleep(0.2)

def handle_motion_2():
    while True:
        if motion_sensor.motion_detected:
            print("Motion 2 detected")
            payload = {'message': 'Intruder Detected!'}
            requests.post('http://localhost:5000/motion', data=payload)
        time.sleep(0.2)
# Create an instance of MotionSensor
motion_sensor = MotionSensor(4)

# Run the RFID reading function in a separate thread
import threading
rfid_thread = threading.Thread(target=read_rfid)
rfid_thread.start()

# Run the PIR motion handling function in a separate thread
motion_thread = threading.Thread(target=handle_motion)
motion_thread.start()

motion_thread_1 = threading.Thread(target=handle_motion_1)
motion_thread_1.start()

motion_thread_2 = threading.Thread(target=handle_motion_2)
motion_thread_2.start()

# Clean up GPIO on exit
def exit_handler(signal, frame):
    GPIO.cleanup()

signal.signal(signal.SIGINT, exit_handler)