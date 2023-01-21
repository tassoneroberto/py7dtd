#!/usr/bin/env python3

import logging

import win32gui

logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)


def select_window(window_name):
    logging.info(f"Detecting {window_name}...")
    hwnd = win32gui.FindWindow(None, r"{}".format(window_name))
    if hwnd == 0:
        raise Exception(f"Application {window_name} not detected.")
    win32gui.SetForegroundWindow(hwnd)
    dimensions = win32gui.GetWindowRect(hwnd)
    width = dimensions[2] - dimensions[0]
    height = dimensions[3] - dimensions[1]
    logging.info(
        f"Application {window_name} detected successfully. Window size: [{width}x{height}]"
    )
    return dimensions


def get_relative_window_center(dimensions):
    return [
        (dimensions[2] - dimensions[0]) // 2,
        (dimensions[3] - dimensions[1]) // 2,
    ]


def get_absolute_window_center(dimensions):
    return [
        (dimensions[2] - dimensions[0]) // 2 + dimensions[0],
        (dimensions[3] - dimensions[1]) // 2 + dimensions[1] + 20,
    ]
