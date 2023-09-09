from cadquery import selectors as sel
import cadquery as cq
from keycap import body, homing, mount, stabilizer

'''
Galeforce Simplified Keycap Profile (GLK-S)

Minimalist GLK keycaps with skirt and other
unnecessary material removed.
'''


#TODO:
# - fix 2U space breaking at 2.5 (default) depth
# - fix 6.25U space breaking at 13 angle


# generate all unique keys required for GLFC, ErgoDox and 100% keyboards
def profile(mx:bool=False):
	rows = [
		{ "scoopAngle":-2.5,	"height":4.7,	"ROWLABEL":"R4" },		# row4, num row + function row
		{ "scoopAngle":3,		"height":3.2,	"ROWLABEL":"R3" },		# row3, qwerty
		{ "scoopAngle":9,		"height":3.2,	"ROWLABEL":"R2" },		# row2, home row
		{ "scoopAngle":13,		"height":3.7,	"ROWLABEL":"R1" },		# row1, shift row + mod row
	]
	keys = [
		[
			{ "unitX":1 },
			{ "unitX":1, "scoopRatio":0.6, "scoopConvex":True,		"PROFILELABEL":"convex" },		# GLFC inner key (+/-)
			{ "unitX":1.15 },										# GLFC wide tilde
			{ "unitX":1.50 },										# ErgoDox wide tilde
			# { "unitX":1.50, "height":-1.5,							"PROFILELABEL":"glthumb1" },
			{ "unitX":2 },											# 100% backspace
		],
		[
			{ "unitX":1 },
			{ "unitX":1, "scoopRatio":0.6, "scoopConvex":True,		"PROFILELABEL":"convex" },		# GLFC inner key (layer-shift)
			{ "unitX":1.50 },										# tab/pipe
			{ "unitX":2,											"PROFILELABEL":"doxthumb" },
			{ "unitY":2,											"PROFILELABEL":"numplen" },		# numpad plus and enter
		],
		[
			{ "unitX":1 },
			{ "unitX":1,	"isHoming":True,						"PROFILELABEL":"home" },		# homing key, numpad 5
			{ "unitX":1.50 },										# GLFC/ErgoDox side key
			{ "unitX":1.75,											"PROFILELABEL":"caps" },
			{ "unitX":2.25,											"PROFILELABEL":"enter" },
		],
		[
			{ "unitX":1 },
			{ "unitX":1,    "isHoming":True,   "homeDotCnt":1,		"PROFILELABEL":"numhome" },	# numpad . 
			{ "unitX":1.25 },
			{ "unitX":1.25, "isOS":True,							"PROFILELABEL":"windows" },
			{ "unitX":2,											"PROFILELABEL":"num0" },
			{ "unitX":2.25,											"PROFILELABEL":"LShift" },
			{ "unitX":2.75,											"PROFILELABEL":"RShift" },
			{ "unitX":2,    "scoopRatio":0.6, "scoopConvex":True, "scoopDepth":2.4, "scoopAngle":11.5, "PROFILELABEL":"space" },		# GLFC spacebar
			{ "unitX":6.25, "scoopRatio":0.6, "scoopConvex":True, "scoopDepth":2.4, "scoopAngle":11.5, "PROFILELABEL":"space" },		# 100% spacebar
		],
	]

	def args2MX(args:dict):
		MX = { "mountIsMX":True, "stemIsMX":True } # don't need height offset because there is no skirt
		return { k: args.get(k,0)+MX.get(k,0) if type(args.get(k)) not in [bool, str] else MX.get(k) if k in MX else args.get(k) for k in set(args)|set(MX) }
	
	keycaps = {}
	prefix = "GLKS_"
	prefix += "MX_" if mx else "KL_"
	for i, r in enumerate(rows):
		for k in keys[i]:
			label = prefix + r["ROWLABEL"]+"_"
			args = r|k if not mx else args2MX(r|k)
			label += str(round(args.get("unitX",1)*100))+"x"+str(round(args.get("unitY",1)*100))+("_"+k["PROFILELABEL"] if "PROFILELABEL" in k else "")
			args = { k: args.get(k) for k in set(keycap.__code__.co_varnames)&set(args) }
			keycaps |= { label: keycap(**args) }
	
	return keycaps

	
