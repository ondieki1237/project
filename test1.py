import cv2
import serial
import time

# Path to cars.xml - adjust this according to your file location
cascade_path = r'C:\Users\makor\Desktop\SMO\PROJECT\code\cars.xml'

# Initialize cascade classifier for cars
car_cascade = cv2.CascadeClassifier(cascade_path)

# Check if cascade classifier loaded successfully
if car_cascade.empty():
    print(f"Error: Cascade classifier not loaded from {cascade_path}")
    exit()

# Function to count vehicles in an image
def count_vehicles(image_path):
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return -1, None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect cars in the image
    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected vehicles (for visualization)
    for (x, y, w, h) in cars:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Return number of cars detected and the image with vehicles outlined
    return len(cars), img

# Function to control LEDs based on vehicle count and communicate with Arduino
def control_leds(vehicle_count, img):
    # Define Arduino's serial port and baud rate
    ser = serial.Serial('COM4', 9600)  # Replace 'COM4' with your Arduino's serial port

    # Wait for serial port to initialize
    time.sleep(2)

    # Set LED to RED initially when not actively controlling
    ser.write(b'R')

    # Calculate time allocated for green light based on vehicle count (max 30 seconds)
    max_green_seconds = 30
    green_light_seconds = min(vehicle_count, max_green_seconds // 2)  # Half of max allocated time

    # Display image with vehicles outlined
    cv2.imshow('Detected Vehicles', img)
    cv2.waitKey(2000)  # Display image for 2 seconds (adjust as needed)

    # Control LEDs based on vehicle count
    if vehicle_count == -1:
        ser.write(b'R')  # Turn LED RED if vehicle count failed
    elif vehicle_count == 0:
        ser.write(b'R')  # Turn LED RED if no vehicles detected
    elif vehicle_count > 0 and vehicle_count <= 5:
        ser.write(b'Y')  # Turn LED YELLOW if 1-5 vehicles detected
    else:
        ser.write(b'G')  # Turn LED GREEN for calculated seconds
        ser.write(str(green_light_seconds).encode())  # Send green light duration

    # Close serial connection
    ser.close()

    # Return to standby mode in YELLOW after green light duration
    time.sleep(green_light_seconds)
    ser = serial.Serial('COM4', 9600)  # Reopen serial port
    ser.write(b'Y')  # Turn LED YELLOW
    ser.close()

# Example usage:
if __name__ == "__main__":
    image_path = r'C:\Users\makor\Desktop\SMO\PROJECT\code\Resources\2side.jpg'  # Replace with your image path
    vehicle_count, image = count_vehicles(image_path)
    
    if vehicle_count == -1:
        print("Vehicle count failed due to image reading error.")
    else:
        print(f"Number of vehicles detected: {vehicle_count}")
        control_leds(vehicle_count, image)
