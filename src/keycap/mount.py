from cadquery import selectors as sel
import cadquery as cq
import math
from keycap.spec import KeySpec
from keycap.vector import Vec2, Vec3
from keycap.helper import KeySizeSpec, makeDraftedCylinder, makeDraftedBlock, makeRoundRectWire, makeRoundDraftedBlock
from keycap import body


# TODO
# - non-preplate MX
# - options to select for preplate ver on negatives
# - options to generate upper hollowing on negatives
# - double check clearances, particularly choc
# - draft angles for injection molding compatibility
# - alps/matias
# - add clearance to bottom of skirt? (check to see how it currently meets plate first)
# - redo cherry negative; current one based on official keycap spec doesn't even get close to plate

MX_STEM_H = 3.8
MX_STAB_H = 3.8
KL_STEM_H = 3.8
KL_STAB_H = 2.2

def getCherryGap(unit:float=2):
	return (unit-1)/2*19.05 if unit>=3 else 1.25/2*19.05 if unit>=2 else 0

def getChocGap(unit:float=2):
	return 76.00/2 if unit>=6.25 else 24.00/2 if unit>=2 else 0


# CHERRY MX

def makeCherryStem(thin:float=1.17, long:float=4.10, h:float=3.8, d:float=5.5, padding:float=0.1, tolerance:float=0.06, isBox:bool=False): 
	extentW = thin+tolerance*2
	extentL = long+tolerance*2
	MXstem = (
		cq.Workplane("XY")
		.circle(d/2)
		.extrude(-(h+padding))
	)
	MXstemCut = (
		cq.Workplane("XY")
		.rect(extentW, extentL)
		.rect(extentL, extentW)
		.clean()
		.extrude(-(h+padding))
		.edges(sel.BoxSelector((-thin,-thin,0),(thin,thin,-(h+padding))))
		.fillet(0.45)
	)
	MXstem = (
		MXstem.cut(MXstemCut)
		.edges("<Z").chamfer(0.2)
		.translate((0, 0, padding))
	)
	if isBox: MXstem = MXstem.intersect((
		cq.Workplane("XY")
		.rect(d, long)
		.extrude(-(h+padding))
	))
	return MXstem

def makeCherrySupport(height:float=10, d=5.5, long=4.10, margin:float=0.2, draft:float=1.5, isBox:bool=False):
	core = makeDraftedCylinder(d/2+margin, height, draft)
	if isBox: core = core.intersect(makeDraftedBlock(d+margin*2, long+margin*2, height, draft))
	return core

def getCherrySize(sizeSpec=KeySizeSpec(), clearance=0.0):
	# z = fillet
	return Vec3(15.4+clearance,15.4+clearance,1.75) + sizeSpec.getCoreSize()

def makeCherryNegative(uX:float, unitX:float, uY:float, unitY:float, padding:float=0.1):
	#TODO: non-preplate skirt
	# based on official cherry mx docs;
	# unsure if good for all MX switches tho.
	# pre-plate skirt length
	sizeX = (uX*unitX-(uX-15.4))
	sizeY = (uY*unitY-(uY-15.4))
	rect = cq.Workplane("XY").rect(sizeX, sizeY)
	cnr = rect.vertices().vals()
	path = rect.val().fillet2D(1.75, cnr) # fillet val not confirmed
	shape = (
		cq.Workplane("XZ")
		.moveTo(-uX*unitX/2, 0)
		.hLineTo(-sizeX/2)
		.line(0, padding) # make sure the cut clears the keycap base
		.line(0, 1.2) # plate mount rim (width not finalized)
		.line(0.39496, 3) # tier1
		.line(1.1547, 2) # tier2
		.hLineTo(-uX*unitX/2)
		.close()
		.sweep(path)
	)
	solid = cq.Solid.extrudeLinear(cq.Face.makeFromWires(path), cq.Vector(0,0,padding+5+1.2))
	return (cq.CQ(solid)-shape).translate((0,0,-padding))

