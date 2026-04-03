import logging.config
import os.path as op
import logging


def config_log(base_dir, logfilename):
    """ format default:
    `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
    """
    format = '[%(asctime)s] %(message)s'
    level = logging.WARNING
    # logfile = op.join(base_dir, "logs", "debug")
    logfile = op.join(base_dir, "logs", logfilename)

    log_setting = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': logging._levelToName[level],
                'formatter': 'file',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'file',
                'filename': logfile,
                'mode': 'a',
                'maxBytes': 10485760,
                'backupCount': 5,
            },
        },
        'formatters': {
            'file': {
                'format': format
            }
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            },
        }

    }

    # Set default log settings.
    logging.config.dictConfig(log_setting)

    # Redirect warnings to log so can be debugged.
    logging.captureWarnings(True)

    # Log out the file output.
    # logging.info(f'Saving log file to: {logfile}')

    return log_setting
