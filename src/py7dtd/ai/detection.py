#!/usr/bin/env python3

from imageai.Detection.Custom import CustomObjectDetection

LATEST_MODEL_VERSION = "v2"


class Detector:
    def __init__(self, model_version=LATEST_MODEL_VERSION):
        self.detector = CustomObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(f"ai/models/{model_version}/model.h5")
        self.detector.setJsonPath(f"ai/models/{model_version}/detection_config.json")
        self.detector.loadModel()

    def analyze(self, input_image):
        detections = self.detector.detectObjectsFromImage(
            input_image=input_image,
            output_image_path="capture_output.png",
            minimum_percentage_probability=70,
        )
        detected_entities = {}
        for detection in detections:
            if detection["name"] not in detected_entities:
                detected_entities[detection["name"]] = []
            else:
                detected_entities[detection["name"]].append(detection["box_points"])
            # print(detection["name"], " : ", detection["percentage_probability"], " : ", detection["box_points"])
        return detected_entities
