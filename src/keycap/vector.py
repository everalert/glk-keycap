import math
import numpy as np
from copy import deepcopy


# VECTOR 2

class Vec2:
	
	def __init__(self, x:float=0, y:float=0) -> 'Vec2':
		self.x:float = x
		self.y:float = y
	
	def clone(self, x=None, y=None) -> 'Vec2':
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new
	
	def toTuple(self) -> tuple:
		return (self.x, self.y)
	
	def toVec3(self) -> 'Vec3':
		return Vec3(self.x, self.y, 0)
	
	def mag(self) -> float:
		return math.sqrt(self.x*self.x + self.y*self.y)
	
	def setMag(self, mag:float) -> 'Vec2':
		m = mag/self.mag()
		self.x, self.y = self.x*m, self.y*m
		return self
	
	def ang(self) -> float:
		if self.y == 0:
			return 0 if self.x >= 0 else 180
		if self.x == 0:
			return 90 if self.y >= 0 else 270
		a = math.degrees(math.atan(self.y/self.x))
		return 180+a if self.x < 0 else a%360
	
	def rotate(self, angle:float) -> 'Vec2':
		t = math.radians(angle)
		xs, xc, ys, yc = self.x*math.sin(t), self.x*math.cos(t), self.y*math.sin(t), self.y*math.cos(t)
		self.x, self.y = xc-ys, xs+yc
		return self
	
	def __deepcopy__(self, memo=None) -> 'Vec2':
		return Vec2(deepcopy(self.x),deepcopy(self.y))
	
	def __str__(self) -> str:
		return "Vec2({0},{1})".format(self.x, self.y)
	
	def __add__(self, o) -> 'Vec2':
		return Vec2(self.x+o, self.y+o) if isinstance(o,(float,int)) else Vec2(self.x+o.x, self.y+o.y) if isinstance(o,(Vec2,Vec3)) else TypeError
	
	def __sub__(self, o) -> 'Vec2':
		return Vec2(self.x-o, self.y-o) if isinstance(o,(float,int)) else Vec2(self.x-o.x, self.y-o.y) if isinstance(o,(Vec2,Vec3)) else TypeError
	
	def __mul__(self, o) -> 'Vec2':
		return Vec2(self.x*o, self.y*o) if isinstance(o,(float,int)) else Vec2(self.x*o.x, self.y*o.y) if isinstance(o,(Vec2,Vec3)) else TypeError
	
	def __truediv__(self, o) -> 'Vec2':
		return Vec2(self.x/o, self.y/o) if isinstance(o,(float,int)) else Vec2(self.x/o.x, self.y/o.y) if isinstance(o,(Vec2,Vec3)) else TypeError


# VECTOR 3

class Vec3:
	
	def __init__(self, x:float=0, y:float=0, z:float=0):
		self.x = x
		self.y = y
		self.z = z
	
	def clone(self, x=None, y=None, z=None):
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new
	
	def toTuple(self):
		return (self.x, self.y, self.z)
	
	def toVec2(self):
		return Vec2(self.x, self.y)
	
	def mag(self):
		return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
	
	def rotateX(self, angle):
		c, s, pos = np.cos(math.radians(angle)), np.sin(math.radians(angle)), [self.x,self.y,self.z]
		new = np.dot(pos, np.array([[1.,  0,  0],  [0 ,  c, -s],  [0 ,  s,  c]]))
		self.x, self.y, self.z = new
		return self
	
	def rotateY(self, angle):
		c, s, pos = np.cos(math.radians(angle)), np.sin(math.radians(angle)), [self.x,self.y,self.z]
		new = np.dot(pos, np.array([[c,  0,  -s],  [0,  1,   0],  [s,  0,   c]]))
		self.x, self.y, self.z = new
		return self
	
	def rotateZ(self, angle):
		c, s, pos = np.cos(math.radians(angle)), np.sin(math.radians(angle)), [self.x,self.y,self.z]
		new = np.dot(pos, np.array([[c, -s,  0 ],  [s,  c,  0 ],  [0,  0,  1.]]))
		self.x, self.y, self.z = new
		return self
	
	def __deepcopy__(self, memo=None):
		return Vec3(deepcopy(self.x),deepcopy(self.y),deepcopy(self.z))
	
	def __str__(self):
		return "Vec3({0},{1},{2})".format(self.x, self.y, self.z)
	
	def __add__(self, o):
		return Vec3(self.x+o, self.y+o, self.z+o) if isinstance(o,(float,int)) else Vec3(self.x+o.x, self.y+o.y, self.z) if isinstance(o,(Vec2)) else Vec3(self.x+o.x, self.y+o.y, self.z+o.z) if isinstance(o,(Vec3)) else TypeError 
	
	def __sub__(self, o):
		return Vec3(self.x-o, self.y-o, self.z-o) if isinstance(o,(float,int)) else Vec3(self.x-o.x, self.y-o.y, self.z) if isinstance(o,(Vec2)) else Vec3(self.x-o.x, self.y-o.y, self.z-o.z) if isinstance(o,(Vec3)) else TypeError
	
	def __mul__(self, o):
		return Vec3(self.x*o, self.y*o, self.z*o) if isinstance(o,(float,int)) else Vec3(self.x*o.x, self.y*o.y, self.z) if isinstance(o,(Vec2)) else Vec3(self.x*o.x, self.y*o.y, self.z*o.z) if isinstance(o,(Vec3)) else TypeError
	
	def __truediv__(self, o):
		return Vec3(self.x/o, self.y/o, self.z/o) if isinstance(o,(float,int)) else Vec3(self.x/o.x, self.y/o.y, self.z) if isinstance(o,(Vec2)) else Vec3(self.x/o.x, self.y/o.y, self.z/o.z) if isinstance(o,(Vec3)) else TypeError
