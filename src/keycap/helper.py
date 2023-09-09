import cadquery as cq
from enum import Enum
from copy import deepcopy
import math
import numpy as np
from keycap.vector import Vec2, Vec3


#NOTE: possible bug in get3DPTiltedHeight


# FUNCTIONS


def makeRoundRectWire(w=10, h=10, rad=1, plane="XY"):
	rect = cq.CQ(plane).rect(w, h)
	cnr = rect.vertices().vals()
	return rect.val().fillet2D(rad, cnr)


def makeDraftedWire(w=1.0, h=1.0, angle=1.5, plane="XZ"):
	return (
		cq.CQ(plane)
		.moveTo(w,0)
		.polarLine(h*(1/math.cos(math.radians(angle))), 90-angle)
		.hLineTo(w)
		.close()
	)


def makeDraftedCylinder(rad=2, height=2, draft=1.5):
	path = cq.CQ("XY").circle(rad).val()
	return makeDraftedWire(rad, height, draft).sweep(path) + cq.CQ(cq.Solid.makeLoft([path, path.translate((0,0,height))], True))


def makeDraftedBlock(x=2, y=2, height=2, draft=1.5):
	path = cq.CQ("XY").rect(x,y).val()
	return makeDraftedWire(x/2, height, draft).sweep(path) + cq.CQ(cq.Solid.makeLoft([path, path.translate((0,0,height))], True))


def makeRoundDraftedBlock(x=2, y=2, height=2, fillet=1, draft=1.5):
	path = makeRoundRectWire(x, y, fillet)
	return makeDraftedWire(x/2, height, draft).sweep(path) + cq.CQ(cq.Solid.makeLoft([path, path.translate((0,0,height))], True))


def apply3DPTilt(vec:Vec3, tilt:float=35, tiltY:float=None) -> Vec3:
	tiltY = tiltY if isinstance(tiltY,(int,float)) else tilt
	return vec.rotateZ(-tilt).rotateY(tiltY).rotateZ(tilt)


def get3DPTiltedHeight(aabb:Vec3, angle:float=35, angleY:float=None):
	size = aabb*Vec3(0.5,-0.5,1)
	roof_h = size.z/math.sin(math.radians(90-(angleY if isinstance(angleY,(int,float)) else angle))) #might run into issues w/ different angle+angleY???
	FRB = apply3DPTilt(size*Vec3(1,1,0), angle, angleY)
	BLT = apply3DPTilt(size*Vec3(-1,-1,1), angle, angleY)
	return { 'top':BLT.z, 'roof':FRB.z+roof_h, 'bot':FRB.z, 'h_roof':roof_h, 'h_top':BLT.z-FRB.z, 'ratio':roof_h/aabb.z }


class KeySizeSpec:
	# defaults to 1U MX spacing
	
	def __init__(self, units:Vec2=Vec2(1,1), spacing:Vec2=Vec2(19.05,19.05)):
		self.units:Vec2 =	units
		self.spacing:Vec2 =	spacing
	
	def clone(self, units=None, spacing=None):
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new
	
	def __deepcopy__(self, memo=None):
		if memo is None:
			memo = {}
		return KeySizeSpec(deepcopy(self.units,memo), deepcopy(self.spacing,memo))
	
	def __str__(self):
		return "KeySizeSpec(units={0},spacing={1})".format(self.units, self.spacing)
	
	def getCoreSize(self):
		return Vec2(max(0,self.units.x-1)*self.spacing.x, max(0,self.units.y-1)*self.spacing.y)
	
	def getFullSize(self):
		return Vec2(self.units.x*self.spacing.x, self.units.y*self.spacing.y)



class KeyMountSpec:
	
	def __init__(self, mxMount:bool=True, mxStem:bool=True, stab:bool=True, stabIsPOS:bool=False):
		self.mxMount: bool =	mxMount		# false = kailh choc v1
		self.mxStem: bool =		mxStem		# false = kailh choc v1
		self.stab: bool =		stab
		self.stabIsPOS: bool =	stabIsPOS	# use POS style stabilizers
	
	def clone(self, mxMount=None, mxStem=None, stab=None, stabIsPOS=None):
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new
	
	def __deepcopy__(self, memo=None):
		return KeyMountSpec(deepcopy(self.mxMount), deepcopy(self.mxStem), deepcopy(self.stab), deepcopy(self.stabIsPOS))
	
	def __str__(self):
		return "KeyMountSpec(mxMount={0},mxStem={1},stab={2},stabIsPOS={3})".format(self.mxMount, self.mxStem, self.stab, self.stabIsPOS)



class KeyMarkShape(Enum):
	CUSTOM =	-1
	NONE =		0
	DOTS =		1
	LINE =		2
	WINDOWS =	3
	RING =		4
	POLYGON =	5
	DISH =		6
	FMTOWNS =	7	# line "ridge" as seen on Fujitsu FMT-KB205
	HEXARRAY =	8	# see vardera choc profile



class KeyMarkSpec:
	
	def __init__(self, shape=KeyMarkShape.NONE, count=2, size=2, depth=0.5, offset=Vec2(), rotation=Vec2()):
		self.shape: KeyMarkShape =	shape
		self.count: int =		max(1, count)		# dots count, polygon edges
		self.size: float =		size		# radius for dot ring, windows/dish, solid ring; spacing for hexarray
		self.depth: float =		depth		# thickness for lines, radius for spheres, height for windows/dish
		self.offset: Vec2 =		offset		# multiplier for keytop size
		self.rotation: Vec2 =	rotation	# in degrees
	
	def clone(self, shape=None, count=None, size=None, depth=None, offset=None, rotation=None):
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new
	
	def __deepcopy__(self, memo=None):
		if memo is None:
			memo = {}
		return KeyMarkSpec(deepcopy(self.shape), deepcopy(self.count), deepcopy(self.size), deepcopy(self.depth), deepcopy(self.offset,memo), deepcopy(self.rotation,memo))
	
	def __str__(self):
		return "KeyMarkSpec(shape={0},count={1},size={2},depth={3},offset={4},rotation={5})".format(
			self.shape, self.count, self.size, self.depth, self.offset, self.rotation)