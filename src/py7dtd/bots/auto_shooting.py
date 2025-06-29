#!/usr/bin/env python3

import argparse
import logging
import os
import threading
import time
from datetime import datetime

from PIL import ImageDraw, ImageGrab
from py7dtd.ai.detection import Detector
from py7dtd.constants import (
    APPLICATION_WINDOW_NAME,
    DEFAULT_HORIZONTAL_FIELD_OF_VIEW,
    ENTITY_ZOMBIE,
    MAX_HORIZONTAL_FIELD_OF_VIEW,
    MIN_HORIZONTAL_FIELD_OF_VIEW,
)

from iocontroller.keymouse.commands_controller import (
    LeftMouseClick,
    MoveMouseRel,
)
from iocontroller.keymouse.key_watcher import KeyWatcher
from iocontroller.window.window_handler import (
    get_relative_window_center,
    select_window,
)

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class AutoShooting(object):

    def __init__(self, args):
        self.stopped = False
        self.args = args
        self.check_args()

        if self.args.log:
            logging.root.setLevel(level=self.args.log)

        if self.args.debug:
            logging.info("Debug mode is enabled")
            logging.root.setLevel(level=logging.DEBUG)
            os.makedirs("./debug", exist_ok=True)

        logging.debug(f"Arguments: {self.args}")

        # Load the trained model
        self.detector = Detector(self.args.dataset)

    def check_args(self):
        if not self.args.dataset:
            raise ValueError("Dataset path is required")
        if not self.args.delay or self.args.delay < 0:
            raise ValueError("Delay must be a positive integer")
        if not (
            MIN_HORIZONTAL_FIELD_OF_VIEW
            <= self.args.hfov
            <= MAX_HORIZONTAL_FIELD_OF_VIEW
        ):
            raise ValueError(
                f"Field of view must be between {MIN_HORIZONTAL_FIELD_OF_VIEW} and {MAX_HORIZONTAL_FIELD_OF_VIEW}"
            )

    def watch_keys(self):
        self.watcher = KeyWatcher(stop_func=self.stop)
        self.watcher.start()

    def start(self):
        self.window = select_window(APPLICATION_WINDOW_NAME)
        window_width = self.window.width
        window_height = self.window.height

        self.pointer_center = get_relative_window_center(
            int(window_width), int(window_height)
        )
        logging.debug(f"Pointer center: {self.pointer_center}")
        center_x = self.pointer_center[0]
        center_y = self.pointer_center[1]

        logging.debug(f"Horizontal field of view: {self.args.hfov} degrees")
        degrees_per_pixel_x = self.args.hfov / window_width
        logging.debug(f"Degrees per pixel X: {degrees_per_pixel_x}")
        aspect_ratio = window_width / window_height
        logging.debug(f"Aspect ratio: {aspect_ratio}")
        vertical_fov = self.args.hfov / aspect_ratio
        logging.debug(f"Vertical field of view: {vertical_fov} degrees")
        degrees_per_pixel_y = vertical_fov / window_height
        logging.debug(f"Degrees per pixel Y: {degrees_per_pixel_y}")

        degrees_per_count = 0.09  # Fine-tuned value for mouse movement
        logging.debug(f"Degrees per count: {degrees_per_count}")

        capture_area = (
            int(self.window.left),
            int(self.window.top),
            int(self.window.left) + int(window_width),
            int(self.window.top) + int(window_height),
        )
        logging.debug(f"Capture area: {capture_area}")

        # Spawn the key_watcher thread
        self.watcher_thread = threading.Thread(target=self.watch_keys, args=())
        # Daemon = True -> kill it when main thread terminates
        self.watcher_thread.daemon = True
        self.watcher_thread.start()

        while not self.stopped:
            time.sleep(self.args.delay / 1000)
            logging.debug("Capturing new image...")
            image = ImageGrab.grab(bbox=capture_area)

            logging.debug("Analyzing...")
            detected_entities = self.detector.analyze(image)
            logging.debug(f"Detected Entities: {detected_entities}")

            if ENTITY_ZOMBIE not in detected_entities:
                continue

            # Select the nearest (biggest target area)
            nearest_target = detected_entities[ENTITY_ZOMBIE][0]
            if len(detected_entities[ENTITY_ZOMBIE]) > 1:
                nearest_area = (nearest_target[2] - nearest_target[0]) * (
                    nearest_target[3] - nearest_target[1]
                )
                for current in detected_entities[ENTITY_ZOMBIE]:
                    current_area = (current[2] - current[0]) * (
                        current[3] - current[1]
                    )
                    if current_area > nearest_area:
                        nearest_target = current

            logging.debug(f"Nearest target: {nearest_target}")

            target_center = (
                int(
                    (nearest_target[2] - nearest_target[0]) // 2
                    + nearest_target[0]
                ),
                int(
                    (nearest_target[3] - nearest_target[1]) // 2
                    + nearest_target[1]
                ),
            )
            logging.debug(f"Nearest target center: {target_center}")

            target_x = target_center[0]
            target_y = target_center[1]

            angle_x = (target_x - center_x) * degrees_per_pixel_x
            angle_y = (target_y - center_y) * degrees_per_pixel_y

            mouse_move_x = angle_x / degrees_per_count
            mouse_move_y = angle_y / degrees_per_count
            logging.debug(
                f"Mouse move X: {mouse_move_x}, Mouse move Y: {mouse_move_y}"
            )

            logging.info(f"Shooting at entity in: {target_center}")
            MoveMouseRel(mouse_move_x, mouse_move_y)
            # Wait for the game to process the mouse movement
            time.sleep(0.1)

            if self.args.debug and detected_entities:
                logging.debug("Generating debug images...")
                # Draw the detected entities and the target on the image
                drawable = ImageDraw.Draw(image)
                for entity, boxes in detected_entities.items():
                    for box in boxes:
                        drawable.rectangle(box, outline="red", width=2)
                        drawable.text((box[0], box[1]), entity, fill="red")
                drawable.ellipse(
                    [
                        (target_center[0] - 5, target_center[1] - 5),
                        (target_center[0] + 5, target_center[1] + 5),
                    ],
                    fill="green",
                )
                drawable.line(
                    [self.pointer_center, target_center],
                    fill="green",
                    width=2,
                )

                # Take a screenshot after the mouse movement
                image_after = ImageGrab.grab(bbox=capture_area)
                drawable_after = ImageDraw.Draw(image_after)
                drawable_after.ellipse(
                    [
                        (
                            self.pointer_center[0] - 5,
                            self.pointer_center[1] - 5,
                        ),
                        (
                            self.pointer_center[0] + 5,
                            self.pointer_center[1] + 5,
                        ),
                    ],
                    fill="green",
                )

                # Save the debug images with timestamps
                filename = datetime.now().strftime("%Y%m%d-%H%M%S_%f")

                path_before = f"./debug/{filename}_0.jpg"
                image.save(path_before)
                logging.debug(
                    f"Saved debug image before shooting: {path_before}"
                )

                path_after = f"./debug/{filename}_1.jpg"
                image_after.save(path_after)
                logging.debug(
                    f"Saved debug image after shooting: {path_after}"
                )

            LeftMouseClick()

        logging.info("Auto shooting stopped")

    def stop(self):
        self.stopped = True


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="./dataset",
        help="Dataset folder path",
        type=str,
    )
    parser.add_argument(
        "--delay",
        default=500,
        help="Time in ms between each screenshot",
        type=int,
    )
    parser.add_argument(
        "--hfov",
        default=DEFAULT_HORIZONTAL_FIELD_OF_VIEW,
        help="Horizontal field of view in degrees (in-game option)",
        type=int,
    )
    parser.add_argument(
        "--log",
        default=logging.INFO,
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        type=lambda x: x.upper(),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    return parser


def main():
    logging.info("Starting Auto Shooting Bot...")
    AutoShooting(get_argument_parser().parse_args()).start()
    logging.info("Auto Shooting Bot has been stopped.")


if __name__ == "__main__":
    main()
