import RPi.GPIO as GPIO
import time
import cv2
import subprocess
from datetime import datetime


# GPIO Mode (BCM)
GPIO.setmode(GPIO.BCM)

# set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    """
    This function measures the distance using the HC-SR04 sensor.
    """
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def capture_image():
    """
    This function captures an image using the USB camera and saves it with the current date and time as the filename.
    """
    cap = cv2.VideoCapture(0)  # '0' for the default camera. Adjust if you have multiple cameras.
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    ret, frame = cap.read()
    
    # Get the current date and time, format it, and use it as the filename
    now = datetime.now()
    filename = now.strftime('%Y-%m-%d_%H-%M-%S.jpg')
    image_path = f'/home/everest/{filename}'  # Adjust the directory as needed

    cv2.imwrite(image_path, frame)
    
    cap.release()
    cv2.destroyAllWindows()
    return image_path


def send_via_bluetooth(image_path):
    """
    This function sends the captured image to the paired device using Bluetooth.
    """
    laptop_mac_address = 'E0:2B:E9:84:55:25'  # Replace with your laptop's Bluetooth MAC address
    # obex_channel = '3'  # This is often 3, but it might be different for your device
    try:
        # Command to send file via Bluetooth
        command = f'bluetooth-sendto --device={laptop_mac_address} {image_path}'
        
        # Execute the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(f'Successfully sent {image_path} to the laptop.')
        else:
            print(f'Failed to send {image_path} to the laptop. Error: {stderr}')
    
    except Exception as e:
        print(f'An error occurred: {e}')

try:
    while True:
        dist = distance()
        print ("Measured Distance = %.1f cm" % dist)
        if dist < 10:  # Adjust this value to the distance threshold you want
            image_path = capture_image()
            send_via_bluetooth(image_path)
            time.sleep(1)  # Prevents multiple captures for the same event

        time.sleep(1)  # Adjust this for how often you want to check the distance

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
