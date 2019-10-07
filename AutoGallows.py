#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
import warnings as warn
import cv2
import numpy as np
from mss import mss
from PIL import Image

import sys
if sys.platform == 'win32':
    from Win32Controls import press_button
    try:
        # For detecting the current location and size of the rpcs3 window
        from WinUtils import WindowManager
        FIND_WIN = True
    except ImportError:
        FIND_WIN = False
        warn.warn('Window detection is disabled! You must set the emulator '
                  'window\'s coordinates. Also you\'ll need to switch to the '
                  'emulator window manually.', ImportWarning)

else:
    raise NotImplementedError('This script currently only works on Windows.')


# Constants, Avoid changing these
STATS_BBOX = (0.55990, 0.64815, 0.58854, 0.87037)  # bbox containing all stats
                                                   # as percentage of screen
STATS_REL_LOC = {  # Relative location of the stats in gallows result screen
        'strength': {'x0': 0, 'y0': 0, 'xf': 1, 'yf': 0.16667},
        'magic': {'x0': 0, 'y0': 0.20833, 'xf': 1, 'yf': 0.375},
        'endurance': {'x0': 0, 'y0': 0.41667, 'xf': 1, 'yf': 0.58333},
        'agility': {'x0': 0, 'y0': 0.625, 'xf': 1, 'yf': 0.79167},
        'luck': {'x0': 0, 'y0': 0.83333, 'xf': 1, 'yf': 1},
        }
# Settings
CONTROLS = {
        'TRIANGLE': 'num8',
        'SQUARE': 'num4',
        'CIRCLE': 'num6',
        'CROSS': 'num5',
        }
STATS_ABS_LOC = {  # Set the coordinates of the stats in the screen
        'strength': {'x0': 1075, 'y0': 700, 'xf': 1130, 'yf': 740},
        'magic': {'x0': 1080, 'y0': 750, 'xf': 1130, 'yf': 790},
        'endurance': {'x0': 1080, 'y0': 800, 'xf': 1130, 'yf': 840},
        'agility': {'x0': 1080, 'y0': 850, 'xf': 1130, 'yf': 890},
        'luck': {'x0': 1080, 'y0': 900, 'xf': 1130, 'yf': 940},
        }


def auto_gallows(level_stats=None):
    if FIND_WIN:
        win_mgr = WindowManager()
        win_mgr.find_window('Persona 5')
        win_x, win_y, win_width, win_height = win_mgr.get_window_rect()
        stats_bbox = (int(win_x + STATS_BBOX[0] * win_width),
                      int(win_y + STATS_BBOX[1] * win_height),
                      int(win_x + STATS_BBOX[2] * win_width),
                      int(win_y + STATS_BBOX[3] * win_height))
        bbox_width = stats_bbox[2] - stats_bbox[0]
        bbox_height = stats_bbox[3] - stats_bbox[1]
        stats = {}
        for k, v in STATS_REL_LOC.items():
            # Use the relative location of the stats with the window's size to
            # find the location for the current stats
            stats[k] = {'x0': int(v['x0']*bbox_width),
                        'y0': int(v['y0']*bbox_height),
                        'xf': int(v['xf']*bbox_width) - 1,
                        'yf': int(v['yf']*bbox_height) - 1,
                        'level_up': False}
        win_mgr.show_window()
    else:
        stats = STATS_ABS_LOC

    while True:
        press_button(CONTROLS['CROSS'])
        sleep(5)
        with mss() as sct:
            monitor = {"top": stats_bbox[1], "left": stats_bbox[0],
                       "width": bbox_width, "height": bbox_height}
            sct_img = sct.grab(monitor)
            img = np.array(Image.frombytes('RGB', sct_img.size,
                                           sct_img.bgra,
                                           'raw', 'BGRX'))
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, (15, 10, 0), (30, 255, 255))
        for stat, val in stats.items():
            if (mask[val['y0']:val['yf'], val['x0']:val['xf']] != 0).any():
                val['level_up'] = True
            else:
                val['level_up'] = False
        print([stat for stat, val in stats.items() if val['level_up']])
        cv2.imshow('screen', img);cv2.waitKey();cv2.destroyAllWindows()
        cv2.imshow('yellow', mask);cv2.waitKey();cv2.destroyAllWindows()
        press_button(CONTROLS['CIRCLE'])
        break
    # logic to detect highlighted (yellow) stats:
    # img = np.array(ImageGrab())
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # mask = cv2.inRange(hsv, (20, 10, 0), (21, 255, 180))
    # for stat, val in stats.items():
    #   if (mask[val['y0']:val['yf'], val['x0']:val['xf']] != 0).any():
    #       val['level_up'] = True
    #   else:
    #       val['level_up'] = False

if __name__ == '__main__':
    auto_gallows()
