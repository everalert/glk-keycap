import cadquery as cq
from cadquery import selectors as sel
from keycap.helper import makeRoundRectWire, KeySizeSpec
from keycap.vector import Vec2, Vec3
from copy import deepcopy


#TODO: make scoop more sensibly so that it always fully cuts the top of an equivalently specced core
#      seems to run into issues with sufficiently large caps (2x2, 4x1, etc.)


class KeyBody:
	
	maxCurve = 50
	maxAngle = 20
	defaults = {
		'base':		Vec2(18.1, 18.1),
		'top':		Vec2(12.4, 14.4),
		'height':	6.5,
		'curve':	0.0,
		'corner':	Vec2(4.0, 1.5), # roundedness; x=top, y=bot
		'edge':		Vec2(0.3, 0.3), # fillet/chamfer; x=top, y=bot
		'offset':	Vec2(),
		'angle':	9,
		'depth':	2.5,
		'ratio':	1.0,
		'convex':	False,
	}
	
	# defaults to MX/OEM measurements
	def __init__(self, **kwargs) -> 'KeyBody':
		if 'curve' in kwargs:	kwargs['curve'] = max(-KeyBody.maxCurve, min(KeyBody.maxCurve, kwargs['curve']))
		if 'angle' in kwargs:	kwargs['angle'] = max(-KeyBody.maxAngle, min(KeyBody.maxAngle, kwargs['angle']))
		defaults = deepcopy(KeyBody.defaults)
		for a in defaults.keys():
			setattr(self, a, kwargs.get(a, defaults.get(a)))
	
	def makeCore(self, coreSize:Vec2=Vec2()) -> cq.Workplane:
		dim2sk = lambda dim : cq.Sketch().rect(dim.x, dim.y).vertices().fillet(dim.z)
		base =	dim2sk(self.getBaseSize(coreSize))
		mid =	dim2sk(self.getMidSize(coreSize))
		top =	dim2sk(self.getTopSize(coreSize))
		return (
			cq.Workplane("XY")
			.placeSketch(
				base,
				mid.moved(cq.Location(cq.Vector(0, -self.offset.y/2, self.height/2), cq.Vector(1,0,0), self.angle/2)),
				top.moved(cq.Location(cq.Vector(0, -self.offset.y, self.height+0.05), cq.Vector(1,0,0), self.angle))
			)
			.loft()
		)

	def makeScoop(self, coreSize:Vec2=Vec2(), planeOnly:bool=False, extraHeight:float=0.0) -> cq.Workplane:
		#TODO: better scoop generation that always fully cuts the top of an equivalently specced core
		bot = self.getBaseSize(coreSize)
		depthMid = self.depth if self.convex else 0
		depthOut = self.depth*(-1 if self.convex else 1)
		scoopX = bot.x/2*(1/self.ratio) if self.ratio<1 else bot.x/2
		scoopY = bot.y/2 if self.ratio<1 else bot.y/2*self.ratio
		scoop_path = (
			cq.Workplane("YZ").transformed(rotate=cq.Vector(0, 0, self.angle))
			.moveTo(-scoopY, depthOut)
			.threePointArc((0, 0), (scoopY, depthOut))
		)
		scoop = (
			cq.Workplane("XZ")
			.moveTo(-scoopX, 0)
			.threePointArc((0, -depthOut), (scoopX, 0))
		)
		scoop = scoop.wire() if planeOnly else (scoop
			.lineTo(scoopX, self.depth*2+extraHeight)
			.lineTo(-scoopX, self.depth*2+extraHeight)
			.close()
		)
		return scoop.sweep(scoop_path).translate((0, 0, -depthMid))

	def applyEdgeFinish(self, keycap, size:KeySizeSpec) -> cq.Workplane:
		#TODO: derive path from keycap input and eliminate this crap
		base = self.getBaseSize(size.getCoreSize())
		sizeU = size.getFullSize()
		edgeBotPath = makeRoundRectWire(base.x, base.y, base.z)
		rimW = (sizeU.y-base.y)/2
		rimH = rimW+self.edge.y
		edgeBotCut = (
			cq.Workplane("YZ")
			.moveTo(sizeU.y/2, 0)
			.line(0, rimH)
			.line(-rimH, -rimH)
			.close()
			.sweep(edgeBotPath)
		)
		return (
			keycap
			.edges(sel.BoxSelector((sizeU.x/2,sizeU.y/2,self.edge.y),(-sizeU.x/2,-sizeU.y/2,self.height))).fillet(self.edge.x)
			.cut(edgeBotCut) # manual bottom chamfer, auto one is bad
		)
	
	def getTopSize(self, coreSize:Vec2=Vec2()) -> Vec3:
		return Vec3(self.top.x+coreSize.x, self.top.y+coreSize.y, self.corner.x)
	
	def getBaseSize(self, coreSize:Vec2=Vec2()) -> Vec3:
		return Vec3(self.base.x+coreSize.x, self.base.y+coreSize.y, self.corner.y)
	
	def getMidSize(self, coreSize:Vec2=Vec2()) -> Vec3:
		curve = 1+self.curve/100
		top = self.getTopSize(coreSize)
		bot = self.getBaseSize(coreSize)
		return Vec3((bot.x-top.x)/2*curve+top.x, (bot.y-top.y)/2*curve+top.y, (bot.z+top.z)/2)

	def getAABB(self, coreSize:Vec2=Vec2()) -> Vec3:
		top = self.getTopSize(coreSize)*Vec3(0.5,0.5,0).rotateX(-self.angle)
		bot = self.getBaseSize(coreSize)
		return Vec3(bot.x, bot.y, self.height+top.z)
	
	def clone(self, **kwargs) -> 'KeyBody':
		new = deepcopy(self)
		for a in vars(new).keys():
			if kwargs.get(a) is not None:
				setattr(new, a, kwargs.get(a))
		return new
	
	def __deepcopy__(self, memo=None) -> 'KeyBody':
		if memo is None:	memo = {}
		return KeyBody(**{a[0]:deepcopy(a[1],memo) for a in vars(self).items()})
	
	def __str__(self) -> str:
		return 'KeyBody({0})'.format(','.join(['{0}={1}'.format(a[0],a[1]) for a in vars(self).items()]))


