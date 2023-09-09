from cadquery import selectors as sel
import math
import cadquery as cq
import cq_warehouse.extensions
from keycap.spec import KeySpec

# TODO
# - solid circle
# - inset/"deep" dish
# - fujitsu tombstone keycap homing mark (on FM Towns FMT-KB205; see https://youtu.be/pFvnROFlgCc?t=93)
# - other shapes?
# - fix addDots() centering issue (DONE???)
# - figure out how to get cap top face center without contrived bs


	# HOMING/WIN-KEY FEATURES

def ang2dir(angle:float=9):
	r = math.radians(90-angle)
	return  (0, math.sin(r), -math.tan(r))


def highestIntersection(keycap, point, direction):
	i = keycap.val().findIntersection(cq.Vector(point), cq.Vector(direction))
	return sorted(i, reverse=True, key=lambda p : p[0].z)[0][0]

def getCapCenter(keycap, topH:float=19.05, topOff:float=0.85, offset=cq.Vector(0,0,0)):
	# the below would be easier/better if CQ could just tell me the isolines lol
	pos = cq.Vector()
	edges = list(filter(lambda e : abs(e.positionAt(0.5).x) < 0.0001, keycap.faces(sel.NearestToPointSelector((0, -topOff, topH))).val().Edges()))
	for e in edges:
		pos = pos.add(e.positionAt(0.5))
	return cq.Location(offset if len(edges)==0 else pos.__truediv__(len(edges)).add(offset))


def addWinBulb(keycap, topH:float=19.05, topOff:float=0.85, topAng:float=9, convex:bool=False):
	Hdir = ang2dir(topAng)
	pt = getCapCenter(keycap, topH, topOff).toTuple()[0]
	ptProj = highestIntersection(keycap, pt, Hdir)
	rad = 5
	insetH = 1.25 if convex else 0.15
	insetA = 37.5
	bulbH = 1.25
	path = cq.Workplane("XY").circle(rad)
	cut = (
		cq.Workplane("XZ")
		.moveTo(0, -insetH)
		.line(rad, 0)
		.polarLine(10, 90-insetA)
		.hLineTo(0)
		.close()
		.sweep(path)
		.rotate((0,0,0),(1,0,0),topAng)
		.translate(ptProj)
	)
	bulb = (
		cq.Workplane("XZ")
		.moveTo(0, bulbH-insetH)
		.ellipseArc(rad+0.2, bulbH, 90, 180)
		.hLineTo(0)
		.close()
		.sweep(path)
		.rotate((0,0,0),(1,0,0),topAng)
		.translate(ptProj)
	)
	return keycap.cut(cut) + bulb

def addInsetBulb(keycap, spec:KeySpec=KeySpec()):
	# need to incorporate more of the spec settings instead of using hardcoded stuff
	Hdir = ang2dir(spec.body.angle)
	pt = getCapCenter(keycap, spec.body.height, spec.body.offset.y).toTuple()[0]
	ptProj = highestIntersection(keycap, pt, Hdir)
	rad = 5
	insetH = 1.25 if spec.body.convex else 0.15
	insetA = 37.5
	bulbH = 1.25
	path = cq.Workplane("XY").circle(rad)
	cut = (
		cq.Workplane("XZ")
		.moveTo(0, -insetH)
		.line(rad, 0)
		.polarLine(10, 90-insetA)
		.hLineTo(0)
		.close()
		.sweep(path)
		.rotate((0,0,0),(1,0,0),spec.body.angle)
		.translate(ptProj)
	)
	bulb = (
		cq.Workplane("XZ")
		.moveTo(0, bulbH-insetH)
		.ellipseArc(rad+0.2, bulbH, 90, 180)
		.hLineTo(0)
		.close()
		.sweep(path)
		.rotate((0,0,0),(1,0,0),spec.body.angle)
		.translate(ptProj)
	)
	return keycap.cut(cut) + bulb


def addDots(keycap, count:float=2, radius:float=0.5, ringRadius:float=1.8, topH:float=19.05, topOff:float=0.85, topAng:float=9, ringOffY:float=2.0):
	Hdir = ang2dir(topAng)
	pt = cq.Vector(getCapCenter(keycap, topH, topOff, cq.Vector(0,ringOffY,0)).toTuple()[0])
	Hstart = ((count%2+1)%2)*360/count/2+90 # make the first dot not start at the top, but only if even number of dots
	H_points = [cq.Vector()] if count==1 else (
		cq.Workplane("XY")
		.transformed(rotate=cq.Vector(topAng, 0, 0))
		.polarArray(ringRadius, Hstart, 360, count)
		.vals()
	)
	for p in H_points:
		point = highestIntersection(keycap, cq.Vector(p.toTuple()[0]).add(pt), Hdir)
		keycap += (
			cq.Workplane("XY")
			.transformed(offset=point)
			.sphere(radius)
		)
	return keycap

def addDots1(keycap, spec:KeySpec=KeySpec()):
	# need to incorporate more of the spec settings instead of using hardcoded stuff, i think?
	topSize = spec.body.getTopSize(spec.size.getCoreSize())
	Hdir = ang2dir(spec.body.angle)
	pt = cq.Vector(getCapCenter(keycap, spec.body.height, spec.body.offset.y, cq.Vector(topSize.x*spec.mark.offset.x,topSize.y*spec.mark.offset.y,0)).toTuple()[0])
	Hstart = ((spec.mark.count%2+1)%2)*360/spec.mark.count/2+90 # make the first dot not start at the top, but only if even number of dots
	H_points = [cq.Vector()] if spec.mark.count==1 else [cq.Vector(p.toTuple()[0]) for p in (
		cq.Workplane("XY")
		.transformed(rotate=cq.Vector(spec.body.angle, 0, 0))
		.polarArray(spec.mark.size, Hstart, 360, spec.mark.count)
		.vals()
	)]
	for p in H_points:
		point = highestIntersection(keycap, p.add(pt), Hdir)
		keycap += (
			cq.Workplane("XY")
			.transformed(offset=point)
			.sphere(spec.mark.depth)
		)
	return keycap


#TODO: solid circle home mark, idk how to sweep the foking projected wire tho
def addRing(keycap):
	pass

#TODO: inset dish
def addDish(keycap):
	pass