import cv2
import serial
import time

# Path to cars.xml - adjust this according to your file location
cascade_path = r'C:\Users\makor\Desktop\SMO\PROJECT\code\cars.xml'

# Initialize cascade classifier for cars
car_cascade = cv2.CascadeClassifier(cascade_path)

# Function to count vehicles in an image
def count_vehicles(image_path):
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return -1

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect cars in the image
    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Return number of cars detected
    return len(cars)

# Function to control LEDs based on vehicle count
def control_leds(vehicle_count):
    # Define Arduino's serial port and baud rate
    ser = serial.Serial('COM4', 9600)  # Replace 'COM4' with your Arduino's serial port

    # Wait for serial port to initialize
    time.sleep(2)

    # Calculate time allocated for green light based on vehicle count (max 30 seconds)
    max_green_seconds = 30
    green_light_seconds = min(vehicle_count, max_green_seconds // 2)  # Half of max allocated time

    # Control LEDs based on vehicle count
    if vehicle_count == 0:
        ser.write(b'R')  # Turn LED RED
    elif vehicle_count > 0 and vehicle_count <= 5:
        ser.write(b'Y')  # Turn LED YELLOW
    else:
        ser.write(b'G')  # Turn LED GREEN for calculated seconds
        ser.write(str(green_light_seconds).encode())  # Send green light duration

    # Close serial connection
    ser.close()

# Example usage:
if __name__ == "__main__":
    image_path = r'C:\Users\makor\Desktop\SMO\PROJECT\code\Resources\trucks.jpg'  # Replace with your image path
    vehicle_count = count_vehicles(image_path)
    
    if vehicle_count == -1:
        print("Vehicle count failed due to image reading error.")
    else:
        print(f"Number of vehicles detected: {vehicle_count}")
        control_leds(vehicle_count)
