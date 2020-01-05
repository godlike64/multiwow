import os
import configparser
import sys
import logging

from multiwow.constants import CONFIG_DIR, CONFIG_FILE

class Config(object):
    
    def __init__(self):
        self.logger = logging.getLogger('multiwow')
        if not os.path.exists(CONFIG_DIR):
            self.logger.warning(f'Configuration directory {CONFIG_DIR} '
                              'does not exist. Creating.')
            os.makedirs(CONFIG_DIR)
        if not os.path.exists(CONFIG_FILE):
            self.logger.warning(f'Configuration file {CONFIG_FILE} does not '
                              'exist. Creating.')
            self.create_config()
        self.parse_config()
        
    def create_config(self):
        self.cp = configparser.ConfigParser(allow_no_value=True)
        self.cp['keys'] = dict()
        self.cp['keys']['start broadcast'] = f'g'
        self.cp['keys']['stop broadcast'] = f'f'
        self.cp['keys']['stop program'] = f'Escape'
        self.cp['keys']['next window'] = f'super+1'
        self.cp['commands'] = dict()
        self.cp['commands']['window ids'] = "xwininfo -int -children -id {id}|grep 1920x1080|cut -d' ' -f6"
        self.cp['commands']['master window'] = f'master_'
        self.cp['commands']['slave windows'] = f'Wow_'
        with open(CONFIG_FILE, 'w') as configfile:
            configfile.write('# This is multiwow\'s default configuration ' +
                'file. It is an example config \n' +
                '# automatically generated due to no config file found.\n' +
                '# Feel free to use this file as is or to modify it to suit '+
                'your needs.\n\n')
            configfile.write('# More information can be found in the ' +
                             'project\'s README file.\n\n\n')
            self.cp.write(configfile)
            self.logger.info(f'Writing default config file at {CONFIG_FILE}.')
    
    def parse_config(self):
        self.cp = configparser.ConfigParser()
        self.cp.read(CONFIG_FILE)

    def config_dump(self):
        self.logger.debug(f'Dumping configuration file:')
        for section in self.cp.sections():
            self.logger.debug(f'- {section}')
            for key in self.cp[section]:
                self.logger.debug(f'  - {key}: {self.cp[section][key]}')
                
                
