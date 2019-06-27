from .. import core
print(dir(core))

def warn(s):
	print("[Warning] ", s)


class decorator:
	@staticmethod
	def ensure_instance(cls_):
		def wrapper(func):
			def inner(self, x, *args, **kwargs):
				cls = eval(cls_)
				if not isinstance(x, cls):
					x = cls(x)
				return func(self, x, *args, **kwargs)
			return inner
		return wrapper


def wrapper(func, *args, **kwargs):
	def inner():
		return func(*args, **kwargs)
	return inner


def ufset_find(f, u):
	return u if f[u]==u else ufset_find(f[u])


def nothing(*args, **kwargs):
	pass