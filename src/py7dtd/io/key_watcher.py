#!/usr/bin/env python3

import logging

from pyWinhook import HookManager
from win32gui import PostQuitMessage, PumpMessages

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


class KeyWatcher(object):
    def __init__(self, stop_func, p_func=None) -> None:
        self.stop_func = stop_func
        self.p_func = p_func
        self.hm = HookManager()
        self.hm.KeyDown = self.on_keyboard_event
        self.hm.HookKeyboard()

    def on_keyboard_event(self, event) -> bool:
        try:
            if event.KeyID == 27:  # `ESC` key
                logging.info("ESC key pressed. Stopping...")
                self.stop_func()
                self.shutdown()
            elif self.p_func and event.KeyID == 80:  # `p` key
                self.p_func()
        except Exception as err:
            logging.error(str(err))
        finally:
            return True

    def start(self) -> None:
        PumpMessages()

    def shutdown(self) -> None:
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()
        logging.info("Key watcher stopped")
