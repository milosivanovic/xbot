import os
import importlib

for module in os.listdir(os.path.dirname(__file__)):
	if module.endswith(".py"):
		module = module[:-3]
		if module != "__init__":
			importlib.reload(importlib.import_module('xbot.modules.' + module, 'xbot.modules'))
del module
