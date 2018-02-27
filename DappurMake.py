import os


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
		pass

	def export(self,*args):
		pass

	def __setitem__(self,key,value):
		print(key,value.var,value.dep,value.act)

	def make(self):
		pass


class rule:
	"""docstring for rule"""
	def __init__(self,var):
		self.var = var
		self.dep = variable()
		self.act = []

	def depend(self,*args):
		self.dep += variable(*args)
		return self

	def do(self,*args):
		for arg in args:
			if isinstance(arg,variable):
				arg = str(arg)
			if isinstance(arg,str) or callable(arg):
				self.act.append(arg)
			else:
				TypeError("%s is not a str or callable" % arg)
		return self


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
				raise TypeError("Error: Unrecognizable variable type")
			for subarg in arg_iter:
				if isinstance(subarg,str):
					self.text.append(subarg)
				else:
					raise TypeError("Error: Unrecognizable variable type")


	@decorator.ensure_instance('variable')
	def __iadd__(self,x):
		self.text.extend(x.text)

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

	@decorator.ensure_instance('variable')
	def __sub__(self,x):
		return self._proto(self._sub_get_list(x))


	def _mul_get_list(x,y) -> list:
		return [k+t for t in y.text for k in x.text]

	@decorator.ensure_instance
	def __imul__(self,x):
		self.text = self._mul_get_list(x)

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
		return rule(var=self).do(*args,**kwargs)

	def depend(self,*args,**kwargs):
		return rule(var=self).depend(*args,**kwargs)


# import inspect
# def retrieve_name(var):
# 	'''
# 	utils:
# 	get back the name of variables
# 	'''
# 	callers_local_vars = inspect.currentframe().f_back.f_locals.items()
# 	return [var_name for var_name, var_val in callers_local_vars if var_val is var]


# b = "abc"
# a = b
# print(retrieve_name(a))