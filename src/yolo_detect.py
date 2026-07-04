import os
import glob
import pandas as pd
from ultralytics import YOLO

def run_object_detection(root_image_directory, output_csv_path):
    print(f" Scanning for images inside: {root_image_directory}")
    
    image_extensions = ('/**/*.jpg', '/**/*.jpeg', '/**/*.png')
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(root_image_directory + ext, recursive=True))
        
    if not image_paths:
        print(" No images found to process. Verify your folder path.")
        return False

    print(f" Found {len(image_paths)} images. Initializing YOLOv8...")
    model = YOLO("yolov8n.pt")
    
    detection_records = []

    for path in image_paths:
        file_name = os.path.basename(path)
        channel_name = os.path.basename(os.path.dirname(path))
        
        try:
            message_id = int(os.path.splitext(file_name)[0])
        except ValueError:
            message_id = None 

        results = model.predict(source=path, conf=0.25, verbose=False)
        result = results[0]
        
        has_person = False
        has_bottle = False
        highest_conf = 0.0
        detected_labels = []

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                conf_score = float(box.conf[0].item())
                class_name = model.names[class_id]
                
                detected_labels.append(class_name)
                
                if conf_score > highest_conf:
                    highest_conf = conf_score
                
                if class_id == 0:
                    has_person = True
                if class_id == 39:
                    has_bottle = True
        
        if has_person and has_bottle:
            image_category = "promotional"
        elif has_bottle and not has_person:
            image_category = "product_display"
        elif has_person and not has_bottle:
            image_category = "lifestyle"
        else:
            image_category = "other"

        detection_records.append({
            "message_id": message_id,
            "channel_name": channel_name,
            "file_name": file_name,
            "detected_class": ", ".join(set(detected_labels)) if detected_labels else "none",
            "confidence_score": round(highest_conf, 4),
            "image_category": image_category
        })
        print(f"   🔹 [{channel_name}] {file_name} -> Category: {image_category} (Max Conf: {round(highest_conf, 2)})")

    df = pd.DataFrame(detection_records)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    df.to_csv(output_csv_path, index=False)
    print(f"\n Success! Object detection dataset written to: {output_csv_path}")
    return True

if __name__ == "__main__":
    IMAGE_DIR = r"D:\KAIM\medical-telegram-warehouse\data\raw\images"
    OUTPUT_CSV = r"D:\KAIM\medical-telegram-warehouse\data\yolo_detections.csv"
    
    run_object_detection(IMAGE_DIR, OUTPUT_CSV)