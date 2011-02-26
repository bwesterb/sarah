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
	def __init__(self, frm):
		logging.Formatter.__init__(self, frm)
	def format(self, record):
		levelname = record.levelname
		pref, suf = '', ''
		if levelname in LEVEL_COLORS:
			pref, suf = LEVEL_COLORS[levelname]
		return pref+logging.Formatter.format(self, record)+suf

def basicConfig(format="%(levelname)s %(name)s %(message)s",
		level=logging.DEBUG):
	formatter = ColoredFormatter(format)
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logging.root.addHandler(handler)
	logging.root.setLevel(level)
