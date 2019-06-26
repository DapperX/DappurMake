from .. import core
from . import helper

class rule:
	"""docstring for rule"""
	def __init__(self, tgt):
		self.tgt = tgt
		self.dep = []
		self.act = []
		self.cmd = []


	def __str__(self):
		res = ""
		res += "[target]" + str(self.tgt) + '\n'
		res += "[depend]" + str(self.dep) + '\n'
		res += "[action]" + str(self.act) + '\n'
		res += "[command]" + str(self.cmd) + '\n'
		return res


	@helper.decorator.ensure_instance("core.variable")
	def depend(self,item):
		self.dep.append(item)
		return self


	def do(self, action, parser=str.format):
		def do_parse(k):
			if isinstance(k, str):
				if parser is not None:
					x = parser(k, self.tgt, *self.dep, _tgt_=self.tgt, _dep_=self.dep, _cmd_=self.cmd)
			elif not callable(k):
				TypeError("%s is not a str or callable" % k)
			return x

		if isinstance(action,str) or callable(action):
			action = [action]
		if not isinstance(action,list):
			raise TypeError("unknown type of action: %s" % type(action))

		self.act.append([do_parse(k) for k in action])
		return self