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
    from .Win32Controls import press_button
    # For detecting the current location and size of the rpcs3 window
    from .WinUtils import WindowManager
else:
    raise NotImplementedError('This script currently only works on Windows.')


# Constants, Avoid changing these
STATS_BBOX = (0.55990,  # Relative location of the stats in the gallows
              0.64815,  # result screen as percentage of the game screen
              0.58854,  # x0, y0, xf, yf
              0.87037)
STATS_REL_LOC = (  # Relative location of the stats in the stat bbox
        # All stats can be fitted to a single bbox (x0, y0, xf, yf)
        ('st', (0, 0, 1, 0.16667)),
        ('ma', (0, 0.20833, 1, 0.375)),
        ('en', (0, 0.41667, 1, 0.58334)),
        ('ag', (0, 0.625, 1, 0.79167)),
        ('lu', (0, 0.83333, 1, 1))
        )


# Settings
CONTROLS = {
        'TRIANGLE': 'num8',
        'SQUARE': 'num4',
        'CIRCLE': 'num6',
        'CROSS': 'num5',
        }


def detect_stats(screenshot):
    """Detect the highlighted stats in the Gallows result screen.

    Args:
      screenshot(PIL.Image): An Image object containing the result screen.
    
    Returns:
      lvl_stats(list): A list of strings, where each string is the name of a
      highlighted stat (can be empty).
    """
    stats = []
    width, height = screenshot.size
    cropped_bbox = (int(width * STATS_BBOX[0]),
                    int(height * STATS_BBOX[1]),
                    int(width * STATS_BBOX[2]),
                    int(height * STATS_BBOX[3]))
    stats_crop = screenshot.crop(cropped_bbox)
    stats_width, stats_height = stats_crop.size
    stats_arr = np.array(stats_crop)
    hsv_stats = cv2.cvtColor(stats_arr, cv2.COLOR_RGB2HSV)
    # Detect stats in yellow i.e. highlight stats
    msk_stats = cv2.inRange(hsv_stats, (15, 10, 0), (30, 255, 255))
    for stat, bbox in STATS_REL_LOC:
        # Get the array indices for each bbox
        stat_bbox = (int(stats_width * bbox[0]),
                     int(stats_height * bbox[1]),
                     int(stats_width * bbox[2]),
                     int(stats_height * bbox[3]))
        array = msk_stats[stat_bbox[1]:stat_bbox[3],
                          stat_bbox[0]:stat_bbox[2]] 
        # cv2.imshow(stat, array);cv2.waitKey();cv2.destroyAllWindows()
        level_up = (array == 255).any()
        if level_up:
            stats.append(stat)
    return stats


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
