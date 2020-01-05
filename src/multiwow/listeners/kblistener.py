
from pynput import keyboard
import termios
import sys
import logging

from multiwow.listeners.mouselistener import MouseListener
from multiwow.utils import get_window_ids, get_vd_window_ids, run_cmd


class KeyboardListener:
    def __init__(self, config):
        self.logger = logging.getLogger('multiwow')
        self.config = config.cp
        self.modifier = ''
        self.p_map = []
        self.arrows = ['Up', 'Down', 'Left', 'Right']
        self.s_map = {
            'space': 'space',
            'ctrl': 'Control_L',
            'alt': 'Alt_L',
            'esc': 'Escape',
            'tab': 'Tab',
            'shift': 'Shift_L',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right',
            'enter': 'KP_Enter',
            'cmd': 'super',
            '`': 'asciitilde',
        }
        self.ids = get_window_ids(self.config['commands']['window ids'], self.config['commands']['slave windows'])
        self.comb = ['Control_L', 'Alt_L', 'Shift_L', 'super']
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
        )
        self.build_window_list()
        self.wl = self.build_window_list()
        self.broadcast = True
        self.clear_modifiers()
        self.toggle_echo(False)
        self.ml = MouseListener(self.ids)
        
    def start(self):
        self.ml.listener.start()
        self.logger.debug(f'Identified slave windows: {self.ids}')
        self.join()
        
    def join(self):
        with self.listener as listener:
            listener.join()
    
    def build_window_list(self):
        main = get_vd_window_ids(name=self.config['commands']['master window'])
        slaves = get_vd_window_ids(name=self.config['commands']['slave windows'])
        main.extend(slaves)
        return main

    def get_current_focus(self):
        result = run_cmd(f'xdotool getwindowfocus')
        id = int(result.stdout.decode('utf-8').split('\n')[0])
        self.logger.debug(f'Current focus is on window: {id}')
        if id in self.wl:
            return self.wl.index(id)
        else:
            self.logger.warning(f'Current focus is not on any window, '
                                'defaulting to focus on master.')
            return 0
    
    def next_window(self):
        self.logger.debug(f'Running next_window')
        index = self.get_current_focus()
        index = index+1 if (index+1) < len(self.wl) else 0
        if len(self.wl) == 0:
            self.logger.warning(f'Window list is empty. Doing nothing.')
            return
        id = self.wl[index]
        self.logger.debug(f'Focusing on {id}')
        run_cmd(f'xdotool windowactivate {id}')
        
    def toggle_echo(self, enabled, fd=sys.stdout.fileno()):
        self.logger.debug(f'Switching echo to {enabled}')
        (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)
        if enabled:
            lflag |= termios.ECHO
        else:
            lflag &= ~termios.ECHO
        
        new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)
        if enabled == True:
            termios.tcflush(fd, termios.TCIOFLUSH)

    def clear_modifiers(self):
        self.logger.debug(f'Clearing modifiers to avoid issues.')
        master_ids = get_window_ids(self.config['commands']['window ids'], self.config['commands']['master window'])
        slave_ids = get_window_ids(self.config['commands']['window ids'], self.config['commands']['slave windows'])
        for char in self.comb:
            self.send_keyup(char, master_ids)
            self.send_keyup(char, slave_ids)
        for char in self.arrows:
            self.send_keyup(char, master_ids)
            self.send_keyup(char, slave_ids)
            
    def on_press(self, key):
        char = self.process_key(key)
        if char:
            if char == self.config['keys']['stop program']:
                # Stop listener
                self.logger.info('Escape key detected. Stopping normally.')
                self.toggle_echo(True)
                self.ml.listener.stop()
                return False
            if char in self.arrows:
                self.logger.debug(f'Ignoring keypress of arrow {char}')
                return
            if char in self.comb:
                self.logger.debug(f'Adding {char} to modifier list.')
                self.modifier = f'{char}+'
            if char not in self.p_map:
                self.logger.debug(f'{char} pressed - current P_MAP: {self.p_map}')
                self.p_map.append(char)
                self.send_keydown(char, self.ids)

    def on_release(self, key):
        char = self.process_key(key)
        if char:
            if char in self.comb:
                self.logger.debug(f'Removing {char} and all modifiers from modifier list.')
                self.modifier = ''
            self.logger.debug(f'{char} released - current P_MAP: {self.p_map}')
            if char in self.p_map:
                self.p_map.remove(char)
                self.send_keyup(char, self.ids)
        

    def send_keydown(self, char, ids):
        if f'{self.modifier}{char}' == self.config['keys']['start broadcast']:
            self.logger.debug(f'Broadcast started')
            self.clear_modifiers()
            self.broadcast = True
            self.ml.broadcast = True
            return
        if char in self.arrows:
            self.logger.debug(f'Ignoring keydown of arrow {char}')
        if f'{self.modifier}{char}' == self.config['keys']['next window']:
            self.clear_modifiers()
            self.next_window()
            return
        for id in ids:
            if self.broadcast or f'{char}' == f'f':
                self.logger.debug(f'Sending keydown {char} to {id}')

                run_cmd(f'xdotool keydown --window {id} {self.modifier}{char}')
        if f'{char}' == f'f':
            self.send_keyup(char, ids)

    def send_keyup(self, char, ids):
        for id in ids:
            if self.broadcast:
                self.logger.debug(f'Sending keyup {char} to {id}')
                run_cmd(f'xdotool keyup --window {id} {self.modifier}{char}')
        if f'{char}' == self.config['keys']['stop broadcast']:
            self.clear_modifiers()
            if self.broadcast:
                self.broadcast = False
                self.ml.broadcast = False
                self.logger.debug(f'Broadcast stopped')


    def process_key(self, key):
        if hasattr(key, 'char'):
            if key.char == '`' or key.char == '~':
                return self.s_map['`']
            return key.char
        elif key.name in self.s_map:
            return self.s_map[key.name]
        else:
            return None


