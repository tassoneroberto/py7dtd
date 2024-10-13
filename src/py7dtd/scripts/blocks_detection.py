#!/usr/bin/env python3

import argparse
import ctypes
import logging
import math
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
        else:
            self.output_filename = self.args.output

    def analyze(self):
        logging.info(f"Loading the image file at: {self.args.input}")
        image = Image.open(self.args.input)
        pixels = image.load()
        logging.info("Image loaded successfully!")
        progress_bar_manager = enlighten.get_manager()
        progress_bar = progress_bar_manager.counter(
            total=image.width, unit="lines"
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

    # def getDensity(x, y, z):
    #     densityTerrain = 0b00000000
    #     densityAir = 0b01111111
    # bytesPerVal = 1
    # num = (y >> 2) * bytesPerVal
    # if num < 0:
    #     return 0
    # # layers = [0b0 for _ in range(64 * bytesPerVal)]

    # int num = (_y >> 2) * bytesPerVal;
    # if (num < 0)
    # {
    # 	return 0L;
    # }
    # CBCLayer cBCLayer = layers[num];
    # if (cBCLayer == null)
    # {
    # 	return getSameValue(num);
    # }
    # int num2 = calcOffset(_x, _y, _z);
    # if (bytesPerVal == 1)
    # {
    # 	return cBCLayer.data[num2];
    # }
    # return (sbyte)getData(num, num2);

    return 1


def int_to_signed_short(value):
    return -(value & 0x8000) | (value & 0x7FFF)


def test():
    print("reading map.png")
    map_image = Image.open("./dev_test/map.png")
    width, height = map_image.size
    cropped_map_image = map_image.crop((32, 16, width - 16, height - 32))  # type: ignore

    w, h = cropped_map_image.size
    print(f"map size: {w}x{h}")

    print("reading dtm_processed.raw to get terrain height")
    terrainHeightMap = [[0 for col in range(w)] for row in range(h)]
    with open("./dev_test/dtm_processed.raw", "rb") as f:
        row = h - 1
        col = 0
        while bytes := f.read(2):
            terrainHeightMap[row][col] = int.from_bytes(
                bytes, byteorder="little", signed=False
            )
            col += 1
            if col == w:
                col = 0
                row -= 1

    print("computing terrain normal")
    terrainNormalMap = [[0 for col in range(w)] for row in range(h)]
    slopeMap = [[0 for col in range(w)] for row in range(h)]

    lhs = [0.0, 0.0, 1.0]
    rhs = [1.0, 0.0, 0.0]
    for col in range(w):  # i
        for row in range(h):  # j
            terrainHeight = terrainHeightMap[row][col]
            num = terrainHeightMap[row + 1][col]
            num2 = terrainHeightMap[row][col + 1]
            if terrainHeight >= 253 or num >= 253 or num2 >= 253:
                # TODO
                continue
            num3 = 1 / (-128.0)
            num4 = 1 / (-128.0)
            num5 = 1 / (-128.0)
            num6 = 1 / (127.0)
            num7 = 1 / (127.0)
            num8 = 1 / (127.0)
            if num3 > 0.999 and num6 > 0.999:
                num3 = 0.5
            if num4 > 0.999 and num7 > 0.999:
                num4 = 0.5
            if num5 > 0.999 and num8 > 0.999:
                num5 = 0.5
            num9 = terrainHeight + num3
            num10 = num + num4
            num11 = num2 + num5
            lhs[1] = num11 - num9
            rhs[1] = num10 - num9

            vector = [
                lhs[1] * rhs[2] - lhs[2] * rhs[1],
                lhs[2] * rhs[0] - lhs[0] * rhs[2],
                lhs[0] * rhs[1] - lhs[1] * rhs[0],
            ]
            length = math.sqrt(
                vector[0] * vector[0]
                + vector[1] * vector[1]
                + vector[2] * vector[2]
            )
            normalized = (
                [vector[0] / length, vector[1] / length, vector[2] / length]
                if length > 0.000001
                else [0, 0, 0]
            )
            terrainNormalMap[row][col] = normalized  # type: ignore

            if normalized[1] < 0.55:
                slopeMap[row][col] = 2  # steep
            elif normalized[1] < 0.65:
                slopeMap[row][col] = 1  # sloped

    print("computing map colors")
    mapColors = [[0 for col in range(w)] for row in range(h)]

    for col in range(w):  # i
        for row in range(h):  # j
            num2 = terrainHeightMap[row][col]  # type: ignore
            num3 = num2 >> 2
            col = [
                0b00000000,
                0b01101001,
                0b10010100,
                0b11111111,
            ]  # 0, 105, 148, 255

            num4 = ctypes.c_float((ctypes.c_byte(terrainNormalMap[row][col][0]).value / 127.0)).value  # type: ignore
            num5 = ctypes.c_float((ctypes.c_byte(terrainNormalMap[row][col][1]).value / 127.0)).value  # type: ignore
            num6 = ctypes.c_float((ctypes.c_byte(terrainNormalMap[row][col][2]).value / 127.0)).value  # type: ignore

            # col = blockValue.Block.GetMapColor(blockValue, new Vector3(num4, num5, num6), num2);

            # Color val = (bMapColorSet ? MapColor : ((!(_normal.x > 0.5f) && !(_normal.z > 0.5f) && !(_normal.x < -0.5f) && !(_normal.z < -0.5f)) ? GetColorForSide(_blockValue, BlockFace.Top) : GetColorForSide(_blockValue, BlockFace.South)));
            # float num = MapSpecular;
            # if (bMapColor2Set && MapElevMinMax.y != MapElevMinMax.x)
            # {
            #     float num2 = (float)Utils.FastMax(_yPos - MapElevMinMax.x, 0) / (float)(MapElevMinMax.y - MapElevMinMax.x);
            #     val = Color.Lerp(MapColor, MapColor2, num2);
            #     num = Utils.FastMax(num - num2 * 0.5f, 0f);
            # }
            # float num3 = (_normal.z + 1f) / 2f * (_normal.x + 1f) / 2f;
            # num3 *= 2f;
            # val = Utils.Saturate(val * 0.5f + val * num3);
            # val.a = num;
            # return val;

            finalized = ctypes.c_ushort(
                ((int)(col[0] * 31.0 + 0.5) << 10)
                | ((int)(col[1] * 31.0 + 0.5) << 5)
                | (int)(col[2] * 31.0 + 0.5)
            ).value

            mapColors[row][col] = finalized

    # <block name="terrTopSoil">
    # 	<property name="Extends" value="terrDirt" param1="DescriptionKey"/>
    # 	<property name="CreativeMode" value="Player"/>
    # 	<property name="CustomIcon" value="terrForestGround"/>
    # 	<property name="Texture" value="195"/>
    # 	<property name="SortOrder2" value="0650"/>
    # </block>

    # sample_row_1 = 3809
    # sample_col_1 = 3184
    # # sample_row_1 = 0
    # # sample_col_1 = 0
    # sample_row_2 = sample_row_1 + 5
    # sample_col_2 = sample_col_1 + 5

    # print("show sample")
    # sample = cropped_map_image.crop((sample_col_1, sample_row_1, sample_col_2, sample_row_2)) # type: ignore
    # sample.show()

    # map_image_pixels = cropped_map_image.load()

    # print("sample map:")
    # for row in range(sample_row_1, sample_row_2):
    #     for col in range(sample_col_1, sample_col_2):
    #         print(map_image_pixels[col, row], end='\t') # type: ignore
    #     print()

    # print("sample raw:")
    # for row in range(sample_row_1, sample_row_2):
    #     for col in range(sample_col_1, sample_col_2):
    #         print(terrainHeightMap[row][col], end='\t')
    #     print()

    return


def main():

    test()
    return

    parser = get_argument_parser()
    args = parser.parse_args()

    blocks_detection = BlocksDetection(args)
    blocks_detection.analyze()


if __name__ == "__main__":
    main()
