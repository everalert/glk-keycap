import cadquery as cq
import keycap as kc
from keycap.helper import KeySizeSpec, KeyMountSpec, KeyMarkSpec, KeyMarkShape
from keycap.vector import Vec2, Vec3
from keycap.spec import KeySpec
from keycap.body import KeyBody

'''
Galeforce Keycap Profile (GLK)

An MX-spaced, low-profile, semi-spherical, sculpted keycap
inspired by the lack of OEM-style keycaps for low-profile
switches. This profile aims to replicate the OEM feel, while
adding a little spice inspired by other profiles.

Use profile() to generate a full set with official specs,
or keycap() to fully customize a single cap
'''

# TODO
#	- hollowing out the upper part to save plastic
#	- fix scoop generation
# FUTURE TODO
#	- fix mx measurements (skirt shape, etc.)
#	- proper stab array for keys 2x2+
#	- costar stab
#	- other homing mark options
#   - confirm mount/stem-related dimensions
#	- separating out profile generation so you can output keycaps for only one kb


# generate all unique keys required for GLFC, ErgoDox and 100% keyboards
def profile(mx:bool=False):
	df = defaults()
	u, size = df.size.units, df.body.size
	# size = df.body.size
	rows = {
		'R4':	{ 'top': {'angle':-2.5},	'body': {'size':size.clone(z=8)}	},	# row4, num row + function row
		'R3':	{ 'top': {'angle':4.25},	'body': {'size':size.clone(z=6.5)}	},	# row3, qwerty
		'R2':	{ 'top': {'angle':9},		'body': {'size':size.clone(z=6.5)}	},	# row2, home row
		'R1':	{ 'top': {'angle':13},		'body': {'size':size.clone(z=7)}	},	# row1, shift/mod row
	}
	keys = {
		'R4': [
			{ 'size':{'units':u.clone(x=1)},	'top': {'ratio':0.6,'convex':True},	'edge':{'top':0.15},	"PROFILELABEL":"convex" },		# GLFC inner key (+/-)
			{ 'size':{'units':u.clone(x=1.15)} },															# GLFC wide tilde
			{ 'size':{'units':u.clone(x=1.50)} },															# ErgoDox wide tilde
			# { 'size':{'units':u.clone(x=1.50)},	"unitX":1.50, "height":-1.5,							"PROFILELABEL":"glthumb1" },
			{ 'size':{'units':u.clone(x=2)} },																# 100% backspace
		],
		'R3': [
			{ 'size':{'units':u.clone(x=1)},	'top': {'ratio':0.6,'convex':True},	'edge':{'top':0.15},	"PROFILELABEL":"convex" },		# GLFC inner key (layer-shift)
			{ 'size':{'units':u.clone(x=1.50)} },																							# tab/pipe
			{ 'size':{'units':u.clone(x=1.50)},	'top': {'convex':True},	'edge':{'top':0.15},				"PROFILELABEL":"glthumb1" },
			{ 'size':{'units':u.clone(x=2)},																"PROFILELABEL":"doxthumb" },
			{ 'size':{'units':u.clone(y=2)},																"PROFILELABEL":"numplen" },		# numpad plus and enter
		],
		'R2': [
			{ 'size':{'units':u.clone(x=1)},	'mark':{'shape':KeyMarkShape.DOTS},							"PROFILELABEL":"home" },		# homing key, numpad 5
			{ 'size':{'units':u.clone(x=1.50)} },															# GLFC/ErgoDox side key
			{ 'size':{'units':u.clone(x=1.50)},	'top': {'convex':True},	'edge':{'top':0.15}, 'body': {'size':size.clone(z=7)},				"PROFILELABEL":"glthumb2" },
			{ 'size':{'units':u.clone(x=1.75)},																"PROFILELABEL":"caps" },
			{ 'size':{'units':u.clone(x=2.25)},																"PROFILELABEL":"enter" },
		],
		'R1': [
			{ 'size':{'units':u.clone(x=1)},	'mark':{'shape':KeyMarkShape.DOTS,'count':1},				"PROFILELABEL":"numhome" },		# numpad . 
			{ 'size':{'units':u.clone(x=1.25)} },
			{ 'size':{'units':u.clone(x=1.25)},	'mark':{'shape':KeyMarkShape.WINDOWS},						"PROFILELABEL":"windows" },
			{ 'size':{'units':u.clone(x=2)},																"PROFILELABEL":"num0" },
			{ 'size':{'units':u.clone(x=2.25)},																"PROFILELABEL":"LShift" },
			{ 'size':{'units':u.clone(x=2.75)},																"PROFILELABEL":"RShift" },
			{ 'size':{'units':u.clone(x=2)},	'top': {'angle':9,'ratio':0.6,'convex':True}, 'edge':{'top':0.15},	"PROFILELABEL":"space" },		# GLFC spacebar
			{ 'size':{'units':u.clone(x=6.25)},	'top': {'angle':9,'ratio':0.6,'convex':True}, 'edge':{'top':0.15},	"PROFILELABEL":"space" },		# 100% spacebar
		],
	}
	def spec2MX(spec):
		# skirt height dif 2.5 preplate, 2.9 plate-length skirt ; where did 1.9 come from?
		# also mx being significantly taller weakens effect of curved wall
		spec.body.size += Vec3(0,0,2.9)
		spec.mount = spec.mount.clone(mxMount=True,mxStem=True)
		return spec
	def apply2spec(spec,params):
		new = spec.clone()
		for key in set(keycap.__code__.co_varnames)&set(params):
			setattr(new, key, getattr(new,key).clone(**params.get(key)))
		return new
	def makeUnitStr(spec):
		return str(round(spec.size.units.x*100))+"x"+str(round(spec.size.units.y*100))
	def makeLabel(spec, rk='R2', mx=False, k={}):
		return 'GLK_{0}_{1}_{2}{3}'.format('MX' if mx else 'KL', rk, makeUnitStr(spec), "_"+k["PROFILELABEL"] if "PROFILELABEL" in k else "")

	keycaps = {}
	for rk in rows.keys():
		rspec = apply2spec(df, rows[rk])
		if mx: rspec = spec2MX(rspec)
		keycaps |= { makeLabel(rspec, rk, mx): keycap(**vars(rspec)) }
		for k in keys[rk]:
			kspec = apply2spec(rspec, k)
			keycaps |= { makeLabel(kspec, rk, mx, k): keycap(**vars(kspec)) }

	return keycaps

	
