import GLK, GLKsimple
import cadquery as cq
from cadquery import exporters
from os.path import dirname, abspath


try:
	from cq_server.ui import ui, show_object
except ModuleNotFoundError:
	pass


# export settings
exportSTL =			True
exportSTEP =	 	True
exportIndividual =	False
exportAssembly =	False
export_pre =	'{0}/../export/preview'.format(dirname(abspath(__file__)))

# STL settings
tol = 0.001
tolAng = 0.05		# 0.025 decent quality/size trade-off; 0.01 for obscene quality


# choose your character
exportMX =		False
exportSimple =	False
prefix =		("GLKS_" if exportSimple else "GLK_") + ("MX_" if exportMX else "KL_")
keycaps =		GLKsimple.profile(mx=exportMX) if exportSimple else GLK.profile(mx=exportMX)


assembly = cq.Assembly()
assemblyTracking = {}
for i, name in enumerate(keycaps):
	cap = keycaps[name]
	# export individual
	if exportIndividual:
		if exportSTL:	exporters.export(cap, './export/STL/' + name + '.stl', tolerance=tol, angularTolerance=tolAng)
		if exportSTEP:	exporters.export(cap, './export/STEP/' + name + '.step')
	# build assembly
	spec = name.split("_")
	if spec[2] not in assemblyTracking: assemblyTracking[spec[2]] = { "x":0, "lastUnitX":0 }
	unitX = float(spec[3].split("x")[0])/100
	unitY = float(spec[3].split("x")[1])/100
	posX = 19.05/2*(assemblyTracking[spec[2]]["lastUnitX"]+unitX) + assemblyTracking[spec[2]]["x"]
	posY = 19.05/2*unitY + 19.05*(4-int(spec[2][1]))
	assembly.add(cap, name=name, loc=cq.Location(cq.Vector(posX,posY,0)))
	assemblyTracking[spec[2]]["x"] = posX
	assemblyTracking[spec[2]]["lastUnitX"] = unitX

# export assembly
if exportAssembly:
	if exportSTL:	exporters.export(assembly.toCompound(), './export/STL/'+prefix+'keycaps.stl', tolerance=tol, angularTolerance=tolAng)
	if exportSTEP:	exporters.export(assembly.toCompound(), './export/STEP/'+prefix+'keycaps.step')


# show in cq-editor
if 'show_object' in locals():
    show_object(assembly)