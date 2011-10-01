# based on http://stackoverflow.com/questions/384076

import logging

RESET_SEQ = "\033[0m"

LEVEL_COLORS = {
        'WARNING': ("\033[1;33m", "\033[0m"),
        'DEBUG': ("\033[36m", "\033[0m"),
        'CRITICAL': ("\033[1;31m", "\033[0m"),
        'ERROR': ("\033[31m", "\033[0m")
}

class ColoredFormatter(logging.Formatter):
        def __init__(self, parent):
                logging.Formatter.__init__(self, None)
                self.parent = parent
        def format(self, record):
                levelname = record.levelname
                pref, suf = '', ''
                if levelname in LEVEL_COLORS:
                        pref, suf = LEVEL_COLORS[levelname]
                return pref+self.parent.format(record)+suf

def basicConfig(format=None,
                formatter=None,
                level=logging.DEBUG):
        if formatter is None:
                if format is None:
                        format = "%(levelname)s %(name)s %(message)s"
                formatter = logging.Formatter(format)
        ourFormatter = ColoredFormatter(formatter)
        handler = logging.StreamHandler()
        handler.setFormatter(ourFormatter)
        logging.root.addHandler(handler)
        logging.root.setLevel(level)
