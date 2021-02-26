#!/usr/bin/env python3

import ctypes

import win32api
import win32con

SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]


def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def MoveMouseAbsolute(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    x = int(x * (65536 / ctypes.windll.user32.GetSystemMetrics(0)) + 1)
    y = int(y * (65536 / ctypes.windll.user32.GetSystemMetrics(1)) + 1)
    ii_.mi = MouseInput(x, y, 0, 0x0001 | 0x8000, 1, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def MoveMouseRel(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x), int(y), 0, 0)


def LeftMouseClick():
    ctypes.windll.user32.mouse_event(
        0x2, 0, 0, 0, 0
    )  # Mouse LClick Down, relative coords, dx=0, dy=0
    ctypes.windll.user32.mouse_event(
        0x4, 0, 0, 0, 0
    )  # Mouse LClick Up, relative coords, dx=0, dy=0


def RightMouseClick():
    ctypes.windll.user32.mouse_event(
        0x8, 0, 0, 0, 0
    )  # Mouse RClick Down, relative coords, dx=0, dy=0
    ctypes.windll.user32.mouse_event(
        0x10, 0, 0, 0, 0
    )  # Mouse RClick Up, relative coords, dx=0, dy=0


def MiddleMouseClick():
    ctypes.windll.user32.mouse_event(
        0x20, 0, 0, 0, 0
    )  # Mouse MClick Down, relative coords, dx=0, dy=0
    ctypes.windll.user32.mouse_event(
        0x40, 0, 0, 0, 0
    )  # Mouse MClick Up, relative coords, dx=0, dy=0


# directx scan codes http://www.gamespp.com/directx/directInputKeyboardScanCodes.html