# full keycap customization; defaults to a 1U home row key
def keycap(
	unitX: float = 1,			# U size
	unitY: float = 1,
	base: float = 18.1,			# 1U size of base (mm); not switch spacing
	topW: float = 12.4,
	topH: float = 14.4,
	topOff: float = 0.85,		# vertical stagger of top (mm)
	baseFil: float = 1.5,		# wall base fillet (mm)
	topFil: float = 4,			# wall top fillet (mm)
	height: float = 3.2,		# Height of the keycap before cutting the scoop (final height is lower)
	scoopAngle: float = 9,		# Angle of the top surface
	scoopDepth: float = 2.5,	# Scoop depth
	scoopRatio: float = 1.25,	# scoop cylinder-ness; 1=spherical, >1=y-cylindrical, <1=x-cylindrical
	scoopConvex: bool = False,	# spacebar-like inverted scoop?
	wallCurve: float = 15,		# sides bowing factor; 0=no bowing, <0=concave, >0=convex
	isHoming: bool = False,
	homeIsSolid: bool = False,	# use solid circle instead of dot ring
	homeDotCnt: float = 2,		# number of dots
	homeRad: float = 2,			# ring radius (mm)
	homeDotRad: float = 0.35,	# dot radius (mm)
	isOS: bool = False,
	mountIsMX: bool = False,	# false = kailh choc v1
	stemIsMX: bool = False,		# false = kailh choc v1
	stab: bool = True,
	stabIsPOS: bool = False,	# use POS style stabilizers
):
	
	# STATIC AND DERIVED SETTINGS
	
	uX: float = 19.05			# 1U size in mm
	uY: float = 19.05

	wallCurveMax: float = 50
	wallCurve = max(-wallCurveMax, min(wallCurveMax, wallCurve))

	scoopAngleMax: float = 20
	scoopAngle = max(-scoopAngleMax, min(scoopAngleMax, scoopAngle))

	homeDotCnt = max(1, homeDotCnt)
	
	edgeTopChm = 0.3 if not scoopConvex else 0.1
	edgeBotFil = 0.45
	
	botX = uX*unitX + base-uX
	botY = uY*unitY + base-uY
	topX = uX*unitX + topW-uX
	topY = uY*unitY + topH-uY
	midX = uX*unitX + (base+topW)/2-uX
	midY = uY*unitY + (base+topH)/2-uY
	midFil = (baseFil+topFil)/2

	mountH = mount.getCherrySkirtHeight(True) if mountIsMX else mount.getChocSkirtHeight()

	ceilAng = 90/4
	ceilDia = 8
	ceilX = ceilDia + stabilizer.getStabLen(unitX, uX, mountIsMX, stabIsPOS) - 1.5*(unitX>=2)
	ceilY = ceilDia + stabilizer.getStabLen(unitY, uY, mountIsMX, stabIsPOS) - 1.5*(unitY>=2)

	coreH = (height+mountH+scoopDepth*2)*2
	scoopH = 1.6

	
	# CORE SHAPE
	
	# core = body.makeCore(topX, topY, botX, botY, height+mountH, wallCurve, scoopAngle, topOff, topFil, baseFil)
	core = cq.CQ( cq.Solid.makeBox(midX,midY,coreH,(-midX/2,-midY/2,-coreH/2),(0,0,1)) ).edges("|Z").fillet(midFil)
	
	scoop_plane =	body.makeScoop(scoopAngle, scoopDepth, scoopRatio, botX, botY, scoopConvex, planeOnly=True).translate((0, -topOff, height+mountH/2))
	scoop_face =	core.intersect(scoop_plane).translate((0,0,-mountH/2))
	scoop_wire1 =	scoop_face.translate((0,0,-scoopH)).wires().val()
	scoop_wire2 =	scoop_face.wires().val()
	scoop =			(
		cq.CQ(cq.Solid.makeLoft([scoop_wire1,scoop_wire2]))
		.faces(sel.NearestToPointSelector((0, -topOff, height+0.1))).edges().chamfer(edgeTopChm)
		.faces(sel.NearestToPointSelector((0, 0, -0.1))).edges().fillet(edgeBotFil)
	)
	scoopTopFace = cq.CQ(scoop.faces(sel.NearestToPointSelector((0, -topOff, height+0.1))).val())
	scoopBotFace = cq.CQ(scoop.faces(sel.NearestToPointSelector((0, 0, -0.1))).val())
	
	ceil_rect =			cq.CQ("XY").rect(ceilX,ceilY)
	ceil_path =			ceil_rect.val().fillet2D(ceilDia/4, ceil_rect.vertices().vals())
	ceil_core = 		core - ( cq.CQ("YZ")
		.moveTo(max(midX,midY), -coreH-0.0001)
		.hLineTo(ceilY/2)
		.vLineTo(0)
		.polarLine(coreH*2, 90-ceilAng)
		.hLineTo(max(midX,midY))
		.close().sweep(ceil_path)
	) - core.translate((0,0,-coreH/2))
	ceilscoop_wire1 =	scoop_face.translate((0,0,-coreH)).wires().val()
	ceilscoop_wire2 =	scoop_face.translate((0,0,-scoopH/2)).wires().val()
	ceilscoop_loft =	cq.CQ(cq.Solid.makeLoft([ceilscoop_wire1,ceilscoop_wire2], True))
	ceil =				ceil_core.intersect(ceilscoop_loft)

	keycap = scoop + ceil


	# HOMING/WIN-KEY FEATURES
	
	if isOS:
		keycap = homing.addWinBulb(keycap, height, topOff, scoopAngle, scoopConvex)
		
	if isHoming:
		keycap = homing.addDots(keycap, homeDotCnt, homeDotRad, homeRad, height, topOff, scoopAngle)
	
	
	# MOUNT CUTOUT
	
	cutoutH = 0
	cutout = None
	mountMinX = stabilizer.getMinNegU(stabilizer.getStabLen(unitX, uX, mountIsMX, stabIsPOS), uX)
	mountMinY = stabilizer.getMinNegU(stabilizer.getStabLen(unitY, uY, mountIsMX, stabIsPOS), uY)
	if mountIsMX:
		cutoutH = mount.getCherrySkirtHeight(True)
		cutout = mount.makeCherryNegative(uX, mountMinX, uY, mountMinY)
	else:
		cutoutH = mount.getChocSkirtHeight(False)
		cutout = mount.makeChocNegative(uX, mountMinX, uY, mountMinY)

	keycap -= cutout.translate((0,0,-mountH))
	
	
	# STEM / STABILIZER
	
	stem = mount.makeCherryStem() if stemIsMX else mount.makeChocStem()
	if stabIsPOS:
		keycap += stabilizer.makePOSStabilizer(stem, uX, unitX, uY, unitY)
	elif stab and stabilizer.canStabilize(unitX, unitY):
		keycap += stem + stabilizer.makeStabilizer(unitX, unitY, not mountIsMX)
	else:
		keycap += stem
	
	
	# OUTPUT
	
	return keycap
	# return {0:keycap,1:core,2:scoop_plane,3:scoopTopFace,4:scoopBotFace,5:scoop}