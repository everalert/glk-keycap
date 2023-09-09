import cadquery as cq
from keycap import mount
from keycap.spec import KeySpec
from keycap.helper import KeySizeSpec
from keycap.vector import Vec2
import math



#TODO: MERGE ALL THIS SHIT INTO mount.py



# STABILIZER

#TODO: proper stab array (not just 1x2+2x1 stabs) for keys 2x2+
#TODO: costar stab
#TODO: confirm spacing of cherry 2U stabs
#TODO: fix getMinNegU; confirm correct required stab spacing
#TODO: confirm and fix choc vertical stab offset

def getCherryGap(unit:float=2):
	return (unit-1)/2*19.05 if unit>=3 else 1.25/2*19.05 if unit>=2 else 0

def getChocGap(unit:float=2):
	return 76.00/2 if unit>=6.25 else 24.00/2 if unit>=2 else 0

def getStabLen(unit:float=2, u:float=19.05, mx:bool=False, pos:bool=False):
	return math.floor(unit-1)*u if pos else 2*(getCherryGap(unit) if mx else getChocGap(unit))


def getMinNegU(gap:float=0, size:float=19.05):
	qU = size/4
	return max(1,math.floor(gap/qU)/4+0.75)


def canStabilize(unitX:float=1, unitY:float=1):
	return unitX >= 2 or unitY >= 2

def canStabilize1(units:Vec2=Vec2(1,1)):
	return units.x >= 2 or units.y >= 2


def makeStabilizer(unitX:float=2, unitY:float=2, chocMount:bool=False):
	stem = mount.makeCherryStem(isBox=True) if not chocMount else mount.makeCherryStem(isBox=True, thin=1.0, long=4.0, h=2.2)
	gapX = getCherryGap(unitX) if not chocMount else getChocGap(unitX)
	gapY = getCherryGap(unitY) if not chocMount else getChocGap(unitY)
	stabX = stem.translate((gapX,0,0))+stem.translate((-gapX,0,0))
	stabY = stem.translate((0,gapY,0))+stem.translate((0,-gapY,0))
	return cq.CQ("XY").add(stabX+stabY if gapX and gapY else stabX if gapX else stabY)

def getStabPoints(spec:KeySpec=KeySpec()) -> list[Vec2]:
	gapX = getCherryGap(spec.size.units.x) if spec.mount.mxMount else getChocGap(spec.size.units.x)
	gapY = getCherryGap(spec.size.units.y) if spec.mount.mxMount else getChocGap(spec.size.units.y)
	stabX = [Vec2(gapX,0), Vec2(-gapX,0)]
	stabY = [Vec2(0,gapY), Vec2(0,-gapY)]
	return stabX+stabY if gapX and gapY else stabX if gapX else stabY

def makeStabilizer1(spec:KeySpec=KeySpec()):
	stem = mount.makeCherryStem(isBox=True) if spec.mount.mxMount else mount.makeCherryStem(isBox=True, thin=1.0, long=4.0, h=2.2)
	stab, points = cq.CQ("XY"), getStabPoints(spec)
	for p in points:
		stab.add(stem.translate(p.toVec3().toTuple()))
	return stab

makeStab = makeStabilizer1

def makeStabilizerSupport(spec:KeySpec=KeySpec()):
	stem = mount.makeCherrySupport(height=spec.body.height, isBox=True, long=4.1 if spec.mount.mxMount else 4.0)
	supp, points = cq.CQ("XY"), getStabPoints(spec)
	for p in points:
		supp.add(stem.translate(p.toVec3().toTuple()))
	return supp

makeStabSupport = makeStabilizerSupport

def makeCostarStabilizer():
	# keycap-mounted wire, like filco
	pass

def makePOSStabilizer(stem, uX:float, unitX:float, uY:float, unitY:float):
	# stems that go into multiple switches, rather than a separate construction
	# also what does POS stand for? surely not point-of-sale?
	return mount.makePOSStems(stem, uX, unitX, uY, unitY)

def makePOSStabilizer1(stem, size:KeySizeSpec=KeySizeSpec()):
	# stems that go into multiple switches, rather than a separate construction
	# also what does POS stand for? surely not point-of-sale?
	return mount.makePOSStems1(stem, size)