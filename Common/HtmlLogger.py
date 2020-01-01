"""
HTML logger inspired by the Horde3D logger.
Usage:
 - call setup and specify the filename, title, version and level
 - call dbg, info, warn or err to log messages.

Source : https://gist.github.com/ColinDuquesnoy/8296508#
"""

import logging
import time, datetime

#: HTML header (starts the document
_START_OF_DOC_FMT = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%(title)s</title>
<link rel = "stylesheet" type = "text/css" href = "static/log.css" />
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<body>
<script>
function autoScrolling() {
   window.scrollTo(0,document.body.scrollHeight);
}

setInterval(autoScrolling, 5000); 
</script>
<div class="Tab blueRows"><div class="TabBody">
"""

_END_OF_DOC_FMT = """
 </div></div>
</body>
</html>
"""

# _MSG_FMT = """
# <tr>
# <td class="time" title="%(time_full)s (%(elaspsed_sec_full)s)">%(time)s%(elaspsed_sec)s</td>
# <td class="%(class)s" title="%(level)s">%(level_short)s</td>
# <td class="name" title="%(pathname)s"><b>%(name)s</b></td>
# <td class="%(class)s">%(msg)s</td>
# <tr>
# """

_MSG_FMT = """
<div class="TabRow %(class)s">
<div class="TabCell time" title="%(time_full)s (%(elaspsed_sec_full)s)">%(time)s%(elaspsed_sec)s</div>
<div class="TabCell level">%(level_short)s</div>
<div class="TabCell name" title="%(pathname)s">%(name)s</div>
<div class="TabCell">%(msg)s</div>
</div>
"""



class HTMLFileHandler(logging.FileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """
    def __init__(self, *args):
        super().__init__(*args)
        assert self.stream is not None
        # Write header
        self.stream.write(_START_OF_DOC_FMT % {"title": "Log"})

    def close(self):
        # finish document
        # self.stream.write(_END_OF_DOC_FMT)
        super().close()


class HTMLRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """
    def __init__(self, filename, when='h', backupCount=7, encoding='utf-8'):
        super().__init__(filename, when=when, interval=1, backupCount=backupCount, encoding=encoding)
        assert self.stream is not None
        # Write header
        self.stream.write(_START_OF_DOC_FMT % {"title": "Log"})

    # def emit(self, record):
    #     super().emit(record)

    # def handle(self, record):
    #     super().handle(record)

    def close(self):
        # finish document
        # self.stream.write(_END_OF_DOC_FMT)
        super().close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    """
    CSS_CLASSES = {'WARNING': 'warn',
                   'INFO': 'info',
                   'DEBUG': 'debug',
                   'CRITICAL': 'err',
                   'ERROR': 'err'}

    def __init__(self):
        super().__init__()
        self._start_time = time.time()

    def format(self, record: logging.LogRecord):
        try:
            class_name = self.CSS_CLASSES[record.levelname]
        except KeyError:
            class_name = "info"

        global _last_log_time
        t = datetime.datetime.now()
        elaspsed_sec = (t - _last_log_time).total_seconds()
        elaspsed_sec_str = f'({elaspsed_sec:.1f})'
        elaspsed_sec_str = elaspsed_sec_str if elaspsed_sec > 1 else ""
        _last_log_time = t

        # handle '<' and '>' (typically when logging %r)
        msg = record.msg
        # msg = msg.replace("<", "&#60")
        # msg = msg.replace(">", "&#62")

        # <LogRecord: API, 20, C:\Src\camera-tools\web\urls.py, 156, "|################################################################################|">
        # args:()
        # asctime:'22:55:52'
        # created:1577570152.9400687
        # exc_info:None
        # exc_text:None
        # filename:'urls.py'
        # funcName:'<module>'
        # levelname:'INFO'
        # levelno:20
        # lineno:156
        # message:'|################################################################################|'
        # module:'urls'
        # msecs:940.0687217712402
        # msg:'|################################################################################|'
        # name:'API'
        # pathname:'C:\\Src\\camera-tools\\web\\urls.py'
        # process:2712
        # processName:'MainProcess'
        # relativeCreated:55798.1812953949
        # stack_info:None
        # thread:14552
        # threadName:'MainThread'

        return _MSG_FMT % {
            "class": class_name,
            "time": f'{t:%H:%M:%S}',
            "time_full": f'{t:%Y-%m-%d %H:%M:%S.%f}',
            "time_microsecond": f'{t:%f}',
            "level": record.levelname,
            "level_short": f'{record.levelname:3.3}',
            "elaspsed_sec": elaspsed_sec_str,
            "elaspsed_sec_full": elaspsed_sec,
            "msg": msg,
            "name": record.name,
            "pathname": record.pathname
        }


class HTMLLogger(logging.Logger):
    """
    Log records to html using a custom HTML formatter and a specialised
    file stream handler.
    """
    def __init__(self,
                 name="html_logger",
                 level=logging.DEBUG,
                 filename="log.html"):
        super().__init__(name, level)
        f = HTMLFormatter()
        h = HTMLFileHandler(filename)
        h.setFormatter(f)
        self.addHandler(h)


#: Global
_logger = None
_last_log_time = datetime.datetime.now()

def setup(level=logging.DEBUG):
    """
    Setup the logger
    :param title: Title of the html document
    :param filename: output filename. Default is "log.html"
    :param mode: File open mode. Default is 'w'
    :param level: handler output level. Default is DEBUG
    """
    global _logger
    if _logger is None:
        _logger = HTMLLogger(filename="log.html", level=level)

    global _last_log_time
    _last_log_time = datetime.datetime.now()


def dbg(msg):
    """
    Logs a debug message
    """
    global _logger
    _logger.debug(msg)


def info(msg):
    """
    Logs an info message
    """
    global _logger
    _logger.info(msg)


def warn(msg):
    """
    Logs a warning message
    """
    global _logger
    _logger.warning(msg)


def err(msg):
    """
    Logs an error message
    """
    global _logger
    _logger.error(msg)


# Example of usage
if __name__ == "__main__":
    setup("Example", "1.0")
    dbg("A debug message")
    info("An information message")
    warn("A warning message")
    time.sleep(1)
    err("An error message")



# HtmlLogger.setup()
# HtmlLogger.dbg("A debug <b>message</b> !!!")
# HtmlLogger.info("An information message")
# HtmlLogger.warn("A warning message")
# HtmlLogger.err("An error message")
