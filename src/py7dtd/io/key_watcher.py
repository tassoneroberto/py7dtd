#!/usr/bin/env python3

from pyWinhook import HookManager
from win32gui import PumpMessages, PostQuitMessage
import logging

logging.getLogger(__name__)

logging.root.setLevel(logging.INFO)


class KeyWatcher(object):
    def __init__(self, stop_func):
        self.stop_func = stop_func
        self.hm = HookManager()
        self.hm.KeyDown = self.on_keyboard_event
        self.hm.HookKeyboard()

    def on_keyboard_event(self, event):
        try:
            if event.KeyID == 27:
                logging.info("ESC key pressed. Stopping...")
                self.stop_func()
                self.shutdown()
        finally:
            return True

    def start(self):
        PumpMessages()

    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()
        logging.info("Key watcher stopped")
