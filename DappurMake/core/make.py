import os
import inspect
from .. import core
from . import helper

class make:
	"""docstring for DPMK_make"""
	def __init__(self):
		self.rule = {}
		self.rule_named = {}
		self.rule_tgt = {}
		self.env = {}

	def export(self, *args):
		caller_local = inspect.currentframe().f_back.f_locals.items()
		caller_global = inspect.currentframe().f_back.f_globals.items()
		for arg in args:
			if not isinstance(arg, core.variable):
				raise TypeError("`export` expects a `variable` type but %s is given" % type(arg))
			ans = None
			for name,val in caller_local:
				if arg is not val:
					continue
				if ans != None:
					raise Exception("Detect duplicate variables %s and %s" % (name_old, name))
				ans = (name, val)
			if ans is None:
				for name,val in caller_global:
					if arg is not val:
						continue
					if ans != None:
						raise Exception("Detect duplicate variables %s and %s" % (name_old, name))
					ans = (name, val)
			if ans is None:
				raise Exception("%s is not a explicit variable" % arg)
			self.env[ans[0]] = ans[1]


	def unexport(self, *args):
		collect = []
		for arg in args:
			if not isinstance(arg, core.variable):
				raise TypeError("`unexport` expects a `variable` type but %s is given" % type(arg))

			is_found = False
			for name,val in self.env.items():
				if arg is val:
					collect.append(name)
					is_found = True
			if not is_found:
				warn("%s is not exported before" % arg)

		for k in collect:
			self.env.pop(k)


	def __setitem__(self, key, value):
		self.register(key, value)


	def call(self, directory=".", filename="makefile.py"):
		os.chdir(directory)
		if not os.path.exists(filename):
			raise FileNotFoundError("%s not found" % filename)
		with open(filename) as file:
			code = compile(file.read(),filename,"exec")
			exec(code, self.env)


	def start(self, root=None):
		if root is None:
			root = self._find_root()
		elif isinstance(root, str):
			root = self.rule_named[root]
		elif isinstance(root, core.rule):
			if id(root) not in self.rule:
				raise ValueError("`root` is not registered")
		else:
			raise TypeError("Unrecognized `root` type %s" % type(root))

		def _start(root):
			for dep in root.dep:
				child = self.rule_tgt.get(id(dep))
				if child is not None:
					_start(child)
			print("#begin actions", root.act)
			for act in root.act:
				act()

		_start(root)


	def register(self, name=None, rule=None):
		if rule is None:
			name, rule = None, name

		if not (isinstance(name, str) or name==None):
			raise TypeError("`str` or None is requested but %s is given" % type(name))
		if not isinstance(rule, core.rule):
			raise TypeError("`rule` is requested but %s is given" % type(rule))

		print("#register", name)
		print(rule)

		rule_id = id(rule)
		if rule_id in self.rule:
			raise KeyError("An identical rule should not be registered more than once")
		self.rule[rule_id] = (name, rule)

		self.rule_tgt[id(rule.tgt)] = rule

		if name is not None:
			if name in self.rule_named:
				raise KeyError("The name %s has been used for another rule" % name)
			self.rule_named[name] = rule

		return rule


	def _find_root(self):
		ufset = {}

		_get_id = lambda var: rank.setdefault(id(var), id(var))
		for k,v in self.rule.items():
			rule = v[1]
			f_tgt = helper.ufset_find(ufset, _get_id(rule.tgt))
			for dep in rule.dep:
				f_dep = helper.ufset_find(ufset, _get_id(dep))
				ufset[f_dep] = f_tgt

		root = []
		for k,v in ufset.items():
			if k==v:
				root.append(k)
		if len(root)>1:
			raise ValueError("%d roots exists, failed to infer" % len(root))
		return self.rule_tgt[root.keys().next()]