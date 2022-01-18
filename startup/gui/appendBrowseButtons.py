import GafferHaven
import Gaffer, GafferUI, os, imath
import GafferCycles

if "GAFFERCYCLES" in os.environ:
	import GafferCycles
	Gaffer.Metadata.registerValue(
		GafferCycles.CyclesLight,
		"layout:activator:lightIsBackground", lambda node : node["__shaderName"].getValue() == "background_light"
	) 
	Gaffer.Metadata.registerValue(
		GafferCycles.CyclesLight, "layout:customWidget:browseHDRI:widgetType", "GafferHaven.gui.BrowseButton",
	)
	Gaffer.Metadata.registerValue(
		GafferCycles.CyclesLight, "layout:customWidget:browseHDRI:section", "Settings",
	)
	Gaffer.Metadata.registerValue(
		GafferCycles.CyclesLight,
		"layout:customWidget:browseHDRI:visibilityActivator", "lightIsBackground"
	)

if "ARNOLD_ROOT" in os.environ:
	import GafferArnold
	Gaffer.Metadata.registerValue(
		GafferArnold.ArnoldShader,
		"layout:activator:shaderIsImage", lambda node : node["name"].getValue() == "image"
	) 
	Gaffer.Metadata.registerValue(
		GafferArnold.ArnoldShader, "layout:customWidget:browseHDRI:widgetType", "GafferHaven.gui.BrowseButton",
	)
	Gaffer.Metadata.registerValue(
		GafferArnold.ArnoldShader, "layout:customWidget:browseHDRI:section", "Settings",
	)
	Gaffer.Metadata.registerValue(
		GafferArnold.ArnoldShader,
		"layout:customWidget:browseHDRI:visibilityActivator", "shaderIsImage"
	)
