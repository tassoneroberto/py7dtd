#!/usr/bin/env python3

import argparse
import fileinput
import importlib.resources as pkg_resources
import logging
import string
import time
from ctypes import windll
from itertools import product

import win32com.client as comclt
import win32gui
from py7dtd.io.commands_controller import MoveMouseAbsolute, RightMouseClick

logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", default=None, help="Maximum number of tries", type=int
    )
    parser.add_argument(
        "--brute",
        default=False,
        help="Bruteforce attack (default method)",
        action="store_true",
    )
    parser.add_argument(
        "--min", default=1, help="Minimum length (default = 1)", type=int
    )
    parser.add_argument(
        "--max", default=20, help="Maximum length (default = 20)", type=int
    )
    parser.add_argument(
        "--delay",
        default=50,
        help="Delay in ms between each try (default = 50)",
        type=int,
    )
    parser.add_argument(
        "--dict", default=False, help="Dictionary attack", action="store_true"
    )
    parser.add_argument("--dictpath", help="Dictionary file path", type=str)

    args = parser.parse_args()

    if args.brute and args.dict:
        logging.error(
            "Error: only a method can be selected. Available are: `brute`, `dict`."
        )
        exit()

    if args.dict and not args.dictpath:
        logging.error("Error: a dictionary must be selected.")
        exit()

    if not args.brute and not args.dict:
        logging.warning(
            "Warning: a method has not been selected. Available are: `brute`, `dict`.\n`brute` has been selected by default."
        )
        args.brute = True

    # Select the application window
    wsh = comclt.Dispatch("WScript.Shell")
    wsh.AppActivate("7 Days To Die")
    hwnd = win32gui.FindWindow(None, r"7 Days to Die")
    win32gui.SetForegroundWindow(hwnd)
    dimensions = win32gui.GetWindowRect(hwnd)

    # Center the mouse
    pointer_center = [
        (dimensions[2] - dimensions[0]) // 2 + dimensions[0],
        (dimensions[3] - dimensions[1]) // 2 + dimensions[1] + 20,
    ]
    MoveMouseAbsolute(pointer_center[0], pointer_center[1])

    tries = 0
    delay = args.delay / 1000

    if args.brute:
        allowed_chars = string.ascii_letters + string.digits

        for length in range(args.min, args.max + 1):
            to_attempt = product(allowed_chars, repeat=length)

            for attempt in to_attempt:
                time.sleep(delay)
                RightMouseClick()
                time.sleep(delay)
                wsh.SendKeys("".join(attempt))
                time.sleep(delay)
                wsh.SendKeys("~")
                time.sleep(delay)

                tries += 1
                if args.limit and tries >= args.limit:
                    exit()

    if args.dict:
        with open(args.dictpath, "r") as dict_file:
            for line in dict_file:
                RightMouseClick()
                time.sleep(delay)
                wsh.SendKeys(line.strip())
                time.sleep(delay)
                wsh.SendKeys("~")
                time.sleep(delay)

                tries += 1
                if args.limit and tries >= args.limit:
                    exit()


if __name__ == "__main__":
    main()
