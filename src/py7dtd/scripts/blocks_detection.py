#!/usr/bin/env python3

import argparse
import logging
import os

import enlighten
import filetype
from PIL import Image

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class BlocksDetection(object):
    def __init__(self, args):
        self.args = args
        self.init_args()

    def init_args(self):
        if (
            not self.args.topsoil
            and not self.args.dirt
            and not self.args.destroyed_stone
            and not self.args.gravel
        ):
            logging.error(
                "Error: No blocks selected."
                + " Select at least one of: [`topsoil`, `dirt`, `gravel`, `destroyed_stone`]."
            )
            exit()

        if not self.args.input:
            logging.error("Error: please provide a map as input.")
            exit()
        elif not os.path.exists(self.args.input):
            logging.error("Error: the provided input file does not exists.")
            exit()
        elif not filetype.is_image(self.args.input):
            logging.error("Error: the provided input file format is invalid.")
            exit()

        if not self.args.output:
            self.output_filename = (
                os.path.splitext(self.args.input)[0] + "_output.png"
            )

    def analyze(self):
        logging.info(f"Loading the image file at: {self.args.input}")
        image = Image.open(self.args.input)
        pixels = image.load()
        logging.info("Image loaded successfully!")
        progress_bar_manager = enlighten.get_manager()
        progress_bar = progress_bar_manager.counter(
            total=image.width, desc="Processing", unit="lines"
        )
        for x in range(0, image.width):
            progress_bar.update()
            for y in range(0, image.height):
                pixel = pixels[x, y]  # type: ignore

                if pixel == (0, 0, 0, 255):
                    # Black pixel
                    continue

                if (
                    (
                        self.args.destroyed_stone
                        and pixel == (148, 148, 66, 255)
                    )
                    or (
                        (self.args.topsoil or self.args.dirt)
                        and pixel == (16, 49, 24, 255)
                    )
                    or (self.args.gravel and pixel == (156, 140, 123, 255))
                ):
                    pixels[x, y] = (255, 0, 0, 255)  # type: ignore
                    continue

        progress_bar.close()
        progress_bar_manager.stop()
        logging.info("\n")

        logging.info(f"Saving output image at: {self.output_filename}")
        image.save(self.output_filename)
        logging.info(f"Successfully saved!")


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topsoil",
        default=False,
        help="Detect topsoil blocks",
        action="store_true",
    )
    parser.add_argument(
        "--dirt",
        default=False,
        help="Detect dirt blocks",
        action="store_true",
    )
    parser.add_argument(
        "--gravel",
        default=False,
        help="Detect gravel blocks",
        action="store_true",
    )
    parser.add_argument(
        "--destroyed_stone",
        default=False,
        help="Detect destroyed stone blocks",
        action="store_true",
    )
    parser.add_argument("--input", help="Raw map image file path", type=str)
    parser.add_argument(
        "--output", help="Map with detected blocks output file path", type=str
    )
    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    blocks_detection = BlocksDetection(args)
    blocks_detection.analyze()


if __name__ == "__main__":
    main()
