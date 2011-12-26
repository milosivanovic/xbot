import os

for module in os.listdir(os.path.dirname(__file__)):
	if module.endswith(".py"):
		module = module[:-3]
		if module != "__init__":
			reload(__import__(module, locals(), globals()))
del module
