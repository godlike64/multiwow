import os
import configparser
import sys
import logging
from pathlib import Path

from multiwow.constants import CONFIG_DIR, CONFIG_FILE

class Config(object):
    """Helper class to handle ConfigParser.
    
    This class creates the necessary directory/files needed for multiwow to 
    work properly. If the configuration file does not exist, a default one is 
    created.
    """
    
    def __init__(self, config_file):
        self.logger = logging.getLogger('multiwow')
        self.config_file=Path(config_file)
        if '~' in str(self.config_file.parent):
            target_dir = self.config_file.parent.expanduser()
        else:
            target_dir = self.config_file.parent
        if not os.path.exists(target_dir):
            self.logger.warning(f'Configuration directory {target_dir} '
                              'does not exist. Creating.')
            os.makedirs(self.config_file.parent)
        if not os.path.exists(self.config_file):
            self.logger.warning(f'Configuration file {self.config_file} does not '
                              'exist. Creating.')
            self.create_config()
        self.parse_config()
        
    def create_config(self):
        """Create a default configuration file."""
        self.cp = configparser.ConfigParser(allow_no_value=True)
        self.cp['keys'] = dict()
        self.cp['keys']['start broadcast'] = f'g'
        self.cp['keys']['stop broadcast'] = f'f'
        self.cp['keys']['stop program'] = f'Escape'
        self.cp['keys']['next window'] = f'r'
        self.cp['commands'] = dict()
        self.cp['commands']['window ids'] = "xwininfo -int -children -id {id}|grep 1920x1080|cut -d' ' -f6"
        self.cp['commands']['master window'] = f'master_'
        self.cp['commands']['slave windows'] = f'Wow_'
        with open(self.config_file, 'w') as configfile:
            configfile.write('# This is multiwow\'s default configuration ' +
                'file. It is an example config \n' +
                '# automatically generated due to no config file found.\n' +
                '# Feel free to use this file as is or to modify it to suit '+
                'your needs.\n\n')
            configfile.write('# More information can be found in the ' +
                             'project\'s README file.\n\n\n')
            self.cp.write(configfile)
            self.logger.info(f'Writing default config file at {self.config_file}.')
    
    def parse_config(self):
        """Parse the existing configuration file."""
        self.cp = configparser.ConfigParser()
        self.cp.read(self.config_file)

    def config_dump(self):
        """Dump the configuration file contents to the log."""
        self.logger.debug(f'Dumping configuration file {self.config_file}:')
        for section in self.cp.sections():
            self.logger.debug(f'- {section}')
            for key in self.cp[section]:
                self.logger.debug(f'  - {key}: {self.cp[section][key]}')
                
                
