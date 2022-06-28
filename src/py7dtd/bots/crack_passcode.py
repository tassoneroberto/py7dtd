#!/usr/bin/env python3

import argparse
import logging
import string
import threading
import time
from itertools import product

import win32com.client as comclt
from PIL import ImageGrab
from py7dtd.io.commands_controller import MoveMouseAbsolute, RightMouseClick
from py7dtd.io.key_watcher import KeyWatcher
from py7dtd.io.window_handler import get_absolute_window_center, select_window

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class CrackPasscode(object):
    def __init__(self, args):
        self.stopped = False
        self.args = args
        self.init_args()

    def init_args(self):
        if self.args.brute and self.args.dict:
            logging.error(
                "Error: only one method can be selected."
                + "Available are: `brute`, `dict`."
            )
            exit()

        if self.args.dict and not self.args.dictpath:
            logging.error("Error: a dictionary must be selected.")
            exit()

        if not self.args.brute and not self.args.dict:
            logging.warning(
                "Warning: a method has not been selected."
                + "Available are: `brute`, `dict`."
                + "`brute` has been selected by default."
            )
            self.args.brute = True

        self.delay = self.args.delay / 1000

    def watch_keys(self):
        self.watcher = KeyWatcher(stop_func=self.stop)
        self.watcher.start()

    def start(self):
        # Select the application window
        try:
            self.dimensions = select_window()
        except Exception as err:
            logging.error(str(err))
            return
        self.pointer_center = get_absolute_window_center(self.dimensions)
        MoveMouseAbsolute(self.pointer_center[0], self.pointer_center[1])

        # Spawn the keywatcher thread
        self.watcher_thread = threading.Thread(target=self.watch_keys, args=())
        # Daemon = True -> kill it when main thread terminates
        self.watcher_thread.setDaemon(True)
        self.watcher_thread.start()

        # Init win32com to inject keys
        self.wsh = comclt.Dispatch("WScript.Shell")
        self.wsh.AppActivate("7 Days To Die")

        self.tries = 0
        self.start_time = time.time()

        if self.args.brute:
            self.crack_brute()

        if self.args.dict:
            self.crack_dict()

        logging.info("Crack passcode stopped")

    def crack_brute(self):
        allowed_chars = []
        if self.args.digits:
            allowed_chars += string.digits
        if self.args.lower:
            allowed_chars += string.ascii_lowercase
        if self.args.upper:
            allowed_chars += string.ascii_uppercase
        if self.args.special:
            allowed_chars += string.punctuation
            # FIXME: the following characters can not be sent
            # https://github.com/tassoneroberto/py7dtd/issues/17
            allowed_chars.remove("(")
            allowed_chars.remove(")")
            allowed_chars.remove("{")
            allowed_chars.remove("}")
            allowed_chars.remove("~")

        if allowed_chars.count == 0:
            logging.error(
                "Error: empty characters set."
                + "Please specify at least one of: "
                + "[digits, lower, upper, special]"
            )
            return

        for length in range(self.args.min, self.args.max + 1):
            to_attempt = product(allowed_chars, repeat=length)

            for attempt in to_attempt:
                self.inject_string("".join(attempt))
                if self.check_stopped():
                    return

    def crack_dict(self):
        with open(self.args.dictpath, "r") as dict_file:
            for line in dict_file:
                self.inject_string(line.strip())
                if self.check_stopped():
                    return

    def inject_string(self, attempt):
        time.sleep(self.delay)
        RightMouseClick()
        time.sleep(self.delay)
        self.wsh.SendKeys(attempt)
        time.sleep(self.delay)
        self.wsh.SendKeys("~")
        time.sleep(self.delay)

        if self.passcode_found():
            logging.info("Passcode found: " + attempt)
            self.stop()
        else:
            self.tries += 1

    def stop(self):
        self.stopped = True

    def passcode_found(self):
        image = ImageGrab.grab(
            (
                self.pointer_center[0],
                self.pointer_center[1] + 6,
                self.pointer_center[0] + 1,
                self.pointer_center[1] + 7,
            )
        )
        pixel_color = image.getcolors()[0][1]
        return pixel_color != (96, 96, 96)

    def check_stopped(self):
        if self.args.limit and self.tries >= self.args.limit:
            logging.info(
                "Max tries reached (" + str(self.args.limit) + "). Stopping..."
            )
            self.key_watcher.shutdown()
            return True
        if (
            self.args.timeout
            and time.time() - self.start_time >= self.args.timeout
        ):
            logging.info(
                "Timeout (" + str(self.args.timeout) + "s). Stopping..."
            )
            self.key_watcher.shutdown()
            return True
        if self.stopped:
            return True


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", default=None, help="Maximum number of tries", type=int
    )
    parser.add_argument(
        "--timeout",
        default=None,
        help="Maximum time (in seconds) allowed to the script to run",
        type=int,
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
        "--digits", default=False, help="Include digits", action="store_true"
    )
    parser.add_argument(
        "--lower",
        default=False,
        help="Include lowercase characters",
        action="store_true",
    )
    parser.add_argument(
        "--upper",
        default=False,
        help="Include uppercase characters",
        action="store_true",
    )
    parser.add_argument(
        "--special",
        default=False,
        help="Include special characters",
        action="store_true",
    )
    parser.add_argument(
        "--delay",
        default=50,
        help="Delay in ms between each mouse/keyboard action (default = 50)",
        type=int,
    )
    parser.add_argument(
        "--dict", default=False, help="Dictionary attack", action="store_true"
    )
    parser.add_argument(
        "--dictpath",
        default="./dictionaries/top1000.txt",
        help="Dictionary file path",
        type=str,
    )

    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    crack_passcode = CrackPasscode(args)
    crack_passcode.start()

    logging.info("Process terminated.")


if __name__ == "__main__":
    main()
