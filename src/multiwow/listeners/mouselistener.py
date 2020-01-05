#!/usr/bin/env python3

from pynput import mouse
import logging

from multiwow.utils import run_cmd

class MouseListener:
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
        
    def get_mouse_location(self):
        result = subprocess.run(shlex.split('xdotool getmouselocation'), stdout=subprocess.PIPE)
        stdout = str(result.stdout).split(' ')
        x = stdout[0].split(':')[-1]
        y = stdout[1].split(':')[-1]
        return (x, y)
        
    def send_click(self):
        for id in self.ids:
            if self.broadcast:
                self.logger.debug(f'Sending click to {id}')
                run_cmd(f'xdotool click --window {id} 1')

    def on_move(self, x, y):
        if self.left_pressed:
            pass
    
    def on_click(self, x, y, button, pressed):
        if not pressed:
            self.send_click()

    def on_scroll(self, x, y, dx, dy):
        pass
