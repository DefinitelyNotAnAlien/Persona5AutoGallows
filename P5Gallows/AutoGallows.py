#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
import warnings as warn
import cv2
import numpy as np
from PIL import ImageGrab

import sys
if sys.platform == 'win32':
    from .Win32Controls import press_button
    # For detecting the current location and size of the rpcs3 window
    from .WinUtils import WindowManager
else:
    raise NotImplementedError('This script currently only works on Windows.')


# Constants, Avoid changing these
STATS_BBOX = (0.56500,  # Relative location of the stats in the gallows
              0.65010,  # result screen as percentage of the game screen
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


# Controller settings
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


def auto_gallows(level_stats):
    """

    Args:
      level_stats(list): List containing the stats that you wish to level up
      the stats must be in order and only use the first two letters e.g.:
      ['st', 'ma']
    """
    win_mgr = WindowManager()
    win_mgr.find_window('Persona 5')
    win_bbox = win_mgr.get_window_rect()
    win_mgr.show_window()
    sleep(0.1)
    while True:
        press_button(CONTROLS['CROSS'])
        sleep(1.1)
        game_screen = ImageGrab.grab(win_bbox)
        level_up = detect_stats(game_screen)
        print(level_up)
        if level_stats == level_up:
            break
        press_button(CONTROLS['CIRCLE'])


if __name__ == '__main__':
    stats_to_level = ['ma', 'en', 'ag']
    auto_gallows(stats_to_level)
