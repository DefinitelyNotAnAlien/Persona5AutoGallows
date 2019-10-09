#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings as warn
try:
    import win32gui
except ImportError:
    raise ImportError('win32api is required for the script to work, install '
                      'it with pip install pywin32')

class NoSelectedWindow(Exception):
    pass


class WindowManager():
    """Wrapper for several Win32 api functions for windows.

    * attribs:
        selected_window: stores the window handle for the selected window
    * methods:
        * find_window: searches all the open windows and searches for one
        with a window title that includes the indicated substring, sets
        selected_window.
        * get_window_rect: gets the rectangle box for the selected window,
        returns the following values in 
            window origin as a tuple (x origin, y origin),
            window width, window height
        * show_window: shows the window and brings it to the foreground (i.e.
        the front of the screen)
    """
    selected_window = None

    def __find_window_callback(self, win_hndl, substr):
        # prevent callback from changing the selected_window handle after if
        # a window has already been found. Since the only moment when
        # selected_window can be None is when find_window is called
        if self.selected_window is not None:
            return
        if substr in win32gui.GetWindowText(win_hndl):
            self.selected_window = win_hndl

    def find_window(self, title_substr):
        """Search for a window containing a substring in it's title."""
        self.selected_window = None
        win32gui.EnumWindows(self.__find_window_callback, title_substr)
        # if callback doesn't find the window, selected_window stays as None
        if self.selected_window is None:
            warn.warn('No windows with the indicated title were found, try '
                      'searching with a different keyword.')

    def get_window_rect(self):
        """Returns the window's boundary box."""
        if self.selected_window is None:
            raise NoSelectedWindow('No window has been selected, call '
                                   'find_window first')
        return win32gui.GetWindowRect(self.selected_window)

    def show_window(self):
        """Shows the window and brings it to the foreground."""
        win32gui.ShowWindow(self.selected_window, 5)
        win32gui.SetForegroundWindow(self.selected_window)
