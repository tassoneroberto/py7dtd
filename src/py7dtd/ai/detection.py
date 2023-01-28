#!/usr/bin/env python3

from imageai.Detection.Custom import CustomObjectDetection


class Detector:
    def __init__(self, dataset_path):
        self.detector = CustomObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(
            f"{dataset_path}/models/yolov3_dataset_last.pt"
        )
        self.detector.setJsonPath(
            f"{dataset_path}/json/dataset_yolov3_detection_config.json"
        )
        self.detector.loadModel()

    def analyze(self, input_image, output_image):
        detections = self.detector.detectObjectsFromImage(
            input_image=input_image,
            output_image_path=output_image,
            minimum_percentage_probability=70,
        )

        detected_entities = {}
        for detection in detections:
            if detection["name"] not in detected_entities:
                detected_entities[detection["name"]] = []

            detected_entities[detection["name"]].append(
                detection["box_points"]
            )

        return detected_entities
