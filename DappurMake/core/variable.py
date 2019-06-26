import subprocess as subproc
from .. import core
from . import helper

class variable:
	"""docstring for DPMK_variable"""

	@classmethod
	def _proto(cls, text:list) -> "variable":
		assert isinstance(text, list)
		proto = cls()
		proto.text = text
		return proto


	def __init__(self, *args):
		self.text = []

		for arg in args:
			if isinstance(arg, bytes):
				arg = arg.decode()
			if isinstance(arg, str):
				self.text.append(arg)
				continue
			if isinstance(arg, variable):
				self.text.extend(arg.text)
				continue
			try:
				arg_iter = iter(arg)
			except TypeError as te:
				raise TypeError("Error: Unrecognizable variable type %s" % str(type(arg)))
			for subarg in arg_iter:
				if isinstance(subarg, str):
					self.text.append(subarg)
				elif isinstance(subarg, variable):
					self.text.extend(subarg.text)
				else:
					raise TypeError("Error: Unrecognizable variable type %s" % str(type(subarg)))


	def __getitem__(self, index):
		return self._proto(self.text[index])


	def __call__(self, shell=True, stdout=None, stderr=None, strip=True, timeout=None):
		if stdout is None:
			stdout = subproc.PIPE
		if stderr is None:
			stderr = subproc.PIPE
		child = subproc.Popen(self.text, shell=shell, stdout=stdout, stderr=stderr)
		child.wait(timeout)
		stdout = child.stdout.read() if child.stdout is not None else b''
		stderr = child.stderr.read() if child.stderr is not None else b''
		if strip:
			stdout = stdout.strip()
			stderr = stderr.strip()
		return (child.returncode, stdout, stderr)


	@helper.decorator.ensure_instance("core.variable")
	def __iadd__(self, x):
		self.text.extend(x.text)
		return self

	@helper.decorator.ensure_instance("core.variable")
	def __add__(self, x):
		return self._proto(self.text + x.text)

	@helper.decorator.ensure_instance("core.variable")
	def __radd__(self, x):
		return x.__add__(self)


	def _sub_get_list(self, x) -> list:
		return list(filter(lambda val:val not in x.text,self.text))

	@helper.decorator.ensure_instance("core.variable")
	def __isub__(self, x):
		self.text = self._sub_get_list(x)
		return self

	@helper.decorator.ensure_instance("core.variable")
	def __sub__(self, x):
		return self._proto(self._sub_get_list(x))


	def _mul_get_list(x,y) -> list:
		return [k+t for t in y.text for k in x.text]

	@helper.decorator.ensure_instance("core.variable")
	def __imul__(self, x):
		self.text = self._mul_get_list(x)
		return self

	@helper.decorator.ensure_instance("core.variable")
	def __mul__(self, x):
		return self._proto(self._mul_get_list(x))

	@helper.decorator.ensure_instance("core.variable")
	def __rmul__(self, x):
		return x.__mul__(self)


	def _div_get_list(self, x) -> list:
		def _div(val):
			if val[-n:]==x:
				return val[:-n]
			warn("'%s' is not the suffix of '%s'" % (x,val))
			return val

		if not isinstance(x,str):
			raise TypeError("Div operator requests 'str' type")
		n = len(x)
		return [_div(k) for k in self.text]

	def __truediv__(self, x):
		return self._proto(self._div_get_list(x))

	def __itruediv__(self, x):
		self.text = self._div_get_list(x)
		return self

	def __rtruediv__(self, x):
		def _rdiv(val):
			if val[:n]==x:
				return val[n:]
			warn("'%s' is not the prefix of '%s'" % (x,val))
			return val

		if not isinstance(x,str):
			raise TypeError("Div operator requests 'str' type")
		n = len(x)
		return self._proto([_rdiv(k) for k in self.text])


	def to_str(self,separator=' ', prefix="", suffix=""):
		return prefix+separator.join(self.text)+suffix

	def __str__(self):
		return self.to_str()

	def __invert__(self):
		return self.__str__()


	def foreach(self,func):
		for i,k in enumerate(self.text):
			self.text[i] = func(k)


	def do(self,*args,**kwargs):
		return core.rule(tgt=self).do(*args, **kwargs)

	def depend(self,*args,**kwargs): 
		return core.rule(tgt=self).depend(*args, **kwargs)