def makeCore(topW:float, topH:float, baseW:float, baseH:float, capH:float, curve:float=25, topA:float=9, topOff:float=0.85, topRad:float=1.5, baseRad:float=4):
	curve = 1+(curve/100)
	midX = (baseW-topW)/2*curve + topW
	midY = (baseH-topH)/2*curve + topH
	midRad = (baseRad-topRad)/2*curve + topRad
	base =	cq.Sketch().rect(baseW, baseH).vertices().fillet(baseRad)
	mid =	cq.Sketch().rect(midX, midY).vertices().fillet(midRad)
	top =	cq.Sketch().rect(topW, topH).vertices().fillet(topRad)
	return (
		cq.Workplane("XY")
		.placeSketch(
			base,
			mid.moved(cq.Location(cq.Vector(0, -topOff/2, capH/2), cq.Vector(1,0,0), topA/2)),
			top.moved(cq.Location(cq.Vector(0, -topOff, capH+0.05), cq.Vector(1,0,0), topA))
		)
		.loft()
	)
	
	
def makeScoop(angle:float=9, depth:float=2.5, ratio:float=1.25, capW:float=19.05, capH:float=19.05, convex:bool=False, planeOnly:bool=False):
	#TODO: better scoop generation that always fully cuts the top of an equivalently specced core
	depthMid = depth if convex else 0
	depthOut = depth*(-1 if convex else 1)
	scoopX = capW/2*(1/ratio) if ratio<1 else capW/2
	scoopY = capH/2 if ratio<1 else capH/2*ratio
	scoop_path = (
		cq.Workplane("YZ").transformed(rotate=cq.Vector(0, 0, angle))
		.moveTo(-scoopY, depthOut)
		.threePointArc((0, 0), (scoopY, depthOut))
	)
	scoop = (
		cq.Workplane("XZ")
		.moveTo(-scoopX, 0)
		.threePointArc((0, -depthOut), (scoopX, 0))
	)
	scoop = scoop.wire() if planeOnly else (scoop
		.lineTo(scoopX, depth*2)
		.lineTo(-scoopX, depth*2)
		.close()
	)
	return scoop.sweep(scoop_path).translate((0, 0, -depthMid))


def applyEdgeFinish(keycap, fillet, chamfer, baseW=18.1, baseH=18.1, baseRad=1.5, uW=19.05, uH=19.05, coreH=19.05):
	#TODO: derive path from keycap input and eliminate this crap
	edgeBotRect = cq.Workplane("XY").rect(baseW, baseH)
	edgeBotCnr = edgeBotRect.vertices().vals()
	edgeBotPath = edgeBotRect.val().fillet2D(baseRad, edgeBotCnr)
	rimW = uH/2-baseH/2
	rimH = rimW+chamfer
	edgeBotCut = (
		cq.Workplane("YZ")
		.moveTo(uH/2, 0)
		.line(0, rimH)
		.line(-rimH, -rimH)
		.close()
		.sweep(edgeBotPath)
	)
	return (
		keycap
		.edges(sel.BoxSelector((uW/2,uH/2,chamfer),(-uW/2,-uH/2,coreH))).fillet(fillet)
		.cut(edgeBotCut) # manual bottom chamfer, auto one is bad
	)