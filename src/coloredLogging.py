# based on http://stackoverflow.com/questions/384076

import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"

LEVEL_COLORS = {
	'WARNING': YELLOW,
	'INFO': WHITE,
	'DEBUG': BLUE,
	'CRITICAL': YELLOW,
	'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
	def __init__(self, frm):
		logging.Formatter.__init__(self, frm)
	def format(self, record):
		levelname = record.levelname
		if levelname in LEVEL_COLORS:
			levelname = (COLOR_SEQ % (30 +
					LEVEL_COLORS[levelname]) +
						levelname + RESET_SEQ)
			record.levelname = levelname
		return logging.Formatter.format(self, record)

def basicConfig(format="%(levelname)s %(name)s %(message)s",
		level=logging.DEBUG):
	formatter = ColoredFormatter(format)
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logging.root.addHandler(handler)
	logging.root.setLevel(level)
