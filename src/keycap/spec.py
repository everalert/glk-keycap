from keycap.helper import KeySizeSpec, KeyMountSpec, KeyMarkSpec
from keycap.body import KeyBody
from copy import deepcopy

class KeySpec:

	defaults = {
		'body':		KeyBody(),
		'size':		KeySizeSpec(),
		'mount':	KeyMountSpec(),
		'mark':		KeyMarkSpec(),
	}

	def __init__(self, **kwargs):
		defaults = deepcopy(KeySpec.defaults)
		for a in defaults.keys():
			setattr(self, a, kwargs.get(a, defaults.get(a)))
	
	def clone(self, **kwargs) -> 'KeySpec':
		new = deepcopy(self)
		for a in vars(new).keys():
			if kwargs.get(a) is not None:
				setattr(new, a, kwargs.get(a))
		return new
	
	def __deepcopy__(self, memo=None) -> 'KeySpec':
		if memo is None:	memo = {}
		return KeySpec(**{a[0]:deepcopy(a[1],memo) for a in vars(self).items()})
	
	def __str__(self) -> str:
		return 'KeySpec( {0} )'.format(', '.join(['{0}={1}'.format(a[0],a[1]) for a in vars(self).items()]))