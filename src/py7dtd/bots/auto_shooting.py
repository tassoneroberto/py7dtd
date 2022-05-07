#!/usr/bin/env python3

import argparse
import logging
import os
import time
from ctypes import windll
from pathlib import Path

import tensorflow as tf
import win32gui
from imageai.Detection.Custom import CustomObjectDetection
from PIL import ImageGrab
from py7dtd.io.commands_controller import (
    LeftMouseClick,
    MoveMouseAbsolute,
    MoveMouseRel,
)
# from py7dtd.io.key_watcher import KeyWatcher

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class AutoShooting(object):
    def __init__(self, args):
        self.stopped = False
        self.args = args

        # Adjust DPI
        user32 = windll.user32
        user32.SetProcessDPIAware()

        # Select the application window
        hwnd = win32gui.FindWindow(None, r"7 Days to Die")
        win32gui.SetForegroundWindow(hwnd)
        self.dimensions = win32gui.GetWindowRect(hwnd)

        # Fix to prevent the full GPU memory issue
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.compat.v1.Session(config=config)

        # Load the trained imageAi model
        self.detector = CustomObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        model_path = os.path.join(
            Path(os.path.dirname(__file__)).parent, Path("ai/models/v2/model.h5")
        )
        model_json_path = os.path.join(
            Path(os.path.dirname(__file__)).parent,
            Path("ai/models/v2/detection_config.json"),
        )
        self.detector.setModelPath(model_path)
        self.detector.setJsonPath(model_json_path)
        self.detector.loadModel()

        self.pointer_center = [
            (self.dimensions[2] - self.dimensions[0]) // 2,
            (self.dimensions[3] - self.dimensions[1]) // 2,
        ]

    def start(self):
        # FIXME: key watcher thread not working
        # self.key_watcher = KeyWatcher(stop_func=self.stop)
        # self.key_watcher.start()

        while not self.stopped:
            print("stopped status: " + str(self.stopped))
            logging.info("Capturing new image...")
            # Capture the frame
            image = ImageGrab.grab(self.dimensions)
            image.save(f"capture.png")
            # Objects detection
            detections = self.detector.detectObjectsFromImage(
                input_image="capture.png",
                output_image_path="capture_output.png",
                minimum_percentage_probability=70,
            )
            detected_entities = {}
            for detection in detections:
                if detection["name"] not in detected_entities:
                    detected_entities[detection["name"]] = []
                detected_entities[detection["name"]].append(detection["box_points"])

            logging.info(f"Detected Entities: {detected_entities}")

            # If zombies are detected, get the nearest (biggest rectangle)
            if "zombie" in detected_entities:
                nearest = detected_entities["zombie"][0]
                if len(detected_entities["zombie"]) > 1:
                    nearest_area = (nearest[2] - nearest[0]) * (nearest[3] - nearest[1])
                    for current in detected_entities["zombie"]:
                        current_area = (current[2] - current[0]) * (
                            current[3] - current[1]
                        )
                        if current_area > nearest_area:
                            nearest = current
                zombie_center = (
                    int((nearest[2] - nearest[0]) // 2 + nearest[0]),
                    int((nearest[3] - nearest[1]) // 2 + nearest[1]),
                )

                rel_move = [
                    zombie_center[0] - self.pointer_center[0],
                    zombie_center[1] - self.pointer_center[1],
                ]

                logging.info(f"Shooting at zombie in: {zombie_center}")
                # TODO: Fix the precision of mouse relative movement
                MoveMouseRel(rel_move[0], rel_move[1])
                LeftMouseClick()

            time.sleep(self.args.delay / 1000)

        logging.info("Auto shooting stopped")

    def stop(self):
        self.stopped = True

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay", default=500, help="Time in ms between each screenshot", type=int
    )
    
    return parser

def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    auto_shooting = AutoShooting(args)
    auto_shooting.start()


if __name__ == "__main__":
    main()
