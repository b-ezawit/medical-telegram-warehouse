import os
from ultralytics import YOLO

def main():
    print(" Loading pre-trained YOLOv8 Nano model...")
    model = YOLO("yolov8n.pt")
    print(" Model loaded successfully!")
    print("\nSample of objects YOLO can detect:")
    sample_classes = [39, 41, 46, 73]
    for class_id in sample_classes:
        if class_id in model.names:
            print(f" - Class {class_id}: {model.names[class_id]}")

if __name__ == "__main__":
    main()