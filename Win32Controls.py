#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reduced version of pyautogui_win by Al Sweigart"""
import ctypes
from ctypes import wintypes
from time import sleep


user32 = ctypes.WinDLL('user32', use_last_error=True)


INPUT_KEYBOARD = 1


KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0003
KEYEVENTF_SCANCODE = 0x0004
MAPVK_VK_TO_VSC = 0

# Virtual key constants
# msdn.microsoft.com/en-us/library/dd375731
VK_CONST = {
        'backspace': 0x08,  # Backspace
        'tab': 0x09,  # Tab
        'num0': 0x60,  # VK_NUMPAD0
        'num1': 0x61,  # VK_NUMPAD1
        'num2': 0x62,  # VK_NUMPAD2
        'num3': 0x63,  # VK_NUMPAD3
        'num4': 0x64,  # VK_NUMPAD4
        'num5': 0x65,  # VK_NUMPAD5
        'num6': 0x66,  # VK_NUMPAD6
        'num7': 0x67,  # VK_NUMPAD7
        'num8': 0x68,  # VK_NUMPAD8
        'num9': 0x69,  # VK_NUMPAD9
        'lshift': 0xa0,  # VK_LSHIFT
        'rshift': 0xa1,  # VK_RSHIFT
        'lctrl': 0xa2,  # VK_LCONTROL
        'rctrl': 0xa3,  # VK_RCONTROL
        'lalt': 0xa4,  # VK_LMENU
        'ralt': 0xa5,  # VK_RMENU
        }
for c in range(32, 128):
    VK_CONST[chr(c)] = ctypes.windll.user32.VkKeyScanA(ctypes.wintypes.WCHAR(chr(c)))


# C structure definitions
wintypes.ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):

    _fields_ = (('dx', wintypes.LONG),
                ('dy', wintypes.LONG),
                ('mouseData', wintypes.DWORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):

    _fields_ = (('wVk', wintypes.WORD),
                ('wScan', wintypes.WORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR))

    def __init__(self, *args, **kwargs):
        """Fix scan code."""
        super(KEYBDINPUT, self).__init__(*args, **kwargs)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):

    _fields_ = (('uMsg', wintypes.DWORD),
                ('wParamL', wintypes.WORD),
                ('wParamH', wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (('ki', KEYBDINPUT),
                    ('mi', MOUSEINPUT),
                    ('hi', HARDWAREINPUT)
                    )

    _anonymous_ = ('_input',)
    _fields_ = (('type', wintypes.DWORD),
                ('_input', _INPUT))


LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args


user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT,  # nInputs
                             LPINPUT,  # pInputs
                             ctypes.c_int)  # cbSize


def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def press_button(button, wait=0.2):
    PressKey(VK_CONST[button])
    sleep(wait)
    ReleaseKey(VK_CONST[button])
