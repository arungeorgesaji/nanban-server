import os
from pathlib import Path
from ultralytics import YOLO
import math
import yaml
import cv2

sensor_width = 790
focal_length = 3.63

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True) 
model = YOLO(MODEL_DIR / "yolov8m-seg.pt")

def calculate_distance(sensor_width, focal_length, object_pixel_width, screen_pixel_width, true_width):
    fov = 2 * math.atan(0.5 * sensor_width / focal_length)
    angle_of_arc = fov * (object_pixel_width / screen_pixel_width)
    true_distance = (true_width / 2) / math.tan(angle_of_arc / 2)
    return true_distance / 240

def load_object_widths(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

def check_location(x_min, y_min, x_max, y_max, frame_width, frame_height):
    object_center_x = (x_min + x_max) // 2
    object_center_y = (y_min + y_max) // 2
    
    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2
    
    margin_of_error = 10
    
    if object_center_x < frame_center_x - margin_of_error:
        return "left"
    elif object_center_x > frame_center_x + margin_of_error:
        return "right"
    else:
        return "front"

def detect_objects(image_filename):
    frame = cv2.imread(image_filename)

    if frame is None:
        print("Error: Unable to load image.")
        return

    results = model(frame)
    names = model.names
    frame_height, frame_width, _ = frame.shape
    
    for result in results:
        for box in result.boxes:
            coordinates = box.xyxy
            name = names[int(box.cls)]
            x_min, y_min, x_max, y_max = coordinates[0][0].item(),coordinates[0][1].item(),coordinates[0][2].item(),coordinates[0][3].item()
            position = check_location(int(x_min), int(y_min), int(x_max), int(y_max), frame_width, frame_height)
            if name in object_widths:
                true_width = object_widths[name]  
                distance = calculate_distance(sensor_width, focal_length, int(x_max)-int(x_min), frame_width, true_width)
                message = f"There is a {name}, around {distance:.2f} centimeters away and it is in your {position}."
                return message
            else:
                return "no_object"


object_widths = load_object_widths("object_widths.yaml")