# full keycap customization; defaults to a 1U home row key
def keycap(
	size:KeySizeSpec = KeySizeSpec(),
	body:KeyBody = KeyBody(
		size=Vec3(18.1, 18.1, 6.5),
		curve=18,
		offset=Vec2(y=0.85),
		angle=9,
		depth=2.5,
		ratio=1.25,
		convex=False,
		corner=Vec2(4.0, 1.5),
		edge=Vec2(0.3,0.3),
	),
	mount:KeyMountSpec = KeyMountSpec(
		mxMount=False,
		mxStem=False,
		stab=True,
		stabIsPOS=False,
	),
	mark:KeyMarkSpec = KeyMarkSpec(
		shape=KeyMarkShape.NONE,
		offset=Vec2(y=1.0/6),
	),
):
	
	spec:KeySpec =	KeySpec(**locals())
	
	
	# CORE SHAPE
	
	core = body.makeCore(size.getCoreSize())
	scoop = body.makeScoop(size.getCoreSize()).translate((0, -body.offset.y, body.height))

	keycap = core - scoop
	keycap = body.applyEdgeFinish(keycap, size)


	# HOMING/WIN-KEY FEATURES

	if mark.shape == KeyMarkShape.WINDOWS:
		keycap = kc.homing.addInsetBulb(keycap, spec)
	if mark.shape == KeyMarkShape.DOTS:
		keycap = kc.homing.addDots1(keycap, spec)

	
	# MOUNT CUTOUT
	
	mountH = kc.mount.getSkirtHeight(mount.mxMount, False)
	mountCut = kc.mount.makeCherryNeg(spec.size) if mount.mxMount else kc.mount.makeChocNeg(spec.size)
	mountTopCut = kc.mount.makeTopNeg(spec)

	keycap -= (mountCut+mountTopCut)
	
	
	# STEM / STABILIZER
	
	stem = (kc.mount.makeCherryStem(isBox=True) if mount.mxMount else kc.mount.makeChocStem()).translate((0, 0, mountH))

	if mount.stab and mount.stabIsPOS:
		keycap += kc.stabilizer.makePOSStabilizer1(stem, size)
	elif mount.stab and kc.stabilizer.canStabilize1(size.units):
		keycap += stem + kc.stabilizer.makeStabilizer1(spec).translate((0, 0, mountH))
	else:
		keycap += stem
	
	
	# OUTPUT
	
	return keycap

def defaults():
	return KeySpec(**{keycap.__code__.co_varnames[n]: keycap.__defaults__[n].clone() for n in range(keycap.__code__.co_argcount)})