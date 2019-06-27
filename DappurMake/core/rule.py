from .. import core
from . import helper
import os
import subprocess as subproc
from collections import Iterable

class rule:
	"""docstring for rule"""
	def __init__(self, tgt):
		self.tgt = tgt
		self.dep = []
		self.act = []


	def __str__(self):
		res = ""
		res += "[target]" + str(self.tgt) + '\n'
		res += "[depend]" + str(self.dep) + '\n'
		res += "[action]" + str(self.act) + '\n'
		return res


	@helper.decorator.ensure_instance("core.variable")
	def depend(self,item):
		self.dep.append(item)
		return self


	def do(self, action, silence=False, parser=str.format):
		# generate the executable function by pasring the str or decorate the callable object
		def gen_executable(k):
			if isinstance(k, str):
				if parser is not None:
					cmd = parser(k, self.tgt, *self.dep, _tgt=self.tgt, _dep=self.dep)
					x = lambda : subproc.run(cmd, shell=True).returncode==0
			elif callable(k):
				x = helper.wrapper(k, self.tgt, *self.dep, _tgt=self.tgt, _dep=self.dep)
			else:
				TypeError("%s is not a str or callable" % k)
			return x

		# if the parameter is a single action, we then wrapper it as an action list
		if isinstance(action, str) or callable(action):
			action = [action]
		if not isinstance(action, Iterable):
			raise TypeError("Unknown type of actions: %s" % type(action))

		self.act.extend([gen_executable(k) for k in action])
		return self


	def need_update(self):
		# Considering four cases that require updates:
		# 1. U.depend(V)	mtime(U)<mtime(V)
		# 2. ().depend(V)	always True (deem mtime(U) as -inf)
		# 3. U.depend(())	always True (deem mtime(V) as inf)
		# 4. ().depend(())	always True (deem mtime(U) as -inf, mtime(V) as inf)
		inf = float("inf")

		mtime_tgt_min = inf
		for stgt in self.tgt.text:
			mtime_tgt = os.path.getmtime(stgt) if os.path.exists(stgt) else -inf
			if mtime_tgt<mtime_tgt_min:
				mtime_tgt_min = mtime_tgt
		if len(self.tgt)==0:
			mtime_tgt_min = -inf

		mtime_dep_max = -inf
		cnt_sdep = 0
		for dep in self.dep:
			cnt_sdep += len(dep.text)
			for sdep in dep.text:
				if not os.path.exists(sdep):
					raise RuntimeError("No rule to make '%s', needed by '%s'" % (sdep,stgt))
				mtime_dep = os.path.getmtime(sdep)
				if mtime_dep>mtime_dep_max:
					mtime_dep_max = mtime_dep
		if cnt_sdep==0:
			mtime_dep_max = inf

		# Whether the oldest target has been outdated than the newest dependency
		return mtime_tgt_min<mtime_dep_max


	def update(self, force=False):
		if not (force or self.need_update()):
			return

		print("#begin actions", self.act)
		for act in self.act:
			if not act():
				raise RuntimeError("Error occurs. Failed")

		if self.need_update():
			raise RuntimeError("Target '%s' is not updated. Failed." % self.tgt)