def makeCherryNegative1(keySize=KeySizeSpec(), padding:float=0.1):
	#TODO: non-preplate skirt
	# based on official cherry mx docs;
	# unsure if good for all MX switches tho.
	# pre-plate skirt length
	clearance:float = 0.0
	size = keySize.getCoreSize() + Vec2(15.4+clearance, 15.4+clearance)
	sizeF = keySize.getFullSize()
	path = makeRoundRectWire(size.x, size.y, 1.75) # fillet val not confirmed
	shape = (
		cq.Workplane("XZ")
		.moveTo(-sizeF.x/2, 0)
		.hLineTo(-size.x/2)
		.line(0, padding) # make sure the cut clears the keycap base
		.line(0, 1.2) # plate mount rim (width not finalized)
		.line(0.39496, 3) # tier1
		.line(1.1547, 2) # tier2
		.hLineTo(-sizeF.x/2)
		.close()
		.sweep(path)
	)
	solid = cq.Solid.extrudeLinear(cq.Face.makeFromWires(path), cq.Vector(0,0,padding+5+1.2))
	return (cq.CQ(solid)-shape).translate((0,0,-padding))

makeCherryNeg = makeCherryNegative1

def getCherrySkirtHeight(preplate:bool=False):
	return 5.0 + (1.2 if not preplate else 0)


# KAILH CHOCOLATE V1

def makeChocStem(thin:float=1.2, long:float=3.0, gap:float=5.7, h:float=3.8, padding:float=0.1, tolerance:float=0.035):
	extentX = thin/2-tolerance
	extentY = long/2-tolerance
	CHstem = (
		cq.Workplane("XY")
		.moveTo(0, -extentY)
		.lineTo(extentX, -extentY)
		.lineTo(extentX, -extentY+extentX)
		.threePointArc((extentX*0.65, 0), (extentX, extentY-extentX))
		.lineTo(extentX, extentY)
		.lineTo(0, extentY)
		.mirrorY()
		.extrude(-(h+padding))
		.edges("|Z")
		.fillet(extentX/1.5)
		.edges("<Z")
		.chamfer(extentX/3)
	)
	return CHstem.translate((gap/2, 0, padding)) + CHstem.translate((-gap/2, 0, padding))

def makeChocSupport(height=10, margin=1.2, fillet=1, draft=1.5):
	size = Vec2(5.7+1.2+margin*2, 3.0+margin*2)
	return makeRoundDraftedBlock(size.x, size.y, height, fillet, draft)

def getChocSize(sizeSpec=KeySizeSpec(), clearance=0.7):
	# z = fillet
	return Vec3(15.2+clearance,15.2+clearance,2.0) + sizeSpec.getCoreSize()

def makeChocNegative(uX:float, unitX:float, uY:float, unitY:float, padding:float=0.1):
	# kailh choc v1
	# (non-pre) plate skirt length
	clearance:float = 0.7
	sizeX = (uX*unitX-(uX-15.2))+clearance
	sizeY = (uY*unitY-(uY-15.2))+clearance
	rect = cq.Workplane("XY").rect(sizeX, sizeY)
	cnr = rect.vertices().vals()
	path = rect.val().fillet2D(2, cnr) # fillet val not confirmed
	shape = (
		cq.Workplane("XZ")
		.moveTo(-uX*unitX/2, 0)
		.hLineTo(-sizeX/2)
		.line(0, padding) # make sure the cut clears the keycap base
		.line(0, 0.8) # plate mount rim
		.line(0.3, 2) # tier1
		.line(0.4, 0.5) # tier2
		.hLineTo(-uX*unitX/2)
		.close()
		.sweep(path)
	)
	solid = cq.Solid.extrudeLinear(cq.Face.makeFromWires(path), cq.Vector(0,0,padding+2.5+0.8))
	return (cq.CQ(solid)-shape).translate((0,0,-padding))

def makeChocNegative1(keySize=KeySizeSpec(), padding:float=0.1):
	# return makeChocNegative(keySize.spacing.x, keySize.units.x, keySize.spacing.y, keySize.units.y, padding)
	# kailh choc v1
	# (non-pre) plate skirt length
	clearance:float = 0.7
	size = keySize.getCoreSize() + Vec2(15.2+clearance, 15.2+clearance)
	sizeF = keySize.getFullSize()
	path = makeRoundRectWire(size.x, size.y, 2.0) # fillet val not confirmed
	shape = (
		cq.Workplane("XZ")
		.moveTo(-sizeF.x/2, 0)
		.hLineTo(-size.x/2)
		.line(0, padding) # make sure the cut clears the keycap base
		.line(0, 0.8) # plate mount rim
		.line(0.3, 2) # tier1
		.line(0.4, 0.5) # tier2
		.hLineTo(-sizeF.x/2)
		.close()
		.sweep(path)
	)
	solid = cq.Solid.extrudeLinear(cq.Face.makeFromWires(path), cq.Vector(0,0,padding+2.5+0.8))
	return (cq.CQ(solid)-shape).translate((0,0,-padding))

