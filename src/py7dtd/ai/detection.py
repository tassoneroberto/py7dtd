#!/usr/bin/env python3

from imageai.Detection.Custom import CustomObjectDetection
from PIL import Image


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

    def analyze(self, image: Image.Image) -> dict:
        detections = self.detector.detectObjectsFromImage(
            input_image=image,
            minimum_percentage_probability=70,
        )

        detected_entities = {}
        for detection in detections:
            if detection["name"] not in detected_entities:  # type: ignore
                detected_entities[detection["name"]] = []  # type: ignore

            detected_entities[detection["name"]].append(  # type: ignore
                detection["box_points"]  # type: ignore
            )

        return detected_entities
