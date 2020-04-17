
from pynput import keyboard
import termios
import sys
import logging

from multiwow.listeners.mouselistener import MouseListener
from multiwow.utils import get_window_ids, get_vd_window_ids, run_cmd


class KeyboardListener:
    """Class to handle keyboard events
    
    Apart from handling keyboard events, this class also makes use of 
    get_window_ids / get_vd_window_ids. Additionally, it also creates the mouse 
    listener object.
    """
    
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
        """Start the listener and block until exit."""
        self.ml.listener.start()
        self.logger.debug(f'Identified slave windows: {self.ids}')
        self.join()
        
    def join(self):
        """Join the listener so the program does not exit prematurely."""
        with self.listener as listener:
            listener.join()
    
    def build_window_list(self):
        """Generate the window list to work on."""
        main = get_vd_window_ids(name=self.config['commands']['master window'])
        slaves = get_vd_window_ids(name=self.config['commands']['slave windows'])
        main.extend(slaves)
        return main

    def get_current_focus(self):
        """Get the currently focused window index in the window list.
        
        If no valid window is focused, the master (first) window is focused 
        to prevent an error or spurious behaviour.
        """
        result = run_cmd(f'xdotool getwindowfocus')
        id = int(result.stdout.decode('utf-8').split('\n')[0])
        self.logger.debug(f'Current focus is on window: {id}')
        if id in self.wl:
            return self.wl.index(id)
        else:
            self.logger.warning(f'Current focus is not on any window.')
            return -1
    
    def next_window(self):
        """Switch to the next window in the list."""
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
        """Enable/disable echo in the terminal.
        
        This was added for testing, so that the echo of the keystrokes do not 
        show up in the terminal if the terminal is the currently focused window.
        Echo is disabled on program start and enabled again when exiting, but 
        only if the program exited cleanly and did not crash.
        """
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
        """Helper method to clear modifiers on all windows.
        
        Sometimes modifier keys get stuck, especially when switching windows. 
        This tries to avoid it. Also, all modifiers are cleared on startup and 
        under certain conditions, preemptively.
        """
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
        """Handle key presses."""
        char = self.process_key(key)
        if char and self.get_current_focus() != -1:
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
        """Handle key releases."""
        char = self.process_key(key)
        if char and self.get_current_focus() != -1:
            if char in self.comb:
                self.logger.debug(f'Removing {char} and all modifiers from modifier list.')
                self.modifier = ''
            self.logger.debug(f'{char} released - current P_MAP: {self.p_map}')
            if char in self.p_map:
                self.p_map.remove(char)
                self.send_keyup(char, self.ids)
        

    def send_keydown(self, char, ids):
        """Send the keydown to the specified window IDs.
        
        This method sends the keydown event to the specified windows. It also 
        makes sure to send modifier keys alongside the pressed key if necessary.
        Additionally, broadcast is started from here if the relevant key was 
        pressed.
        """
        if f'{self.modifier}{char}' == self.config['keys']['start broadcast']:
            self.logger.debug(f'Broadcast started')
            self.clear_modifiers()
            self.broadcast = True
            self.ml.broadcast = True
            return
        if char in self.arrows:
            self.logger.debug(f'Ignoring keydown of arrow {char}')
        if f'{self.modifier}{char}' == self.config['keys']['next window']:
            #self.clear_modifiers()
            self.next_window()
            return
        for id in ids:
            if self.broadcast or f'{char}' == self.config['keys']['stop broadcast']:
                self.logger.debug(f'Sending keydown {char} to {id}')
                run_cmd(f'xdotool keydown --window {id} {self.modifier}{char}')
        if f'{char}' == self.config['keys']['stop broadcast']:
            self.send_keyup(char, ids)

    def send_keyup(self, char, ids):
        """Send the keyup to the specified window IDs.
        
        This method sends the keyup event to the specified windows. It also 
        makes sure to send modifier keys alongside the pressed key if necessary.
        Additionally, broadcast is stopped from here if the relevant key was 
        depressed.
        """
        for id in ids:
            if self.broadcast or f'{char}' == self.config['keys']['stop broadcast']:
                self.logger.debug(f'Sending keyup {char} to {id}')
                run_cmd(f'xdotool keyup --window {id} {self.modifier}{char}')
        if f'{char}' == self.config['keys']['stop broadcast']:
            self.clear_modifiers()
            if self.broadcast:
                self.broadcast = False
                self.ml.broadcast = False
                self.logger.debug(f'Broadcast stopped')


    def process_key(self, key):
        """Helper method for processing keys.
        
        Not all keys are created equal. This makes sure to return the correct 
        value back to the calling function for further processing, regardless 
        of whether the key was a normal or modifier key.
        """
        if hasattr(key, 'char'):
            if key.char == '`' or key.char == '~':
                return self.s_map['`']
            return key.char
        elif key.name in self.s_map:
            return self.s_map[key.name]
        else:
            return None


