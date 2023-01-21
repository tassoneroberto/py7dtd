#!/usr/bin/env python3

import argparse
import datetime
import logging
import os
import threading
import time

from PIL import ImageGrab
from py7dtd.constants import APPLICATION_WINDOW_NAME
from py7dtd.io.key_watcher import KeyWatcher
from py7dtd.io.window_handler import select_window

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class BlocksDetection(object):
    def __init__(self, args):
        self.stopped = False
        self.args = args
        self.init_args()

    def init_args(self):
        if not self.args.topsoil and not self.args.destroyed:
            logging.error(
                "Error: No blocks selected."
                + " Select at least one of: [`topsoil`, `destroyed`]."
            )
            exit()
        if not os.path.exists(self.args.output):
            os.makedirs(self.args.output)
            logging.info(f"Folder {self.args.output} created successfully.")

    def watch_keys(self):
        self.watcher = KeyWatcher(stop_func=self.stop, p_func=self.p_func)
        self.watcher.start()

    def start(self):
        try:
            self.dimensions = select_window(APPLICATION_WINDOW_NAME)
        except Exception as err:
            logging.error(str(err))
            return

        self.watcher_thread = threading.Thread(target=self.watch_keys, args=())
        # Daemon = True -> kill it when main thread terminates
        self.watcher_thread.setDaemon(True)
        self.watcher_thread.start()

        while not self.stopped:
            time.sleep(5)

        logging.info("Blocks detection stopped")

    def stop(self):
        self.stopped = True

    def p_func(self):
        # Capture the frame
        image = ImageGrab.grab(self.dimensions)
        pixels = image.load()
        for x in range(0, self.dimensions[2] - self.dimensions[0]):
            for y in range(0, self.dimensions[3] - self.dimensions[1]):
                # FIXME: adjust precision
                # https://github.com/tassoneroberto/py7dtd/issues/18
                if self.args.destroyed:
                    if (
                        pixels[x, y][0] >= 125
                        and pixels[x, y][0] <= 125
                        and pixels[x, y][1] >= 125
                        and pixels[x, y][1] <= 125
                        and pixels[x, y][2] >= 54
                        and pixels[x, y][2] <= 54
                    ):  # destroyed stone
                        pixels[x, y] = (255, 0, 0)  # mark it red
                if self.args.topsoil:
                    if (
                        pixels[x, y][0] >= 12
                        and pixels[x, y][0] <= 19
                        and pixels[x, y][1] >= 40
                        and pixels[x, y][1] <= 53
                        and pixels[x, y][2] >= 19
                        and pixels[x, y][2] <= 19
                    ):  # topsoil
                        pixels[x, y] = (255, 0, 0)  # mark it red

        filename = (
            f'{str(datetime.datetime.now().strftime("%Y%m%d-%I%M%S%f"))}.png'
        )
        full_path = os.path.join(self.args.output, filename)
        image.save(full_path)
        logging.info(f"New block detection picture created -> {full_path}")


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topsoil",
        default=False,
        help="Detect topsoil blocks",
        action="store_true",
    )
    parser.add_argument(
        "--destroyed",
        default=False,
        help="Detect destroyed stone blocks",
        action="store_true",
    )
    parser.add_argument(
        "--output", default="blocks_detection", help="Output folder", type=str
    )
    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    blocks_detection = BlocksDetection(args)
    blocks_detection.start()

    logging.info("Process terminated.")


if __name__ == "__main__":
    main()
