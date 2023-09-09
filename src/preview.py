from os.path import dirname, abspath
import cadquery as cq
from cadquery import exporters
import GLK


# export settings
export =		False
exportSTL =		False
exportSTEP =	False
export_pre =	'{0}/../export/preview'.format(dirname(abspath(__file__)))

# STL settings
tol =		0.001
tolAng =	0.025		# 0.025 decent quality/size trade-off; 0.01 for obscene quality


try:
	from cq_server.ui import ui, show_object
except ModuleNotFoundError:
	pass


model = GLK.keycap()
# model = GLKsimple.keycap()
# model = GLK.profile(mx=False) 		# generate keys for all officially supported sets
# model = GLKsimple.profile(mx=False) 	# generate keys for all officially supported sets


if type(model) in [cq.Workplane, cq.Compound, cq.Assembly]:
	if 'show_object' in locals():
		show_object(model)
	if export:
		if exportSTL:	exporters.export(model, '{0}.stl'.format(export_pre), tolerance=tol, angularTolerance=tolAng)
		if exportSTEP:	exporters.export(model, '{0}.step'.format(export_pre))
else:
	assembly = cq.Assembly()
	for i, k in enumerate(model):
		assembly.add(model[k], loc=cq.Location(cq.Vector(0, 0, 0*19.05)), name=str(k))
		if export:
			if exportSTL:	exporters.export(model[k], '{0}_{1}.stl'.format(export_pre, str(k)), tolerance=tol, angularTolerance=tolAng)
			if exportSTEP:	exporters.export(model[k], '{0}_{1}.step'.format(export_pre, str(k)))
	if 'show_object' in locals():
		show_object(assembly.toCompound())