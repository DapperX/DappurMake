from .. import core
import os

def dir(pwd=None):
	if pwd is None:
		pwd = "."
	res = []
	for file in os.listdir(pwd):
		if os.path.isdir(os.path.join(pwd, file)):
			res.append(file)
	return core.variable(res)