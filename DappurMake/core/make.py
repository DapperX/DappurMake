import os
import inspect
from .variable import *

class make:
	"""docstring for DPMK_make"""
	def __init__(self):
		self.rule = []
		self.exp = {}

	def export(self, *args):
		caller_local = inspect.currentframe().f_back.f_locals.items()
		for arg in args:
			if not isinstance(arg, variable):
				raise TypeError("`export` expects a variable type but %s is given" % str(type(arg)))
			ans = None
			for var_name,var_val in caller_local:
				if arg is not var_val:
					continue
				if ans != None:
					raise Exception("Detect duplicate variables %s and %s" % (name_old,name))
				ans = (var_name,var_val)
			if ans == None:
				raise Exception("%s is not a explicit variable" % arg)
			self.exp[ans[0]] = ans[1]


	def unexport(self, *args):
		collect = []
		for arg in args:
			if not isinstance(arg, variable):
				raise TypeError("`unexport` expects a variable type but %s is given" % str(type(arg)))
			for name,val in self.exp.items():
				if arg is val:
					collect.append(name)
		if len(collect) != len(args):
			raise warn("Unexport an unexported variable")
		for k in collect:
			self.exp.pop(k)


	def __setitem__(self, key, value):
		if not (isinstance(key,str) or key == None):
			raise TypeError("`str` or None is requested but %s is given" % str(type(key)))
		if not isinstance(value,rule):
			raise TypeError("`rule` is requested but %s is given" % str(type(value)))
		self.rule.append((key,value))
		print(key,value.tgt,value.dep,value.act)

	def make(self):
		pass

	def start(self, directory=".", filename="makefile.py"):
		os.chdir(directory)
		if not os.path.exists(filename):
			raise FileNotFoundError("%s not found" % filename)
		with open(filename) as file:
			code = compile(file.read(),filename,"exec")
			exec(code,self.exp)

	def register(self, name=None, rule=None):
		if rule is None:
			name, rule = "None", name
		print("#register", name)
		print(rule)