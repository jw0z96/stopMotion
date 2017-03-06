import maya.cmds as cmds
import random

def maxValueChange(frame, randomness):

	defaultRandom = randomness
	selection = cmds.ls(selection=True)
	valueList = []

	for object in selection:
		cmds.select(object)
		attrList = cmds.keyframe(query=True, name=True)
		randomness = defaultRandom
		
		if(cmds.attributeQuery('smr', n=object, exists = True)):
			randomness = cmds.getAttr(str(object)+'.smr')
		
		for activeAttr in attrList:
			activeAttr=activeAttr[len(object)+1:]
			val2 = cmds.keyframe(query=True, attribute=activeAttr, lsl=True, valueChange=True , t=(frame+1,frame+1))
			val1 = cmds.keyframe(query=True, attribute=activeAttr, lsl=True, valueChange=True , t=(frame,frame))
			
			valChng = float(val2[0]) - float(val1[0])
			
			cmds.setKeyframe(attribute=activeAttr, v=val1[0]+(randomness*(valChng*random.random())) , t=frame)
			
			if activeAttr is 'rotationX' or 'rotationY' or 'rotationZ':
				valChng = valChng/100
			
			valueList.append(abs(valChng))

	cmds.select(selection)
	return max(valueList)

def stopMotionGen(ratio, randomness, frameStart, frameEnd):
	
	k = 0
	
	delet=0
	stap=0
	
	for frame in range (frameStart,frameEnd+1):
		cmds.setKeyframe(t=frame, i=True, )
		
	autoCounter = []
	for frame in range (frameStart,frameEnd):
		autoCounter.append(maxValueChange(frame, randomness))

	autoCounterSorted = sorted(autoCounter)
	threshold = autoCounterSorted[0]+((autoCounterSorted[-1]-autoCounterSorted[0])*ratio)

	for frame in range (frameStart,frameEnd-1):
		if k == 1:
			k = 0
			cmds.cutKey( time=(frame,frame) )
			delet = delet + 1
		elif k == 0:
			valChange = autoCounter[frame]
			if valChange == 0:
				k = 1
				cmds.cutKey( time=(frame,frame) )
				delet = delet + 1
			if valChange < threshold:
				k = 1
				cmds.keyTangent(t=(frame,frame), ott='step' )
				stap = stap + 1	
			elif valChange > threshold:
				k = 0
				cmds.keyTangent(t=(frame,frame), ott='step' )
				stap = stap + 1

	print delet
	print stap

def randomAttribute(random):
	"""
	adds 'random' attribute to the currently selected node
	"""
	cmds.addAttr(shortName='smr', longName='StopMotionRandomnessOverride', defaultValue=random, minValue=0, maxValue=5)

def createUI(*args):
	
	windowID = 'stopmoInterface'
	if cmds.window(windowID, exists = True):
		cmds.deleteUI(windowID)
	cmds.window(windowID, title='Stop Motion Simulator', resizeToFitChildren=True, sizeable=False)
	
	cmds.rowColumnLayout(w=400)
	cmds.image(image=cmds.internalVar(usd=True)+"stopMotion/UIheader.png")
	cmds.setParent("..")
	
	cmds.frameLayout(label="Options", collapsable=False, mw=5, mh=5)
	
	
	cmds.text(label='Please select all animated controllers and/or Objects.', height=20,align='center')
	
	cmds.rowColumnLayout(w=300)
	ratioControl = cmds.floatSliderGrp(label='Ratio Control', minValue=0, maxValue=1, value=0.5, field=True)
	randomnessControl = cmds.floatSliderGrp(label='Randomness Control', minValue=0, maxValue=5, value=1, field=True)
	cmds.setParent("..")
	
	cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1,142),(2,100),(3,100)])
	cmds.text(label='Frame Range:', height=20,align='right')
	startFrame = cmds.intField(value=cmds.playbackOptions(q=True, minTime=True))
	endFrame= cmds.intField(value=cmds.playbackOptions(q=True, maxTime=True))
	cmds.setParent("..")
	cmds.rowColumnLayout(w=390)
	cmds.separator(height=20)
	
	cmds.button(label = 'Add Randomness Override Attribute', height=30, command = lambda *args: randomAttribute(cmds.floatSliderGrp(randomnessControl, query=True, value=True)))
	
	cmds.button(label='Simulate Stop Motion', height=30, command = lambda *args: stopMotionGen(
	cmds.floatSliderGrp(ratioControl, query=True, value=True),
	cmds.floatSliderGrp(randomnessControl, query=True, value=True),
	cmds.intField(startFrame, query=True, value=True),
	cmds.intField(endFrame, query=True, value=True)))
	
	cmds.separator(height=20)
	
	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,300),(2,100)])
	
	cmds.button(label = 'Add to Custom shelf', command = shelfButton)
	cmds.button(label = 'Reset', command = createUI)
	cmds.setParent("..")
	
	#text
	cmds.text(l='Joe Withers - 2016', w=400, h=30, ww=True, fn="smallPlainLabelFont")
	
	cmds.showWindow()

def shelfButton(*args):
	"""
	adds a shelf button for the script under the custom tab
	"""
	cmds.shelfButton(annotation='Stop Motion Simulator - Joe Withers', image = "commandButton.png", l='Stop Motion', p='Custom', imageOverlayLabel='StopMo', overlayLabelBackColor=(.6, .6, .6, .6), command=str("from stopMotion import smGui;reload(smGui);smGui.createUI()"))
