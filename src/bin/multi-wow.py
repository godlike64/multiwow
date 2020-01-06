#!/usr/bin/env python3

import argparse
import logging

from multiwow.listeners.kblistener import KeyboardListener
from multiwow.config import Config

def loglevel_validator(v):
    """Validate selected log level. Return v.upper() or raise an error."""
    if v.upper() not in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
        raise argparse.ArgumentTypeError('Log level must be a valid Python ' +
                                         'log level. See -h for details.')
    else:
        return v.upper()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'wow-multibox v0.1')
    parser.add_argument('-l', '--log-level',
                        metavar='level',
                        type=loglevel_validator,
                        default='INFO',
                        help='Define wow-multibox\'s log level. Can be any of' +
                        ' Python\'s standard log levels: CRITICAL, ERROR, ' +
                        'WARNING, INFO, DEBUG.')
    args = parser.parse_args()
    try:
        if args.log_level == 'DEBUG':
            extra_log_fields = '- %(filename)s:%(lineno)s '
        else:
            extra_log_fields = ''
        logformat = f'%(asctime)s - %(name)s - %(levelname)s {extra_log_fields}- %(message)s'
        logging.basicConfig(level=args.log_level, format=logformat)
        logger = logging.getLogger('multiwow')
        logger.info('Starting')
        config = Config()
        config.config_dump()
        kl = KeyboardListener(config)
        kl.start()
    except KeyboardInterrupt:
        logger.warn('Ctrl-C detected. Shutting down cleanly.')
        kl.ml.listener.stop()
        kl.toggle_echo(True)
    finally:
        logger.info('Shutdown complete.')
