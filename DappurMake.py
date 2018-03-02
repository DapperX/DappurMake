import os
import inspect


def warn(s):
	print("Warning",s)


class decorator:
	@staticmethod
	def ensure_instance(cls_):
		def wrapper(func):
			def inner(self,x,*args,**kwargs):
				cls = eval(cls_)
				if not isinstance(x,cls):
					x = cls(x)
				return func(self,x,*args,**kwargs)
			return inner
		return wrapper


class function:
	"""docstring for function"""
	@staticmethod
	def pwd():
		return variable(os.getcwd())

	@staticmethod
	def dir(path='.'):
		return variable(os.listdir(path))


class make:
	"""docstring for DPMK_make"""
	def __init__(self):
		self.rule = []
		self.exp = {}

	def export(self,*args):
		caller_local = inspect.currentframe().f_back.f_locals.items()
		for arg in args:
			if not isinstance(arg,variable):
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


	def unexport(self,*args):
		collect = []
		for arg in args:
			if not isinstance(arg,variable):
				raise TypeError("`unexport` expects a variable type but %s is given" % str(type(arg)))
			for name,val in self.exp.items():
				if arg is val:
					collect.append(name)
		if len(collect) != len(args):
			raise warn("Unexport an unexported variable")
		for k in collect:
			self.exp.pop(k)


	def __setitem__(self,key,value):
		if not (isinstance(key,str) or key == None):
			raise TypeError("`str` or None is requested but %s is given" % str(type(key)))
		if not isinstance(value,rule):
			raise TypeError("`rule` is requested but %s is given" % str(type(value)))
		self.rule.append((key,value))
		print(key,value.tgt,value.dep,value.act)

	def make(self):
		pass

	def start(self,directory=".",filename="makefile.py"):
		os.chdir(directory)
		if not os.path.exists(filename):
			raise FileNotFoundError("%s not found" % filename)
		with open(filename) as file:
			code = compile(file.read(),filename,"exec")
			exec(code,self.exp)


class rule:
	"""docstring for rule"""
	def __init__(self,tgt):
		self.tgt = tgt
		self.dep = variable()
		self.act = []

	def depend(self,*args):
		self.dep += args
		return self

	def __getattr__(self,name):
		def do(*args):
			for arg in args:
				if isinstance(arg,variable):
					arg = str(arg)
				if isinstance(arg,str):
					arg= command(arg)
				if callable(arg):
					self.act.append(arg)
				else:
					TypeError("%s is not a str or callable" % arg)
			return self

		if name=="do":
			global globalDependence
			global globalTarget
			globalDependence.text = self.dep.text
			globalTarget.text = self.tgt.text
			return do
		else:
			AttributeError("Attribute %s does not exist" % name)


class command:
	"""docstring for command"""
	def __init__(self,cmd):
		assert isinstance(cmd,str)
		self.cmd = cmd
		
	def __call__(self):
		os.system(self.cmd)

	def __str__(self):
		return self.cmd

class variable:
	"""docstring for DPMK_variable"""

	@classmethod
	def _proto(cls,text:list) -> 'variable':
		assert isinstance(text,list)
		proto = cls()
		proto.text = text
		return proto


	def __init__(self,*args):
		self.text = []

		for arg in args:
			if isinstance(arg,str):
				self.text.append(arg)
				continue
			if isinstance(arg,variable):
				self.text.extend(arg.text)
				continue
			try:
				arg_iter = iter(arg)
			except TypeError as te:
				raise TypeError("Error: Unrecognizable variable type %s" % str(type(arg)))
			for subarg in arg_iter:
				if isinstance(subarg,str):
					self.text.append(subarg)
				elif isinstance(subarg,variable):
					self.text.extend(subarg.text)
				else:
					raise TypeError("Error: Unrecognizable variable type %s" % str(type(subarg)))


	@decorator.ensure_instance('variable')
	def __iadd__(self,x):
		self.text.extend(x.text)
		return self

	@decorator.ensure_instance('variable')
	def __add__(self,x):
		return self._proto(self.text + x.text)

	@decorator.ensure_instance('variable')
	def __radd__(self,x):
		return x.__add__(self)


	def _sub_get_list(self,x) -> list:
		return list(filter(lambda val:val not in x.text,self.text))

	@decorator.ensure_instance('variable')
	def __isub__(self,x):
		self.text = self._sub_get_list(x)
		return self

	@decorator.ensure_instance('variable')
	def __sub__(self,x):
		return self._proto(self._sub_get_list(x))


	def _mul_get_list(x,y) -> list:
		return [k+t for t in y.text for k in x.text]

	@decorator.ensure_instance
	def __imul__(self,x):
		self.text = self._mul_get_list(x)
		return self

	@decorator.ensure_instance('variable')
	def __mul__(self,x):
		return self._proto(self._mul_get_list(x))

	@decorator.ensure_instance('variable')
	def __rmul__(self,x):
		return x.__mul__(self)


	def __truediv__(self,x):
		def _div(val):
			if val[-n:]==x:
				return val[:-n]
			warn("'%s' is not the prefix of '%s'" % (x,val))
			return val

		if not isinstance(x,str):
			raise TypeError("Div operator requests 'str' type")

		n = len(x)
		return self._proto([_div(k) for k in self.text])

	def __rtruediv__(self,x):
		def _rdiv(val):
			if val[:n]==x:
				return val[n:]
			warn("'%s' is not the prefix of '%s'" % (x,val))
			return val

		if not isinstance(x,str):
			raise TypeError("Div operator requests 'str' type")

		n = len(x)
		return self._proto([_rdiv(k) for k in self.text])


	def to_str(self,separator=' '):
		return separator.join(self.text)

	def __str__(self):
		return self.to_str()

	def __invert__(self):
		return self.__str__()


	def foreach(self,func):
		for i,k in enumerate(self.text):
			self.text[i] = func(k)


	def do(self,*args,**kwargs):
		return rule(tgt=self).do(*args,**kwargs)

	def depend(self,*args,**kwargs):
		return rule(tgt=self).depend(*args,**kwargs)


globalDependence = variable()
globalTarget = variable()