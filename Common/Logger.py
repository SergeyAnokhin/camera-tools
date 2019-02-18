import logger


class Logger:
    name: str
    loggers: []

    def __init__(self, name: str):
        self.name = name

    def Create(self, name: str):
        result = Logger(name)
        self.loggers.append(result)
        return result

# import os
# import logging

# os.remove('temp/example.html')
# logging.basicConfig(
#     format='%(asctime)s <b>%(message)s</b><br>',
#     datefmt='%H:%M:%S',
#     filename='temp/example.html',
#     level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')