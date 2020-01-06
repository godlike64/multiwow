#!/usr/bin/env python3

from pynput import mouse
import logging

from multiwow.utils import run_cmd

class MouseListener:
    """Class to handle mouse events
    
    Window IDs are received from the KeyboardListener. There might be some 
    leftover functions from when I was trying to also propagate mouse moves and 
    dragging as well as clicks. This did not make sense so they will be removed.
    """
    
    def __init__(self, ids):
        self.logger = logging.getLogger('multiwow')
        self.cx, self.cy = (None, None)
        self.left_pressed = False
        self.right_pressed = False
        self.ids = ids
        self.broadcast = True
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )
        
    def send_click(self):
        """Send left button click to slave windows."""
        for id in self.ids:
            if self.broadcast:
                self.logger.debug(f'Sending click to {id}')
                run_cmd(f'xdotool click --window {id} 1')

    def on_move(self, x, y):
        """Do nothing. Successfully."""
        if self.left_pressed:
            pass
    
    def on_click(self, x, y, button, pressed):
        """Handle on_click events from the listener."""
        if not pressed:
            self.send_click()

    def on_scroll(self, x, y, dx, dy):
        """Do nothing. Successfully."""
        pass
