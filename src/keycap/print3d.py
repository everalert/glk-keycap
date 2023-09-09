# from cadquery import exporters
import cadquery as cq
# import keycap as kc
# from keycap.helper import *
import math
# import numpy
from copy import deepcopy
from keycap.vector import Vec2, Vec3


#NOTE: CHITUBOX LIGHT SUPPORT MEASUREMENTS
# tip diameter - 0.30
# mid diameter - 0.80
# angle - 70
# cross width - 4
# cross start height - 3
# cross angle - 45
# z lift - 5



class Leg3DP:

	bank = {}
	s_angle = 50
	s_barangle = 22.5
	s_bargap = 0.5
	s_tipdia = 0.35
	s_middia = 0.80
	s_botdia = 1.50
	s_bardia = 0.40
	s_tiplen = 1.0
	s_both = 0.5
	
	def __init__(self, h=32, w=5, pos:Vec3=Vec3(), angle=0, tip=1.5):
		self.h = h
		self.w = w
		self.pos = pos
		self.angle = angle
		self.tip = max(Leg3DP.s_tiplen,tip)
	
	def __deepcopy__(self, memo=None):
		if memo is None:
			memo = {}
		return Leg3DP(deepcopy(self.h),deepcopy(self.w),deepcopy(self.pos,memo),deepcopy(self.angle),deepcopy(self.tip))
	
	def __str__(self):
		return "Leg3DP({0},{1},{2},{3},{4})".format(self.h, self.w, self.pos, self.angle, self.tip)
	
	def getID(self, h=False) -> str:
		return "Leg3DP({0}W,{1}A,{2}T)".format(self.w, self.angle, self.tip) + ('({0}H)'.format(self.h) if h else '')
	
	def clone(self, h=None, w=None, pos=None, angle=None, tip=None) -> 'Leg3DP':
		args = locals()
		new = deepcopy(self)
		for a in args.keys()^['self']:
			if args.get(a) is not None:
				setattr(new, a, args.get(a))
		return new

	def applyTilt(self, angle) -> 'Leg3DP':
		self.pos.rotateZ(-angle).rotateY(angle).rotateZ(angle)
		return self
	
	def getAngledLen(self) -> float:
		'''
		Return the length of only the angled part of the leg.
		'''
		return self.w/math.sin(math.radians(Leg3DP.s_angle))
	
	def getAngledH(self) -> float:
		'''
		Return the height of only the angled part of the leg.
		'''
		return self.getAngledLen() * math.cos(math.radians(Leg3DP.s_angle))
	
	@classmethod
	def getBarLen(cls, mag) -> float:
		return mag/math.sin(math.radians(Leg3DP.s_barangle))
	
	@classmethod
	def getBarH(cls, mag) -> float:
		return Leg3DP.getBarLen(mag) * math.cos(math.radians(Leg3DP.s_barangle))

	def getKneeOff(self) -> Vec2:
		'''
		Return the position offset at the end of the upper portion of the leg,
		i.e. the top of the last vertical section.
		'''
		return Vec2(x=self.w).rotate(self.angle).toVec3() + Vec3(z=-self.getAngledH()-self.tip)

	def getKneePos(self) -> Vec3:
		'''
		Return the world position at the end of the upper portion of the leg,
		i.e. the top of the last vertical section.
		'''
		return self.pos + self.getKneeOff()

	def makeToPos(self, pos2:Vec2) -> 'Leg3DP':
		'''
		Return a new Leg3DP that starts at this leg's position but
		extends toward pos2, resulting in an extra leg connected to the
		model at the same point.
		'''
		dif = pos2-self.pos.clone()
		return self.clone(w=dif.mag(), angle=dif.ang())

	@classmethod
	def getManagedModel(cls, name):
		return Leg3DP.bank[name] if name in Leg3DP.bank else None
	
	@classmethod
	def addManagedModel(cls, name, model):
		Leg3DP.bank[name] = model
		return model
	
	def generateKnee(self):
		'''
		Return a CQ model of only the upper portion of the leg.
		'''
		modelname = 'KNEE_{0}'.format(self.getID(h=False))
		model = Leg3DP.getManagedModel(modelname)
		if model is not None:
			return model
		sk_tip = cq.Sketch().circle(Leg3DP.s_tipdia/2)
		sk_mid = cq.Sketch().circle(Leg3DP.s_middia/2)
		midlen = self.getAngledLen()
		midh = self.getAngledH()
		model = ( cq.CQ().tag('tip')
				.sphere(Leg3DP.s_tipdia/2)
				.placeSketch(
					sk_tip,
					sk_mid.moved(cq.Location(cq.Vector(0,0,-Leg3DP.s_tiplen))),
					sk_mid.moved(cq.Location(cq.Vector(0,0,-self.tip)))
				).loft(True)
				.faces('<Z').workplane().tag('mid')
					.sphere(Leg3DP.s_middia/2)
				.workplaneFromTagged('mid').transformed(offset=(self.w/2, 0, midh/2), rotate=cq.Vector(0,Leg3DP.s_angle,0))
					.cylinder(midlen, Leg3DP.s_middia/2)
				.workplaneFromTagged('mid').transformed(offset=(self.w, 0, midh)).tag('bot')
					.sphere(Leg3DP.s_middia/2)
		).rotate((0,0,0),(0,0,1),self.angle)
		return Leg3DP.addManagedModel(modelname, model)
	
	def generateShin(self):
		'''
		Return a CQ model of only the lower (vertical) portion of the leg.
		'''
		modelname = 'SHIN_{0}H'.format(self.h)
		model = Leg3DP.getManagedModel(modelname)
		if model is not None:
			return model
		height = self.h+self.getKneeOff().z
		model = cq.CQ().transformed(offset=(0,0,-height/2)).cylinder(height, Leg3DP.s_middia/2)
		return Leg3DP.addManagedModel(modelname, model)
	
	def generate(self):
		'''
		Return a CQ model of the whole leg; combination of generateKnee() and
		generateShin().
		'''
		modelname = 'ALL_{0}'.format(self.getID(h=True))
		model = Leg3DP.getManagedModel(modelname)
		if model is not None:
			return model
		a = cq.Assembly()
		a.add(self.generateKnee())
		a.add(self.generateShin(), loc=cq.Location(cq.Vector(self.getKneeOff().toTuple())))
		model = a.toCompound().fuse()
		return Leg3DP.addManagedModel(modelname, model)
	
	@classmethod
	def generateShin(cls, h:float, bars:list[Vec2]=[]):
		'''
		Return a CQ model of a shin of a given height, with attached nets toward an arbitrary
		number of XY points. 
		'''
		a = cq.Assembly()
		barName = lambda b : 'BAR{0}A{1}M'.format(b.ang(), b.mag())

		names = ['SHIN_{0}H'.format(h)]
		for i in range(len(bars)):
			name = barName(bars[i])
			if name not in names:
				names.append(name)
		model = Leg3DP.getManagedModel('_'.join(names))
		if model is not None:
			return model
		
		for i in range(len(bars)):
			b = bars[i]
			modelname = barName(b)
			bar = Leg3DP.getManagedModel(modelname)
			bar_h = Leg3DP.getBarH(b.mag())
			bar_len = Leg3DP.getBarLen(b.mag())
			if bar is None:
				bar = Leg3DP.addManagedModel(modelname, (
					cq.CQ().transformed(offset=(-b.mag()/2,0,-bar_h/2), rotate=cq.Vector(0,180+Leg3DP.s_barangle,0))
					.cylinder(Leg3DP.getBarLen(b.mag()),Leg3DP.s_bardia/2)
				).rotate((0,0,0),(0,0,1),b.ang()) )
			for j in range(1+int(h//(bar_h+Leg3DP.s_bargap))):
				a.add(bar, name='bar_{0}_{1}'.format(i,j), loc=cq.Location(cq.Vector(0,0,-(bar_h+Leg3DP.s_bargap)*j)))
		modelname = names[0]
		shin = Leg3DP.getManagedModel(modelname)
		if shin is None:
			shin = Leg3DP.addManagedModel(modelname, cq.CQ().transformed(offset=(0,0,-h/2)).cylinder(h,Leg3DP.s_middia/2))
		a.add(shin, name='shin')
		return Leg3DP.addManagedModel('_'.join(names), a.toCompound().fuse())
	
	@classmethod
	def generateFeet(cls, legs):
		'''
		Return a CQ model containing all feet needed for a given set of Leg3DP
		objects, positioned at Z=0.
		'''
		modelname = 'FOOT_{0}H_{1}x{2}D'.format(Leg3DP.s_both, Leg3DP.s_middia, Leg3DP.s_botdia)
		model = Leg3DP.getManagedModel(modelname)
		if model is None:
			sk_mid = cq.Sketch().circle(Leg3DP.s_middia/2)
			sk_bot = cq.Sketch().circle(Leg3DP.s_botdia/2)
			model = cq.CQ().placeSketch( sk_bot, sk_mid.moved(cq.Location(cq.Vector(0,0,Leg3DP.s_both))) ).loft(True)
			Leg3DP.addManagedModel(modelname, model)
		a = cq.Assembly()
		for l in legs:
			a.add(model, loc=cq.Location(cq.Vector(l.getKneePos().toVec2().toVec3().toTuple())))
		return a.toCompound().fuse()