makeChocNeg = makeChocNegative1

def getChocSkirtHeight(preplate:bool=False):
	return 2.5 + (0.8 if not preplate else 0)


# MISC

def getSkirtHeight(cherry:bool=False, preplate:bool=False):
	return getCherrySkirtHeight(preplate) if cherry else getChocSkirtHeight(preplate)


# POS STEMS

def makePOSStems(stem, uX:float, unitX:float, uY:float, unitY:float):
	numX = math.floor(unitX)
	numY = math.floor(unitY)
	startX = -(numX-1)*uX/2
	startY = -(numY-1)*uY/2
	points = []
	for x in range(numX):
		for y in range(numY):
			points.append((startX+uX*x, startY+uY*y))
	pos = (cq.CQ()
		.pushPoints(points)
		.eachpoint(lambda loc: stem.val().located(loc))
	)
	return pos

def getPOSPoints(size:KeySizeSpec=KeySizeSpec()) -> list[Vec2]:
	numX = math.floor(size.units.x)
	numY = math.floor(size.units.y)
	startX = -(numX-1)*size.spacing.x/2
	startY = -(numY-1)*size.spacing.y/2
	points = []
	for x in range(numX):
		for y in range(numY):
			points.append(Vec2(startX+size.spacing.x*x, startY+size.spacing.y*y))
	return points

def makePOSStems1(stem, size:KeySizeSpec=KeySizeSpec()):
	points = [p.toTuple() for p in getPOSPoints(size)]
	return ( cq.CQ()
		.pushPoints(points)
		.eachpoint(lambda loc: stem.val().located(loc))
	)


# TOP CUTOUT

def makeTopNegative(spec=KeySpec(), thickness:float=1.2):
	ks:KeySpec = spec
	skirtH = getSkirtHeight(ks.mount.mxMount, False)
	sizeU = ks.size.getFullSize()

	negative = makeCherryNeg(ks.size) if ks.mount.mxMount else makeChocNeg(ks.size)
	neg_face = negative.faces(sel.NearestToPointSelector((0, 0, skirtH)))
	neg_wire = cq.Wire.assembleEdges(neg_face.val().Edges())
	neg_extrude = cq.CQ(cq.Solid.makeLoft([neg_wire.translate((0,0,-0.1)), neg_wire.translate((0,0,ks.body.height))], True))

	ks_inner = ks.clone()
	ks_inner.body.base -= Vec2(x=thickness*2, y=thickness*2)
	ks_inner.body.top -= Vec2(thickness*2, thickness*2)
	ks_inner.body.corner = Vec2(max(0.01,ks_inner.body.corner.x-thickness), max(0.01,ks_inner.body.corner.y-thickness))
	coretest = ks_inner.body.makeCore(ks_inner.size.getCoreSize())
	scooptest = ks.body.makeScoop(ks_inner.size.getCoreSize(), extraHeight=thickness*2).translate((0, 0, ks.body.height-thickness))

	base = neg_extrude.intersect(coretest-scooptest)

	mxSupport = makeCherrySupport(height=ks.body.height, margin=thickness/6, isBox=True, long=4.1 if spec.mount.mxMount else 4.0)
	support = makeCherrySupport(height=ks.body.height, margin=thickness/6, isBox=True) if ks.mount.mxMount else makeChocSupport(height=ks.body.height)
	xSupport = makeDraftedBlock(sizeU.x, thickness, ks.body.height)
	ySupport = makeDraftedBlock(thickness, sizeU.y, ks.body.height)
	gapX = getCherryGap(spec.size.units.x) if spec.mount.mxMount else getChocGap(spec.size.units.x)
	gapY = getCherryGap(spec.size.units.y) if spec.mount.mxMount else getChocGap(spec.size.units.y)
	stabX = (mxSupport+ySupport).translate((gapX,0,0))+(mxSupport+ySupport).translate((-gapX,0,0))
	stabY = (mxSupport+xSupport).translate((0,gapY,0))+(mxSupport+xSupport).translate((0,-gapY,0))
	stabSupport = cq.CQ("XY").add(stabX+stabY if gapX and gapY else stabX if gapX else stabY)
	support += xSupport + ySupport + stabSupport


	return base - support.translate((0,0,skirtH)).edges("<Z").chamfer(thickness/6)

makeTopNeg = makeTopNegative