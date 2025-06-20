#!/usr/bin/env python3

import argparse
import logging
import threading
import time

from PIL import ImageGrab
from py7dtd.ai.detection import Detector
from py7dtd.constants import APPLICATION_WINDOW_NAME, ENTITY_ZOMBIE

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

        # Load the trained model
        self.detector = Detector(self.args.dataset)

    def watch_keys(self):
        self.watcher = KeyWatcher(stop_func=self.stop)
        self.watcher.start()

    def start(self):
        # Select the application window
        try:
            self.window = select_window(APPLICATION_WINDOW_NAME)
        except Exception as err:
            logging.error(str(err))
            return
        self.pointer_center = get_relative_window_center(
            int(self.window.width), int(self.window.height)
        )

        # Spawn the key_watcher thread
        self.watcher_thread = threading.Thread(target=self.watch_keys, args=())
        # Daemon = True -> kill it when main thread terminates
        self.watcher_thread.setDaemon(True)
        self.watcher_thread.start()

        while not self.stopped:
            logging.info("Capturing new image...")
            # Capture the frame
            image = ImageGrab.grab(
                bbox=(
                    int(self.window.left),
                    int(self.window.top),
                    int(self.window.left) + int(self.window.width),
                    int(self.window.top) + int(self.window.height),
                )
            )
            # Objects detection
            detected_entities = self.detector.analyze(image)

            logging.info(f"Detected Entities: {detected_entities}")

            # If zombies are detected, get the nearest (biggest rectangle)
            if ENTITY_ZOMBIE in detected_entities:
                nearest = detected_entities[ENTITY_ZOMBIE][0]
                if len(detected_entities[ENTITY_ZOMBIE]) > 1:
                    nearest_area = (nearest[2] - nearest[0]) * (
                        nearest[3] - nearest[1]
                    )
                    for current in detected_entities[ENTITY_ZOMBIE]:
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
                # FIXME: the precision of mouse relative movement
                # https://github.com/tassoneroberto/py7dtd/issues/19
                MoveMouseRel(rel_move[0], rel_move[1])
                LeftMouseClick()

            time.sleep(self.args.delay / 1000)

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

    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    auto_shooting = AutoShooting(args)
    auto_shooting.start()


if __name__ == "__main__":
    main()
