##
# mySchedule.py
# Will be started from WalkNGrab.\n
# \namespace mySchedule

import steamvr
from struct import *
import viz
import vizshape
import KP
from types import * #for assert
import vizproximity #for the method addSensor
import vizmat
import viztask
import vizact #für vizact.fadeTo
import vizinfo
import vizinput
import numpy as np
import vizfx
import time
import datetime
import transform
import math
import vizconnect
## This is needed for the logfile
import sys
## This is needed for the logfile
import os.path
import tools
from tools import grabber
from tools import highlighter
## Import the class Shelfobject
from Shelfobject import *
## Import the class Ballobject
from Ballobject import *


## 
# Reads the Versuchszenario file (Program gets loaded). It just contains the
# variable \c vardict.
# \see myTaskSchedule
# \see Versuchsszenario.py
# Use this for pilot project
#from Versuchsszenario_zuerst_kein_Zeitdruck_demo import vardict
# Use this for debugging
from Versuchsszenario_Pilot2Test import vardict

vartorusBallIntersection = False
#use vizconnect configuration 
# 10. Juni 2021
#vizconnect.go('configR.py')
firstGrab = True
isGrabbed = False

#isReleased = False

controllerobject = None

controllersteam = None

instruction_text1 = None
text2 = viz.addText3D('')
text3 = viz.addText3D('')
text4 = viz.addText3D('')
moveInstruction = None

firstRunInstruction = True
firstRunInstructionMovement = True

#enable physics
viz.phys.enable()
# viz.phys.setGravity(0.0, -0.098, 0.0)
# print 'My gravity is: '
# print viz.phys.getGravity()

# Will appear when the trial starts
torus = None

torusSensor = None

greentorusColor = None
redtorusColor = None

failArea = None


##
# A boolean, which is set by the programmer. 
# Some hardware is just available in the vr-lab. 
# If \c True, \ref rigidSensor and \ref rigidSensor2 will be used.
notinthevrlab = False

##
# A boolean, which is set by the programmer.  
# If \c True, the experiment is using the suit ('WalkNGrab-Reloaded (Suit)'). Otherwise \c False ('WalkNGrab-Reloaded').
isItSuit = True

##
# A 4x4 Transformation matrix as calculated using CoordinateSystmsCalib.py and Coordinate_systmes_model.ipynb.
# It helps to adjust the vive coordinate system to the phasespace coordinate system.
T = vizmat.Transform([1.0, 0.016, 0.015, 0.0, -0.015, 1.004, 0.004, 0.0, -0.013, -0.002, 1.004, 0.0, -0.016, -0.015, 0.019, 1.0]  )
#no transformation
#T = vizmat.Transform([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1] )

##
# This variables sets the duration of a block. Current block duration is 240 seconds (4 minutes).
# \see remain
# \see TrialCountDownTask
TRIAL_DURATION = 240

##
# It is needed for the countdown. It 'will be set' in \ref TrialCountDownTask<a></a>.
# \see TrialCountDownTask
trial_duration_temp = TRIAL_DURATION

## 
# Create time limit text. It is used together with \ref VIEWBALL.
# \see VIEWBALL
time_text = viz.addText3D('')
time_text.fontSize(1)
time_text.setScale([0.01]*3)
time_text.alignment(viz.ALIGN_CENTER_TOP)
time_text.setCenter([-0.06, 0.04, 0.1])

## 
# Creates text for balls with a good trial. It is used together with \ref VIEWBALL<a></a>.\n
# It will show the value of \ref goodballs and \ref numberOfBalls.
# \see VIEWBALL, goodballs
ball_text = viz.addText3D('')
ball_text.fontSize(1)
ball_text.setScale([0.01]*3)
ball_text.alignment(viz.ALIGN_CENTER_TOP)
ball_text.setCenter([0.06, 0.04, 0.1])		
		
	

# This variable contains a plane, which will be used in in \ref validation.
# It will be set in \c viz.Scene2. It is at start invisible.
# \see validation.
plane_v = vizshape.addBox(size=[5, 3, 0.1], scene = viz.Scene2)
plane_v.addParent(viz.WORLD, scene = viz.Scene1)
plane_v.visible(viz.OFF)


## 
# Creates text for balls with a bad trial. It is used together with \ref VIEWBALL<a></a>.\n
# It will show the value of the variable \ref wrongballs.
# \see VIEWBALL, getWrongBalls
wrongball_text = viz.addText3D('')
wrongball_text.fontSize(1)
wrongball_text.setScale([0.01]*3)
wrongball_text.alignment(viz.ALIGN_CENTER_TOP)
wrongball_text.setCenter([0.04, 0.04, 0.1])

## 
# Trick to get 3D-text on right position. It is used together with \ref time_text, 
# \ref ball_text and \ref wrongball_text. It also has a\n
# <code>
# VIEWBALL.disable(viz.INTERSECT_INFO_OBJECT)\n
# VIEWBALL.disable(viz.INTERSECTION)\n
# </code>\n
# This vizshape gets linked with \c viz.MainView.
# \see time_text, ball_text, wrongball_text
VIEWBALL = vizshape.addCube(0.0001)
VIEWBALL.disable(viz.INTERSECT_INFO_OBJECT)
VIEWBALL.disable(viz.INTERSECTION)

time_text.setParent(VIEWBALL)
time_text.setPosition(time_text.getCenter())

ball_text.setParent(VIEWBALL)
ball_text.setPosition(ball_text.getCenter())

#instruction_text1.setParent(VIEWBALL)
#instruction_text1.setPosition(instruction_text1.getCenter())

#text2.setParent(VIEWBALL)
#text2.setPosition(text2.getCenter())

wrongball_text.setParent(VIEWBALL)
wrongball_text.setPosition(wrongball_text.getCenter())

##
# Boolean for logging (CSV).
# \see getShowTime, setShowTime, writeCSVfile
show_time = False

##
# Variable for the text on screen. It contains the total amount of balls in a trial.
# \see time_text
numberOfBalls = 0

##
# Variable for the text on screen. It contains the amount of balls with a good trial. 
# A good trial is trial, in which the participant has passed the \ref viapoint 
# and placed the \ref ball on the \ref placement successfully.
# \see ball_text, wrongballs
# \see calculateTrial
goodballs     = 0

##
# Variable for text on screen. It contains the amount of balls with a bad trial.
# \see wrongball_text, goodballs
# \see calculateTrial, getWrongBalls
wrongballs    = 0

##
# This variable stores the time, which is left/remain.
# \see TRIAL_DURATION
# \see TrialCountDownTask
remain = 0

##
# An iterator integer for the method \ref handleDict.
# \see handleDict
int_i = 1

##
# It contains the path to this program.
# \see ORDNERPFAD
var_path = os.path.split(sys.argv[0])

##
# It contains the 'nice' path to this program.
# \see var_path
# \see fileExists
ORDNERPFAD = var_path[0] + "\\"

##
# Stores the subject id (id of partipant; of Versuchsperson). It will be used in the variable \c filename in \ref writeCSVfile.
# \see fileExists, writeCSVfile
vpn_id = "testdummyfile"

##
# Stores the block id. It is an integer.
# \see getBlock, setBlock, fileExists, writeCSVfile
varBlockID = 0

##
# Stores the current type of the trial. It is a string.
# \see writeCSVfile
varTrialType = None

##
# Stores the trial id. It is an integer.
# \see setTrial, writeCSVfile
varTrialID = 0

##
# Stores the starttime of a trial.
varTrailStartTime = 0.0

##
# Stores the duration of a trial.
# \see calculateTrialDurationTime
varTrailDuration  = 0.0

##
# Variable for the update-function.
# This enables to track the balls position and notes down the events (when does a block start, when does it end). It will be used together with \ref writeCSVfile.
# \see writeCSVfile
varonupdate = None

##
# Variable for the update-function. It will be used together with \ref writeSuitData.
# This enables to track the positions of the phasespaxce markers.
# \see writeSuitData
varonupdate2 = None

##
# String is needed for logging the events in file for C3D-data (a note for the column event).
# \see writeSuitData, getEventstring, setEventstring
eventstring = ""

##
# String is needed for logging the effects in CSV-file.
# \see writeCSVfile, getEffectstring, setEffectstring
effectstring = ""

## 
# Length of the rectangular parallelepiped (quader).
# \see makeARect
varLength = 3.6

## 
# Width of the rectangular parallelepiped (quader).
# \see makeARect
varWidth = 3.6

##
# Defines the size of the startplane.
varPlaneDim = 0.6

## 
# Variable for the ballobject.
# At the beginning it is \c None , but during the methods \ref doTypeA, \ref doTypeB, \ref doTypeC or \ref doTypeD
# the method \ref showBall will be called, which creates a ballobject.
# \see doTypeA, doTypeB, doTypeC, doTypeD, showBall
ball = None

##
# Stores the sensorsize. It is a float.
# \see writeCSVfile
varSensorsize = -1.0

##
# Variable for the viapoint.
# \see manager4, viapointsize, viapointpassed
# \see placeViapoint, playSound, addStartSensor, addSoundSensor
viapoint = None

## 
# This variable defines the size of the \ref viapoint.
# \see viapoint
viapointsize = 0.23

## 
# If the VP went through the \ref viapoint, it will be set to \c True.
# \see viapoint
viapointpassed = False

# This is for the instruction text
startpointpassed = ''

InteractionAdded = ''

# Will be set to true if the goal is hit
toruspassed = False

# Will be set to true if the ball rolls over the edge
overTheEdge = False

#TODO get this out?!
##
# Custom event for the \ref viapoint.
# \see sendMyCustomEvent
# \todo get this out?!
MY_SUPER_SPECIAL_CUSTOM_EVENT = viz.getEventID('MY_SUPER_SPECIAL_CUSTOM_EVENT')

##
# A boolean, which replaces the former custom event. For
# more inforamtion see \ref setCUSTOM
# \see setCUSTOM, getCUSTOM
boolCUSTOM_EVENT = False


##
# Stores the destination shelf for the \ref placement.
# \see setPlacementDestination, getPlacementDestination
varDestination = None


## 
# Variable for the Shelfobject \ref shelfA.
# It the shelf where the \ref ball is placed at the start of a trial.
# \see shelfB, shelfC, shelfD
# \see getShelf
shelfA = None


##
# This array contains the colors of object Shelfobject \ref shelfA.
# \see shelfA
shelfAcolors = [[0.2, 0.5, 0.5],[0.5, 0.5, 0.5],[0.0, 0.0, 0.0]]
#shelfAcolors = [[1,1,1],[0,0,0],[1,1,1]]

## 
# Array for the bodymeasures.
# \see varKoerpergroesse2
varKoerpergroesse = []

##
# Will contains the height of the participant.
# It is set by \ref setKoerpergroesse<a></a>.
# \see setKoerpergroesse, getKoerpergroesse
varKoerpergroesse2 = 0.0



##
# Will contain the weight of the participant.
# It is set by \ref setBodyweight<a></a>.
# \see setBodyweight, getBodyweight
varBodyweight = 0.0

##
# Will contain the shoulder-to-shoulder length of the participant.
# It is set by \ref setShoulderToShoulderLength<a></a>.
# \see setShoulderToShoulderLength, getShoulderToShoulderLength
varShoulderToShoulderLength = 0.0

##
# Will contain the upper arm length of the participant.
# It is set by \ref setUpperArmLength<a></a>.
# \see setUpperArmLength, getUpperArmLength
varUpperArmLength = 0.0

##
# Will contain the fore arm length of the participant.
# It is set by \ref setArmLength<a></a>.
# \see setForeArmLength, getForeArmLength
varForeArmLength = 0.0


##
# It is a Boolean. It is \c True, if the \ref ball has been released.
# \see doTypeA, doTypeB, doTypeC, doTypeD, getvarTrialAchievement, setvarTrialAchievement
varTrialAchievement = False

##
# A variable for the vive contoller object. Only needed when, we are debugging.
l = None

##
# This variable will contain the info panel. This formular will collect the vp number and
# the height of the experimentee.
participantInfo = vizinfo.InfoPanel('', title='Participant Information', icon=True)

##
# It contains a textbox for the info panel \ref participantInfo. It will collect
# the vp number as a string.
# \see participantInfo
textbox_id = participantInfo.addLabelItem('ID', viz.addTextbox())

##
# It contains a textbox for the info panel \ref participantInfo. It will collect
# the vp height as a string.
# \see participantInfo
textbox_kp = participantInfo.addLabelItem('Bodyheight\nin cm', viz.addTextbox())

#textbox for bodyweight
textbox_bw = participantInfo.addLabelItem('Bodyweight\nin kg', viz.addTextbox())

#textbox for shoulder-to-shoulder length
textbox_sts = participantInfo.addLabelItem('Shoulder-to-Shoulder length\nin cm', viz.addTextbox())

#textbox for upper arm length
textbox_ual = participantInfo.addLabelItem('Upper arm length\nin cm', viz.addTextbox())

#textbox for fore arm length
textbox_fal = participantInfo.addLabelItem('Fore arm length\nin cm', viz.addTextbox())

##
# It contains a submit button for the info panel \ref participantInfo. 
# \see participantInfo
submitButton = participantInfo.addItem(viz.addButtonLabel('Submit'), align=viz.ALIGN_RIGHT_CENTER)

##
# This variable stores the action-event for the \ref ball or the \ref placement. Needs to be global for control with viztask.
# It can contain a 'moveTo' or a 'sizeTo'.
# \see doTypeA, doTypeB, doTypeD
actionevent = None

##
# Variable for the target of the left hand.
target1 = None

##
# Variable for the target of the right hand.
#target2 = None

##
# Variable for the target of the head.
headtarget = None

##
# It will contain a non-rigged avatar, which is a left white glove.
# \see grabberRighthand, myLink1, myLink2
#grabberLefthand  = viz.addAvatar("glove_left.cfg")

##
# It will contain a non-rigged avatar, which is a right white glove.
# \see grabberLefthand, myLink1, myLink2
#grabberRighthand = viz.addAvatar("glove.cfg")

#footplane = viz.addChild("VectorBootzweiFuesse.svg")

#def addFootPlane():
#	footplane = vizshape.addPlane([0.3, 0.3],vizshape.AXIS_Y)
#	footTex = viz.addTexture('path2995.png')
#	footplane.texture(footTex)


##
# This variable contains the tool for the grabbing.
# \see ungrab, releaseBall, grabEvent 
#tool = grabber.Grabber(usingPhysics=True, usingSprings=False, highlightMode=highlighter.MODE_OUTLINE)
tool = grabber.Grabber(usingPhysics=True, usingSprings=True, highlightMode=highlighter.MODE_NONE, placementMode = tools.placer.MODE_MID_AIR, updatePriority=vizconnect.PRIORITY_ANIMATOR+3)
#tool = grabber.Grabber(usingPhysics=True, usingSprings=True, highlightMode=highlighter.MODE_NONE) #updatePriority=vizconnect.PRIORITY_ANIMATOR+10)
#(tool._currentHighlighter).setColor([1.0,0.0,1.0]) # color violet
#(tool._currentHighlighter)._highlightRadius = 0.05

#collisionTester =  tool.getCollisionTester()
#print "collisionTester= ",
#print collisionTester

##
# Creates a proximity manager. This manager handles the ball sensors (shrink-Sensor) and events (e.g. \ref grabEvent or \ref releaseTheBall).
# \see ball
# \see releaseTheBall, grabEvent, shrinkTheBall, moveTheBall
manager = vizproximity.Manager()

#this variable contains the manager for the failAreaSensor 
manager2 = vizproximity.Manager()
##
# This variable contains the manager for \ref ball and \ref ungrab.
# \see ball
# \see ungrab
manager3 = vizproximity.Manager()

##
# This variable contains the manager for the \ref viapoint.
# \see viapoint
manager4 = vizproximity.Manager()
manager4.setDebugColor([1.0,0.0,0.0])

##
# It will contain sensors for the start-torus and the \ref viapoint box.
# \see addStartSensor, addSoundSensor, sendMyCustomEvent
sensorarray = []

##
# Contains the targetobject of the \ref ball. It is generated in the method \ref showPlacement. Interacts with \ref manager2.
# \see ball, manager2
# \see showPlacement
t = None

##
# It contains a 'sad' trombone sound. This sound will be played when the ball get dropped and the trials fails.\n
# I was downloaded from https://soundbible.com/about.php or https://soundbible.com/1830-Sad-Trombone.html resp.
# Creator is Joe Lamb and it is under Attribution 3.0 license.
# \see 
#sad = viz.addAudio('Sad_Trombone-Joe_Lamb-665429450.mp3')

#success = viz.addAudio('positive-game-bling-sound-effect-59094239.mp3')
success2 = viz.addAudio('achiement-4-sound-effect-6274415.mp3')

fail = viz.addAudio('end-tone-01-sound-effect-665284.mp3')
#fail2 = viz.addAudio('negative-game-hit-01-sound-effect-47344971.mp3')



##
# Contains the audio response for passing the \ref viapoint.
# \see viapoint
# \see playSound
#audio1 = viz.addAudio('Robot_blip-Marianne_Gagnon-120342607.mp3')

##
# Contains the audio response for passing the startpoint or starttorus.
# \see viapoint
# \see doTypeA, doTypeB, doTypeC, doTypeD
#audio2 = viz.addAudio('Tick-DeepFrozenApps-397275646.mp3')


##
# This variable contains the index of a marker. 
m000 = 0

##
# This variable contains the index of a marker. 
m001 = 1

##
# This variable contains the index of a marker. 
m002 = 2

##
# This variable contains the index of a marker. 
m003 = 3

##
# This variable contains the index of a marker. 
m004 = 4

##
# This variable contains the index of a marker. 
m005 = 5

##
# This variable contains the index of a marker. 
m006 = 6

##
# This variable contains the index of a marker. 
m007 = 7

##
# This variable contains the index of a marker. 
m008 = 8

##
# This variable contains the index of a marker. 
m009 = 9

##
# This variable contains the index of a marker. 
m010 = 10

##
# This variable contains the index of a marker. 
m011 = 11

##
# This variable contains the index of a marker. 
m012 = 12

##
# This variable contains the index of a marker. 
m013 = 13

##
# This variable contains the index of a marker. 
m014 = 14

##
# This variable contains the index of a marker. 
m015 = 15

##
# This variable contains the index of a marker. 
m016 = 16

##
# This variable contains the index of a marker. 
m017 = 17

##
# This variable contains the index of a marker. 
m018 = 18

##
# This variable contains the index of a marker. 
m019 = 19

##
# This variable contains the index of a marker. 
m020 = 20

##
# This variable contains the index of a marker. 
m021 = 21

##
# This variable contains the index of a marker. 
m022 = 22

##
# This variable contains the index of a marker. 
m023 = 23

##
# This variable contains the index of a marker. 
m024 = 24

##
# This variable contains the index of a marker. 
m025 = 25

##
# This variable contains the index of a marker. 
m026 = 26

##
# This variable contains the index of a marker. 
m027 = 27

##
# This variable contains the index of a marker. 
m028 = 28

##
# This variable contains the index of a marker. 
m029 = 29

##
# This variable contains the index of a marker. 
m030 = 30

##
# This variable contains the index of a marker. 
m031 = 31

##
# This variable contains the index of a marker. 
m032 = 32

##
# This variable contains the index of a marker. 
m033 = 33

##
# This variable contains the index of a marker. 
m034 = 34

##
# This variable contains the index of a marker. 
m035 = 35

##
# This variable contains the index of a marker. 
m036 = 36

##
# This variable contains the index of a marker. 
m037 = 37

#06.09.21: additional tracker for controller
##
# This variable contains the index of a marker. 
m038 = 38

##
# This variable will contain the phasespace marker with the index of \ref m000.
pointTracker000 = None

##
# This variable will contain the phasespace marker with the index of \ref m001.
pointTracker001 = None

##
# This variable will contain the phasespace marker with the index of \ref m002.
pointTracker002 = None

##
# This variable will contain the phasespace marker with the index of \ref m003.
pointTracker003 = None

##
# This variable will contain the phasespace marker with the index of \ref m004.
pointTracker004 = None

##
# This variable will contain the phasespace marker with the index of \ref m005.
pointTracker005 = None

##
# This variable will contain the phasespace marker with the index of \ref m006.
pointTracker006 = None

##
# This variable will contain the phasespace marker with the index of \ref m007.
pointTracker007 = None

##
# This variable will contain the phasespace marker with the index of \ref m008.
pointTracker008 = None

##
# This variable will contain the phasespace marker with the index of \ref m009.
pointTracker009 = None

##
# This variable will contain the phasespace marker with the index of \ref m010.
pointTracker010 = None

##
# This variable will contain the phasespace marker with the index of \ref m011.
pointTracker011 = None

##
# This variable will contain the phasespace marker with the index of \ref m012.
pointTracker012 = None

##
# This variable will contain the phasespace marker with the index of \ref m013.
pointTracker013 = None

##
# This variable will contain the phasespace marker with the index of \ref m014.
pointTracker014 = None

##
# This variable will contain the phasespace marker with the index of \ref m015.
pointTracker015 = None

##
# This variable will contain the phasespace marker with the index of \ref m016.
pointTracker016 = None

##
# This variable will contain the phasespace marker with the index of \ref m017.
pointTracker017 = None

##
# This variable will contain the phasespace marker with the index of \ref m018.
pointTracker018 = None

##
# This variable will contain the phasespace marker with the index of \ref m019.
pointTracker019 = None

##
# This variable will contain the phasespace marker with the index of \ref m020.
pointTracker020 = None

##
# This variable will contain the phasespace marker with the index of \ref m021.
pointTracker021 = None

##
# This variable will contain the phasespace marker with the index of \ref m022.
pointTracker022 = None

##
# This variable will contain the phasespace marker with the index of \ref m023.
pointTracker023 = None

##
# This variable will contain the phasespace marker with the index of \ref m024.
pointTracker024 = None

##
# This variable will contain the phasespace marker with the index of \ref m025.
pointTracker025 = None

##
# This variable will contain the phasespace marker with the index of \ref m026.
pointTracker026 = None

##
# This variable will contain the phasespace marker with the index of \ref m027.
pointTracker027 = None

##
# This variable will contain the phasespace marker with the index of \ref m028.
pointTracker028 = None

##
# This variable will contain the phasespace marker with the index of \ref m029.
pointTracker029 = None

##
# This variable will contain the phasespace marker with the index of \ref m030.
pointTracker030 = None

##
# This variable will contain the phasespace marker with the index of \ref m031.
pointTracker031 = None

##
# This variable will contain the phasespace marker with the index of \ref m032.
pointTracker032 = None

##
# This variable will contain the phasespace marker with the index of \ref m033.
pointTracker033 = None

##
# This variable will contain the phasespace marker with the index of \ref m034.
pointTracker034 = None

##
# This variable will contain the phasespace marker with the index of \ref m035.
pointTracker035 = None

##
# This variable will contain the phasespace marker with the index of \ref m036.
pointTracker036 = None

##
# This variable will contain the phasespace marker with the index of \ref m037.
pointTracker037 = None

#06.09.21: additional tracker for controller
# This variable will contain the phasespace marker with the index of \ref m037.
pointTracker038 = None

##
# It will contain the link of \ref VIEWBALL and \c viz.MainView<a></a>.
# \see VIEWBALL
vclink = None

##
# This variable will contain the Vive headtracker. It will be linked with the \ref headtarget<a></a>.
headTracker = None

##
# It will contain a link of \ref navigationNode and \c viz.MainView. This link will
# get preMultLinkable.
viewLink = None

##
# It contains a \c viz.Group and will be linked with \ref viewLink<a></a>.
# \see viewLink
navigationNode = viz.addGroup()

##
# It will contain the vrpn plugin. This virtual server is needed for the rigid bodies.
# \see VRPN_SOURCE, rigidTracker, rigidTracker2, rigidTracker, rigidTracker2, pointTracker000, pointTracker001, pointTracker002, 
# pointTracker003, pointTracker004, pointTracker005, pointTracker006, pointTracker007, pointTracker008, pointTracker009, 
# pointTracker010, pointTracker011, pointTracker012, pointTracker013, pointTracker014, pointTracker015, pointTracker016, 
# pointTracker017, pointTracker018, pointTracker019, pointTracker020, pointTracker021, pointTracker022, pointTracker023, 
# pointTracker024, pointTracker025, pointTracker026, pointTracker027, pointTracker028, pointTracker029, pointTracker030, 
# pointTracker031, pointTracker032, pointTracker033, pointTracker034, pointTracker035, pointTracker036, pointTracker037, pointtracker038
vrpn = None

##
# This variable is a string, which is the address for the virual vrpn server.
# \see vrpn
VRPN_SOURCE = 'Tracker0@localhost'

# Falls vergessen wurde zu setzen
if (os.environ['COMPUTERNAME'] == "PC04162"):
	notinthevrlab = False
	print("we are in the lab")
else:
	notinthevrlab = True

##
# Adds ground for collide. Also here:
# \code{.py}
# ground.visible(viz.OFF)
# ground.collidePlane()
# \endcode
# If \ref notinthevrlab is set to \c False, it should be the room.
# \see notinthevrlab
if (notinthevrlab):
	ground = viz.addChild('ground.osgb')
	ground.collidePlane()
else:
	#Todo set back to room
	#ground = viz.addChild("room22.obj") # load the background
	ground = viz.addChild('ground.osgb')
	ground.collidePlane()
	ground.disable(viz.LIGHTING)

if (notinthevrlab): #unten im Labor dann auf False und anpassen
	target1 = vizproximity.Target(grabberLefthand)
	headtarget = vizproximity.Target(grabberLefthand)

	manager.addTarget(target1)
	manager2.addTarget(target1)
	manager3.addTarget(target1)
	manager4.addTarget(target1)

	del vrpn
	del VRPN_SOURCE
	del rigidSensor
	del rigidSensor2
	del rigidTracker
	del rigidTracker2
	
	viz.go()
else:
	vrpn = viz.addExtension('vrpn7.dle')

	if (isItSuit):
		rigidSensor = 38
		rigidSensor2 = 39
	else:
		rigidSensor = 6
		rigidSensor2 = 7

#		rigidSensor = 7
#		rigidSensor2 = 8
	
	# 10. Juni 2021: Rigid bodies raus
	#rigidTracker  = vrpn.addTracker(VRPN_SOURCE, rigidSensor2)
	#rigidTracker2 = vrpn.addTracker(VRPN_SOURCE, rigidSensor)

	if (not isItSuit):
		print("we do not have a suit")
		tracker = vrpn.addTracker(VRPN_SOURCE,0)
#		FootTracker2 = vrpn.addTracker(VRPN_SOURCE,25)
		print(tracker)
#		print(FootTracker2)
#		FootTracker2.swapPos([-1,2,3])
		tracker.swapPos([-1,2,3]) #depending on the direction of your SteamVR playground, this may not be necessary
		blink = vizshape.addSphere(0.01)
		#ball2 = vizshape.addSphere(0.01, color = viz.BLACK)

		link = viz.link(tracker, blink)
		#print(link)
		# 10. Juni 2021
#		pointTracker000 = vrpn.addTracker(VRPN_SOURCE, m000)
#		pointTracker001 = vrpn.addTracker(VRPN_SOURCE, m001)
#		pointTracker002 = vrpn.addTracker(VRPN_SOURCE, m002)
#		pointTracker003 = vrpn.addTracker(VRPN_SOURCE, m003)
#		pointTracker004 = vrpn.addTracker(VRPN_SOURCE, m004)
#		pointTracker005 = vrpn.addTracker(VRPN_SOURCE, m005)
	else:
		print("we ARE using a suit")
		pointTracker000 = vrpn.addTracker(VRPN_SOURCE, m000)
		pointTracker001 = vrpn.addTracker(VRPN_SOURCE, m001)
		pointTracker002 = vrpn.addTracker(VRPN_SOURCE, m002)
		pointTracker003 = vrpn.addTracker(VRPN_SOURCE, m003)
		pointTracker004 = vrpn.addTracker(VRPN_SOURCE, m004)
		pointTracker005 = vrpn.addTracker(VRPN_SOURCE, m005)
		pointTracker006 = vrpn.addTracker(VRPN_SOURCE, m006)
		pointTracker007 = vrpn.addTracker(VRPN_SOURCE, m007)
		pointTracker008 = vrpn.addTracker(VRPN_SOURCE, m008)
		pointTracker009 = vrpn.addTracker(VRPN_SOURCE, m009)
		pointTracker010 = vrpn.addTracker(VRPN_SOURCE, m010)
		pointTracker011 = vrpn.addTracker(VRPN_SOURCE, m011)
		pointTracker012 = vrpn.addTracker(VRPN_SOURCE, m012)
		pointTracker013 = vrpn.addTracker(VRPN_SOURCE, m013)
		pointTracker014 = vrpn.addTracker(VRPN_SOURCE, m014)
		pointTracker015 = vrpn.addTracker(VRPN_SOURCE, m015)
		pointTracker016 = vrpn.addTracker(VRPN_SOURCE, m016)
		pointTracker017 = vrpn.addTracker(VRPN_SOURCE, m017)
		pointTracker018 = vrpn.addTracker(VRPN_SOURCE, m018)
		pointTracker019 = vrpn.addTracker(VRPN_SOURCE, m019)
		pointTracker020 = vrpn.addTracker(VRPN_SOURCE, m020)
		pointTracker021 = vrpn.addTracker(VRPN_SOURCE, m021)
		pointTracker022 = vrpn.addTracker(VRPN_SOURCE, m022)
		pointTracker023 = vrpn.addTracker(VRPN_SOURCE, m023)
		pointTracker024 = vrpn.addTracker(VRPN_SOURCE, m024)
		#print(pointTracker024)
		pointTracker025 = vrpn.addTracker(VRPN_SOURCE, m025)
		pointTracker026 = vrpn.addTracker(VRPN_SOURCE, m026)
		pointTracker027 = vrpn.addTracker(VRPN_SOURCE, m027)
		pointTracker028 = vrpn.addTracker(VRPN_SOURCE, m028)
		pointTracker029 = vrpn.addTracker(VRPN_SOURCE, m029)
		pointTracker030 = vrpn.addTracker(VRPN_SOURCE, m030)
		pointTracker031 = vrpn.addTracker(VRPN_SOURCE, m031)
		pointTracker032 = vrpn.addTracker(VRPN_SOURCE, m032)
		pointTracker033 = vrpn.addTracker(VRPN_SOURCE, m033)
		pointTracker034 = vrpn.addTracker(VRPN_SOURCE, m034)
		pointTracker035 = vrpn.addTracker(VRPN_SOURCE, m035)
		pointTracker036 = vrpn.addTracker(VRPN_SOURCE, m036)
		pointTracker037 = vrpn.addTracker(VRPN_SOURCE, m037)
		#06.09.21 
		tracker = vrpn.addTracker(VRPN_SOURCE, m038)

		#1.10. Funktioniert jetzt so in dieser Form im Großen und Ganzen, allerdings spiegelverkehrt (ohne KoordinatenTransformation) schauen, ob das durch die Transformation behoben wird), ansonsten mit swappos arbeiten
		blink2 = vizshape.addSphere(0.01)
		blink3 = vizshape.addSphere(0.01)
		blink4 = vizshape.addSphere(0.01)
		blink5 = vizshape.addSphere(0.01)
		blink6 = vizshape.addSphere(0.01)
		blink7 = vizshape.addSphere(0.01)
		
		pointTracker025.swapPos([-1,2,3])
		pointTracker026.swapPos([-1,2,3])
		pointTracker027.swapPos([-1,2,3])
		pointTracker036.swapPos([-1,2,3])
		pointTracker037.swapPos([-1,2,3])
		tracker.swapPos([-1,2,3])
		
		#blink2.setPosition(pointTracker025.getPosition())
		
		
		FootLink = viz.link(pointTracker025, blink2)
		FootLink2 = viz.link(pointTracker026, blink3)
		FootLink3 = viz.link(pointTracker027, blink4)
		FootLink4 = viz.link(pointTracker036, blink5)
		FootLink5 = viz.link(pointTracker037, blink6)
		FootLink6 = viz.link(tracker, blink7)
		
		
	# 10. Juni 2021: Rigid bodies raus
	#rigidTracker.swapQuat([-1, 2 ,3, -4])
	#rigidTracker2.swapQuat([-1, 2, 3, -4])
	
	##
	# It contains the vive hmd object.
	hmd = steamvr.HMD()
	
	if (not hmd.getSensor()):
		sys.exit('SteamVR HMD not detected')
	
	viewLink = viz.link(navigationNode, viz.MainView)
	viewLink.preMultLinkable(hmd.getSensor())
	headTracker = hmd.getSensor()
	print("Hi")
	#prepare VIEWBALL
	vclink = viz.link(viz.MainView, VIEWBALL)

	for controller in steamvr.getControllerList():
		# Create model for controller
		controller.model = controller.addModel(parent=navigationNode)
		
		if (not controller.model):
			controller.model = viz.addGroup(parent=navigationNode)
		
		
		controller.model.disable(viz.INTERSECTION)
		print controller
		print controller.model
		
		l = viz.link(controller, controller.model)
		controllerobject =  controller.model
		controllersteam = controller
		l2 = viz.link(controllerobject, tool)
		#controllerobject.collideSphere(radius=0.03)
		print tool
		print l.getSrc()
		print l2.getSrc()
		print l2.getDst()
		# 10. Juni 2021
		
		print tool.getItems()


	##
	# A group node, which will have \ref linkable1 and \ref linkable2 as children.
	# \c group will have set \ref T as matrix.
	# \see linkable1, linkable2, myLink1, myLink2, rigidTracker, rigidTracker2, T
	group = viz.addGroup()
	group.setMatrix(T)
	
	linkable = viz.link(tracker, viz.NullLinkable)
	linkable.postMultLinkable(group)

	if(isItSuit):
#		# Hier Anpassung mit T-Matrix für die restlichen 38 Tracker  pointTracker000, etc.
		linkable1 = viz.link(pointTracker000, viz.NullLinkable)
		linkable1.postMultLinkable(group)
		linkable2 = viz.link(pointTracker001, viz.NullLinkable)
		linkable2.postMultLinkable(group)
		linkable3 = viz.link(pointTracker002, viz.NullLinkable)
		linkable3.postMultLinkable(group)
		linkable4 = viz.link(pointTracker003, viz.NullLinkable)
		linkable4.postMultLinkable(group)
		linkable5 = viz.link(pointTracker004, viz.NullLinkable)
		linkable5.postMultLinkable(group)
		linkable6 = viz.link(pointTracker005, viz.NullLinkable)
		linkable6.postMultLinkable(group)
		linkable7 = viz.link(pointTracker006, viz.NullLinkable)
		linkable7.postMultLinkable(group)
		linkable8 = viz.link(pointTracker007, viz.NullLinkable)
		linkable8.postMultLinkable(group)
		linkable9 = viz.link(pointTracker008, viz.NullLinkable)
		linkable9.postMultLinkable(group)
		linkable10 = viz.link(pointTracker009, viz.NullLinkable)
		linkable10.postMultLinkable(group)
		linkable11 = viz.link(pointTracker010, viz.NullLinkable)
		linkable11.postMultLinkable(group)
		linkable12 = viz.link(pointTracker011, viz.NullLinkable)
		linkable12.postMultLinkable(group)
		linkable13 = viz.link(pointTracker012, viz.NullLinkable)
		linkable13.postMultLinkable(group)
		linkable14 = viz.link(pointTracker013, viz.NullLinkable)
		linkable14.postMultLinkable(group)
		linkable15 = viz.link(pointTracker014, viz.NullLinkable)
		linkable15.postMultLinkable(group)
		linkable16 = viz.link(pointTracker015, viz.NullLinkable)
		linkable16.postMultLinkable(group)
		linkable17 = viz.link(pointTracker016, viz.NullLinkable)
		linkable17.postMultLinkable(group)
		linkable18 = viz.link(pointTracker017, viz.NullLinkable)
		linkable18.postMultLinkable(group)
		linkable19 = viz.link(pointTracker018, viz.NullLinkable)
		linkable19.postMultLinkable(group)
		linkable20 = viz.link(pointTracker019, viz.NullLinkable)
		linkable20.postMultLinkable(group)
		linkable21 = viz.link(pointTracker020, viz.NullLinkable)
		linkable21.postMultLinkable(group)
		linkable22 = viz.link(pointTracker021, viz.NullLinkable)
		linkable22.postMultLinkable(group)
		linkable23 = viz.link(pointTracker022, viz.NullLinkable)
		linkable23.postMultLinkable(group)
		linkable24 = viz.link(pointTracker023, viz.NullLinkable)
		linkable24.postMultLinkable(group)
		linkable25 = viz.link(pointTracker024, viz.NullLinkable)
		linkable25.postMultLinkable(group)
		linkable26 = viz.link(pointTracker025, viz.NullLinkable)
		linkable26.postMultLinkable(group)
		linkable27 = viz.link(pointTracker026, viz.NullLinkable)
		linkable27.postMultLinkable(group)
		linkable28 = viz.link(pointTracker027, viz.NullLinkable)
		linkable28.postMultLinkable(group)
		linkable29 = viz.link(pointTracker028, viz.NullLinkable)
		linkable29.postMultLinkable(group)
		linkable30 = viz.link(pointTracker029, viz.NullLinkable)
		linkable30.postMultLinkable(group)
		linkable31 = viz.link(pointTracker030, viz.NullLinkable)
		linkable31.postMultLinkable(group)
		linkable32 = viz.link(pointTracker031, viz.NullLinkable)
		linkable32.postMultLinkable(group)
		linkable33 = viz.link(pointTracker032, viz.NullLinkable)
		linkable33.postMultLinkable(group)
		linkable34 = viz.link(pointTracker033, viz.NullLinkable)
		linkable34.postMultLinkable(group)
		linkable35 = viz.link(pointTracker034, viz.NullLinkable)
		linkable35.postMultLinkable(group)
		linkable36 = viz.link(pointTracker035, viz.NullLinkable)
		linkable36.postMultLinkable(group)
		linkable37 = viz.link(pointTracker036, viz.NullLinkable)
		linkable37.postMultLinkable(group)
		linkable38 = viz.link(pointTracker037, viz.NullLinkable)
		linkable38.postMultLinkable(group)
		linkable39 = viz.link(tracker, viz.NullLinkable)
		linkable39.postMultLinkable(group)
	else:
		pass
	
	# 10. Juni 2021: changed
	target1 = vizproximity.Target(controllersteam)
	headtarget = vizproximity.Target(headTracker)

	manager.addTarget(target1)
	manager2.addTarget(target1)
	manager3.addTarget(target1)
	manager4.addTarget(target1)

	viz.vsync(1)
	viz.setOption('viz.glFinish', 1)
	viz.setMultiSample(8)
	viz.go()

	viz.logNotice('******************************************************************************')
	for monitor in viz.window.getMonitorList():
		print "** " + monitor.name
		print '**   ',monitor
	viz.logNotice('******************************************************************************')


##
# Plane as starting- and via-point. Also coded here, the definition of color, visibility and the position:
# \code{.py}
# plane.color(1.0,0.0,0.0)
# plane.ambient([1.0,0.0,0.0])
# plane.emissive([1.0,0.0,0.0])
# plane.visible(viz.OFF)
# plane.setPosition(0.0,10.0,0.0)
# \endcode
# \see varPlaneDim,varPlaneDim
plane = vizshape.addPlane([varPlaneDim/2,varPlaneDim],vizshape.AXIS_Y)
plane.color(1.0, 0.0, 0.0)
plane.ambient([1.0, 0.0, 0.0])
plane.emissive([1.0, 0.0, 0.0])
plane.visible(viz.OFF)
plane.setPosition(0.0, 10.0, 0.0)


## 
# Adds a point light in 5 meters height.
light = vizfx.addPointLight(color=viz.WHITE, pos=(0,5,0))

## 
# This method prepares the next block. It uses \ref setCUSTOM and clears the sensors
# of the managers \ref manager, \ref manager3, \ref manager4 and \ref manager5. It 
# also clears the texts of \ref time_text, \ref wrongball_text and \ref ball_text. 
# It sets the \ref shelfA, \ref shelfB, \ref shelfC and \ref shelfD to \c None. It
#  also offers an optional \ref validation.
# \see shelfA, shelfB, shelfC, shelfD, ball, manager, manager3, manager4, manager5, 
# target1, target2, target5, placement, viapoint, 
# viapointpassed, wrongballs, time_text, wrongball_text, ball_text
# \see setGoodBalls, validation
def prepareForNextBlock():
	global shelfA
	global ball
	global manager
	global manager2
	global manager3
	global manager4
	global viapoint
	global target1
	global target5
	global notinthevrlab
	global viapoint
	global viapointpassed
	global time_text
	global wrongball_text
	global ball_text
	global overTheEdge

	time_text.clearActions()
	time_text.alpha(1.0)
	time_text.color(viz.WHITE)
	time_text.setScale([0.01]*3)
	time_text.message('')

	wrongball_text.clearActions()
	wrongball_text.alpha(1.0)
	wrongball_text.color(viz.RED)
	wrongball_text.setScale([0.01]*3)
	wrongball_text.message('')

	ball_text.clearActions()
	ball_text.alpha(1.0)
	ball_text.color(viz.GREEN)
	ball_text.setScale([0.01]*3)
	ball_text.message('')

	shelfA = None

	manager.clearSensors()
	manager2.clearSensors()
	manager3.clearSensors()
	manager4.clearSensors()

	if (ball is not None):
		print (ball.getNode()).getAction()
		(ball.getNode()).clearActions()
		print("prepareForNextBlock: (ball.getNode()).clearActions()")
	else:
		pass

	if  (not notinthevrlab):
		manager.addTarget(target1)
		manager2.addTarget(target1)
		manager3.addTarget(target1)
		manager4.addTarget(target1)
	else:
		manager.addTarget(target1)
		manager2.addTarget(target1)
		manager3.addTarget(target1)
		manager4.addTarget(target1)

	print manager.getTargets()
	print manager3.getTargets()
	#print("got here")
	setCUSTOM(False)

	if viapoint != None:
		viapoint.remove()
	else:
		pass

	viapoint = None
	prepareScene()

	setvarTrialAchievement(False)
	actionevent = None
	viapointpassed = False
	overTheEdge = False
	

	setGoodBalls(0)
	setWrongBalls(0)
	setTrial(0)
	

##
# Between two trials some variables need some preparations. Actions gets cleared (\ref ball, \ref placement), nodes will be removed (\ref viapoint) and other variables
# will be set to \c False or \c None. This method also clears the targets and sensors of \b all managers. But then it adds \ref target1 to \ref manager and \ref manager3. 
# It adds \ref headtarget to \ref manager4 and \ref target5 to \ref manager5. \n
# It also calls \ref prepareScene<a></a>.
# \see ball, placement, manager, manager2, manager3, manager4, manager5, target1, target2, target5, ignore, grableftright, actionevent, notinthevrlab, viapointpassed, 
# varPlacementBallIntersection, varTrailDuration, viapoint
# \see setCUSTOM, setvarTrialAchievement, prepareScene
def prepareForNextTrial():
	global ball
	global manager
	global manager2
	global manager3
	global manager4
	global target1
	global target5
	global actionevent
	global notinthevrlab
	global viapointpassed
	global vartorusBallIntersection
	global varTrailDuration
	global viapoint
	global tool
	global overTheEdge
	global sensorarray
	global torus
	global firstGrab

	if (ball is not None):
		tool.removeItems([ball.getNode()])
	else:
		pass

	#viapoint.remove()
	viapoint = None
	setCUSTOM(False)

	print sensorarray
	for i in range(len(sensorarray)):
		sensorarray.remove(sensorarray[0])
	print sensorarray

	manager.clearSensors()
	manager.clearTargets()
	manager2.clearSensors()
	manager2.clearTargets()
	manager3.clearSensors()
	manager3.clearTargets()
	manager4.clearSensors()
	manager4.clearTargets()

	print "################################################"
	print manager4.getActiveSensors()
	print manager4.getSensors()
	print manager4.getTargets()

	
	
	if (ball is not None):
		(ball.getNode()).clearActions()
	else:
		pass

	manager.addTarget(target1)
	manager2.addTarget(target1)
	manager3.addTarget(target1)
	manager4.addTarget(target1)

	if (not notinthevrlab):
		pass
	else:
		pass

	yield prepareScene()

	setvarTrialAchievement(False)
	varTrailDuration = 0.0
	actionevent = None
	viapointpassed = False
	vartorusBallIntersection = False
	overTheEdge = False
	torus.clearAttribute(viz.ATTR_COLOR)
	torus.remove()
	firstGrab = True
	
	#setFirstRunInstruction(False)
	


##
# This method prepares the scene. It hides the start \ref plane and sets \ref ball, \ref placement, \ref varDestination
# and \ref varTrialType back to \c None. It also sets \ref varSensorsize back to the default \c -1.
# \see ball, placement
# \see hidePlane, setPlacementDestination, setTrialType, setSensorSize
def prepareScene():
	global ball
	global torus

	ball = None
	hidePlane()
	setTrialType(None)
	setSensorSize(-1.0)
	

##
# This method sets a new value for \ref vpn_id.
# \param val: a string
# \see vpn_id
# \see getVPNid
def setVPNid(val):
	global vpn_id
	vpn_id = val

##
# Returns the value of \ref vpn_id.
# \returns vpn_id
# \see vpn_id
# \see setVPNid
def getVPNid():
	global vpn_id
	return vpn_id
	
	
##
# This method sets a new value for \ref bodyweight.
# \param val: a string
# \see bodyweight
# \see getBodyweight
def setBodyweight(val):
	global varBodyweight
	varBodyweight = val

##
# Returns the value of \ref Bodyweight.
# \returns Bodyweight
# \see vpn_id
# \see setBodyweight
def getBodyweight():
	global varBodyweight
	return varBodyweight
	
	
##
# This method sets a new value for \ref shoulder-to-shoulder length.
# \param val: a string
# \see shoulder-to-shoulder length
# \see getShoulderToShoulderLength
def setShoulderToShoulderLength(val):
	global varShoulderToShoulderLength
	varShoulderToShoulderLength = val
	

##
# Returns the value of \ref ShoulderToShoulderLength.
# \returns ShoulderToShoulderLength
# \see vpn_id
# \see setShoulderToShoulderLength
def getShoulderToShoulderLength():
	global varShoulderToShoulderLength
	return varShoulderToShoulderLength
	
	
	
	
##
# This method sets a new value for \ref Upper Arm length.
# \param val: a string
# \see Upper Arm length
# \see getUpperArmLength
def setUpperArmLength(val):
	global varUpperArmLength
	varUpperArmLength = val
	

##
# Returns the value of \ref UpperArmLength.
# \returns UpperArmLength
# \see vpn_id
# \see setUpperArmLength
def getUpperArmLength():
	global varUpperArmLength
	return varUpperArmLength
	
	
##
# This method sets a new value for \ref ForeArm length.
# \param val: a string
# \see ForeArm length
# \see getForeArmLength
def setForeArmLength(val):
	global varForeArmLength
	varForeArmLength = val
	

##
# Returns the value of \ref ForeArmLength.
# \returns ForeArmLength
# \see vpn_id
# \see setForeArmLength
def getForeArmLength():
	global varForeArmLength
	return varForeArmLength
	

##
# This method helps to get a nice and fine log-entry. It is use by writeCSVfile. mF2Sac is a shortcut for 'MakeFloatToStringAndComma'.
# English float do have a point, but we need a comma.
# \param varfloat: a float
# \return string, which has a comma instead of a point
# \see writeCSVfile
def mF2Sac(varfloat):
	temp = "{:-f}".format(varfloat)
	return temp.replace('.',',')

##
# This method returns the value of \ref eventstring. It contains a note for column event of the log. It is used in \ref writeSuitData.
# \returns a string
# \see eventstring
# \see setEventstring
def getEventstring():
	global eventstring
	return eventstring

##
# This method sets the value of \ref eventstring.
# \param val: a string
# \see eventstring
# \see getEventstring
def setEventstring(val):
	global eventstring
	eventstring = val

##
# It returns the value of \ref effectstring.
# \see effectstring
# \see setEffectstring
def getEffectstring():
	global effectstring
	return effectstring

##
# It sets a new value for \ref effectstring.
# \param val: a string
# \see getEffectstring
def setEffectstring(val):	
	global effectstring
	effectstring = val

##
# It notes the 4x4 transformation matrix, which was calculatetd by coordinate_systems_model_compact.py. The data for
# this calculation was collected with coordinate_systems_calibration.py. It generates a file named
# <code>getVPNid()  +"_" + str(getBlock()) + "_matrixT.csv"</code>
# \see T, ORDNERPFAD
# \see getVPNid, getBlock
def writeTransformationMatrix():
	global T
	global ORDNERPFAD
	
	filename_T  = getVPNid()  +"_" + str(getBlock()) + "_matrixT.csv"

	if os.path.isfile(ORDNERPFAD + filename_T):
		with open(ORDNERPFAD + filename_T, 'a') as f_handle:
			np.savetxt(f_handle, [T], newline='\r', delimiter = ';', fmt='%s')
		f_handle.close()
	else:
		with open(ORDNERPFAD + filename_T, 'w') as f_handle:
			np.savetxt(f_handle, [T], newline='\r', delimiter = ';', fmt='%s')
		f_handle.close()

##
# Write an csv, which can be transformed to a C3D file.
# \see pointTracker000, pointTracker001, pointTracker002, pointTracker003, pointTracker004, pointTracker005, 
# pointTracker006, pointTracker007, pointTracker008, pointTracker009, pointTracker010, pointTracker011, 
# pointTracker012, pointTracker013, pointTracker014, pointTracker015, pointTracker016, pointTracker017, 
# pointTracker018, pointTracker019, pointTracker020, pointTracker021, pointTracker022, pointTracker023, 
# pointTracker024, pointTracker025, pointTracker026, pointTracker027, pointTracker028, pointTracker029, 
# pointTracker030, pointTracker031, pointTracker032, pointTracker033, pointTracker034, pointTracker035, 
# pointTracker036, pointTracker037, pointTracker038
def writeSuitData():
	global pointTracker000
	global pointTracker001
	global pointTracker002
	global pointTracker003
	global pointTracker004
	global pointTracker005
	global pointTracker006
	global pointTracker007
	global pointTracker008
	global pointTracker009
	global pointTracker010
	global pointTracker011
	global pointTracker012
	global pointTracker013
	global pointTracker014
	global pointTracker015
	global pointTracker016
	global pointTracker017
	global pointTracker018
	global pointTracker019
	global pointTracker020
	global pointTracker021
	global pointTracker022
	global pointTracker023
	global pointTracker024
	global pointTracker025
	global pointTracker026
	global pointTracker027
	global pointTracker028
	global pointTracker029
	global pointTracker030
	global pointTracker031
	global pointTracker032
	global pointTracker033
	global pointTracker034
	global pointTracker035
	global pointTracker036
	global pointTracker037
	global tracker

	filename2  = getVPNid()+"_"+str(getBlock())+"_c3d.csv"

	try:
		pointTracker000Position      = pointTracker000.getPosition()
		pointTracker001Position      = pointTracker001.getPosition()
		pointTracker002Position      = pointTracker002.getPosition()
		pointTracker003Position      = pointTracker003.getPosition()
		pointTracker004Position      = pointTracker004.getPosition()
		pointTracker005Position      = pointTracker005.getPosition()
		pointTracker006Position      = pointTracker006.getPosition()
		pointTracker007Position      = pointTracker007.getPosition()
		pointTracker008Position      = pointTracker008.getPosition()
		pointTracker009Position      = pointTracker009.getPosition()
		pointTracker010Position      = pointTracker010.getPosition()
		pointTracker011Position      = pointTracker011.getPosition()
		pointTracker012Position      = pointTracker012.getPosition()
		pointTracker013Position      = pointTracker013.getPosition()
		pointTracker014Position      = pointTracker014.getPosition()
		pointTracker015Position      = pointTracker015.getPosition()
		pointTracker016Position      = pointTracker016.getPosition()
		pointTracker017Position      = pointTracker017.getPosition()
		pointTracker018Position      = pointTracker018.getPosition()
		pointTracker019Position      = pointTracker019.getPosition()
		pointTracker020Position      = pointTracker020.getPosition()
		pointTracker021Position      = pointTracker021.getPosition()
		pointTracker022Position      = pointTracker022.getPosition()
		pointTracker023Position      = pointTracker023.getPosition()
		pointTracker024Position      = pointTracker024.getPosition()
		pointTracker025Position      = pointTracker025.getPosition()
		pointTracker026Position      = pointTracker026.getPosition()
		pointTracker027Position      = pointTracker027.getPosition()
		pointTracker028Position      = pointTracker028.getPosition()
		pointTracker029Position      = pointTracker029.getPosition()
		pointTracker030Position      = pointTracker030.getPosition()
		pointTracker031Position      = pointTracker031.getPosition()
		pointTracker032Position      = pointTracker032.getPosition()
		pointTracker033Position      = pointTracker033.getPosition()
		pointTracker034Position      = pointTracker034.getPosition()
		pointTracker035Position      = pointTracker035.getPosition()
		pointTracker036Position      = pointTracker036.getPosition()
		pointTracker037Position      = pointTracker037.getPosition()
		#06.09.
		pointTracker038Position      = tracker.getPosition()
		
	except:
		pointTracker000Position = [-1.0, -1.0, -1.0]
		#test 26.11.20
		#pointTracker000Position = pointTracker006.getPosition()
		pointTracker001Position = [-1.0, -1.0, -1.0]
		pointTracker002Position = [-1.0, -1.0, -1.0]
		pointTracker003Position = [-1.0, -1.0, -1.0]
		pointTracker004Position = [-1.0, -1.0, -1.0]
		pointTracker005Position = [-1.0, -1.0, -1.0]
		pointTracker006Position = [-1.0, -1.0, -1.0]
		pointTracker007Position = [-1.0, -1.0, -1.0]
		pointTracker008Position = [-1.0, -1.0, -1.0]
		pointTracker009Position = [-1.0, -1.0, -1.0]
		pointTracker010Position = [-1.0, -1.0, -1.0]
		pointTracker011Position = [-1.0, -1.0, -1.0]
		pointTracker012Position = [-1.0, -1.0, -1.0]
		pointTracker013Position = [-1.0, -1.0, -1.0]
		pointTracker014Position = [-1.0, -1.0, -1.0]
		pointTracker015Position = [-1.0, -1.0, -1.0]
		pointTracker016Position = [-1.0, -1.0, -1.0]
		pointTracker017Position = [-1.0, -1.0, -1.0]
		pointTracker018Position = [-1.0, -1.0, -1.0]
		pointTracker019Position = [-1.0, -1.0, -1.0]
		pointTracker020Position = [-1.0, -1.0, -1.0]
		pointTracker021Position = [-1.0, -1.0, -1.0]
		pointTracker022Position = [-1.0, -1.0, -1.0]
		pointTracker023Position = [-1.0, -1.0, -1.0]
		pointTracker024Position = [-1.0, -1.0, -1.0]
		pointTracker025Position = [-1.0, -1.0, -1.0]
		pointTracker026Position = [-1.0, -1.0, -1.0]
		pointTracker027Position = [-1.0, -1.0, -1.0]
		pointTracker028Position = [-1.0, -1.0, -1.0]
		pointTracker029Position = [-1.0, -1.0, -1.0]
		pointTracker030Position = [-1.0, -1.0, -1.0]
		pointTracker031Position = [-1.0, -1.0, -1.0]
		pointTracker032Position = [-1.0, -1.0, -1.0]
		pointTracker033Position = [-1.0, -1.0, -1.0]
		pointTracker034Position = [-1.0, -1.0, -1.0]
		pointTracker035Position = [-1.0, -1.0, -1.0]
		pointTracker036Position = [-1.0, -1.0, -1.0]
		pointTracker037Position = [-1.0, -1.0, -1.0]
		#06.09.
		pointTracker038Position = [-1.0, -1.0, -1.0]

	listenarray = [[pointTracker000Position[0], pointTracker000Position[1], pointTracker000Position[2],
					pointTracker001Position[0], pointTracker001Position[1], pointTracker001Position[2],
					pointTracker002Position[0], pointTracker002Position[1], pointTracker002Position[2],
					pointTracker003Position[0], pointTracker003Position[1], pointTracker003Position[2],
					pointTracker004Position[0], pointTracker004Position[1], pointTracker004Position[2],
					pointTracker005Position[0], pointTracker005Position[1], pointTracker005Position[2],
					pointTracker006Position[0], pointTracker006Position[1], pointTracker006Position[2],
					pointTracker007Position[0], pointTracker007Position[1], pointTracker007Position[2],
					pointTracker008Position[0], pointTracker008Position[1], pointTracker008Position[2],
					pointTracker009Position[0], pointTracker009Position[1], pointTracker009Position[2],
					pointTracker010Position[0], pointTracker010Position[1], pointTracker010Position[2],
					pointTracker011Position[0], pointTracker011Position[1], pointTracker011Position[2],
					pointTracker012Position[0], pointTracker012Position[1], pointTracker012Position[2],
					pointTracker013Position[0], pointTracker013Position[1], pointTracker013Position[2],
					pointTracker014Position[0], pointTracker014Position[1], pointTracker014Position[2],
					pointTracker015Position[0], pointTracker015Position[1], pointTracker015Position[2],
					pointTracker016Position[0], pointTracker016Position[1], pointTracker016Position[2],
					pointTracker017Position[0], pointTracker017Position[1], pointTracker017Position[2],
					pointTracker018Position[0], pointTracker018Position[1], pointTracker018Position[2],
					pointTracker019Position[0], pointTracker019Position[1], pointTracker019Position[2],
					pointTracker020Position[0], pointTracker020Position[1], pointTracker020Position[2],
					pointTracker021Position[0], pointTracker021Position[1], pointTracker021Position[2],
					pointTracker022Position[0], pointTracker022Position[1], pointTracker022Position[2],
					pointTracker023Position[0], pointTracker023Position[1], pointTracker023Position[2],
					pointTracker024Position[0], pointTracker024Position[1], pointTracker024Position[2],
					pointTracker025Position[0], pointTracker025Position[1], pointTracker025Position[2],
					pointTracker026Position[0], pointTracker026Position[1], pointTracker026Position[2],
					pointTracker027Position[0], pointTracker027Position[1], pointTracker027Position[2],
					pointTracker028Position[0], pointTracker028Position[1], pointTracker028Position[2],
					pointTracker029Position[0], pointTracker029Position[1], pointTracker029Position[2],
					pointTracker030Position[0], pointTracker030Position[1], pointTracker030Position[2],
					pointTracker031Position[0], pointTracker031Position[1], pointTracker031Position[2],
					pointTracker032Position[0], pointTracker032Position[1], pointTracker032Position[2],
					pointTracker033Position[0], pointTracker033Position[1], pointTracker033Position[2],
					pointTracker034Position[0], pointTracker034Position[1], pointTracker034Position[2],
					pointTracker035Position[0], pointTracker035Position[1], pointTracker035Position[2],
					pointTracker036Position[0], pointTracker036Position[1], pointTracker036Position[2],
					pointTracker037Position[0], pointTracker037Position[1], pointTracker037Position[2],
					#06.09.
					pointTracker038Position[0], pointTracker038Position[1], pointTracker038Position[2],
					getEventstring(), str(time.time())]]

	if (os.path.isfile("F:\\" + filename2)):
		with open("F:\\" + filename2, 'a') as f_handle:
			np.savetxt(f_handle, listenarray, newline='\r', delimiter = ';', fmt='%s')
		f_handle.close()
	else:
		listenheader = "pointTracker000_x; pointTracker000_y; pointTracker000_z; \
		pointTracker001_x; pointTracker001_y; pointTracker001_z; \
		pointTracker002_x; pointTracker002_y; pointTracker002_z; \
		pointTracker003_x; pointTracker003_y; pointTracker003_z; \
		pointTracker004_x; pointTracker004_y; pointTracker004_z; \
		pointTracker005_x; pointTracker005_y; pointTracker005_z; \
		pointTracker006_x; pointTracker006_y; pointTracker006_z; \
		pointTracker007_x; pointTracker007_y; pointTracker007_z; \
		pointTracker008_x; pointTracker008_y; pointTracker008_z; \
		pointTracker009_x; pointTracker009_y; pointTracker009_z; \
		pointTracker010_x; pointTracker010_y; pointTracker010_z; \
		pointTracker011_x; pointTracker011_y; pointTracker011_z; \
		pointTracker012_x; pointTracker012_y; pointTracker012_z; \
		pointTracker013_x; pointTracker013_y; pointTracker013_z; \
		pointTracker014_x; pointTracker014_y; pointTracker014_z; \
		pointTracker015_x; pointTracker015_y; pointTracker015_z; \
		pointTracker016_x; pointTracker016_y; pointTracker016_z; \
		pointTracker017_x; pointTracker017_y; pointTracker017_z; \
		pointTracker018_x; pointTracker018_y; pointTracker018_z; \
		pointTracker019_x; pointTracker019_y; pointTracker019_z; \
		pointTracker020_x; pointTracker020_y; pointTracker020_z; \
		pointTracker021_x; pointTracker021_y; pointTracker021_z; \
		pointTracker022_x; pointTracker022_y; pointTracker022_z; \
		pointTracker023_x; pointTracker023_y; pointTracker023_z; \
		pointTracker024_x; pointTracker024_y; pointTracker024_z; \
		pointTracker025_x; pointTracker025_y; pointTracker025_z; \
		pointTracker026_x; pointTracker026_y; pointTracker026_z; \
		pointTracker027_x; pointTracker027_y; pointTracker027_z; \
		pointTracker028_x; pointTracker028_y; pointTracker028_z; \
		pointTracker029_x; pointTracker029_y; pointTracker029_z; \
		pointTracker030_x; pointTracker030_y; pointTracker030_z; \
		pointTracker031_x; pointTracker031_y; pointTracker031_z; \
		pointTracker032_x; pointTracker032_y; pointTracker032_z; \
		pointTracker033_x; pointTracker033_y; pointTracker033_z; \
		pointTracker034_x; pointTracker034_y; pointTracker034_z; \
		pointTracker035_x; pointTracker035_y; pointTracker035_z; \
		pointTracker036_x; pointTracker036_y; pointTracker036_z; \
		pointTracker037_x; pointTracker037_y; pointTracker037_z; \
		pointTracker038_x; pointTracker038_y; pointTracker038_z; \
		Event; Zeit"

		with open("F:\\"+filename2,'a') as f_handle:
			np.savetxt(f_handle, listenarray, newline='\r', header=listenheader, delimiter = ';', fmt='%s')
		f_handle.close()

		del listenheader

	setEventstring('')

##
# Writes a csv file, which can be transformed to a c3d file.
# \see pointTracker000, pointTracker001, pointTracker002, pointTracker003, pointTracker004, pointTracker005, 
# pointTracker006, pointTracker007, pointTracker008, pointTracker009, pointTracker010, pointTracker011, 
# pointTracker012, pointTracker013, pointTracker014, pointTracker015, pointTracker016, pointTracker017, 
# pointTracker018, pointTracker019, pointTracker020, pointTracker021, pointTracker022, pointTracker023, 
# pointTracker024, pointTracker025, pointTracker026, pointTracker027, pointTracker028, pointTracker029, 
# pointTracker030, pointTracker031, pointTracker032, pointTracker033, pointTracker034, pointTracker035, 
# pointTracker036, pointTracker037, pointTracker038
# \see writeSuitData
def writeSuitData2():
	global pointTracker000
	global pointTracker001
	global pointTracker002
	global pointTracker003
	global pointTracker004
	global pointTracker005
	global pointTracker006
	global pointTracker007
	global pointTracker008
	global pointTracker009
	global pointTracker010
	global pointTracker011
	global pointTracker012
	global pointTracker013
	global pointTracker014
	global pointTracker015
	global pointTracker016
	global pointTracker017
	global pointTracker018
	global pointTracker019
	global pointTracker020
	global pointTracker021
	global pointTracker022
	global pointTracker023
	global pointTracker024
	global pointTracker025
	global pointTracker026
	global pointTracker027
	global pointTracker028
	global pointTracker029
	global pointTracker030
	global pointTracker031
	global pointTracker032
	global pointTracker033
	global pointTracker034
	global pointTracker035
	global pointTracker036
	global pointTracker037
	#06.09.
	global pointTracker038

	filename2  = getVPNid()+"_"+str(getBlock())+"_c3d.binarypoint"
	filename3  = getVPNid()+"_"+str(getBlock())+"_c3d.event"

	try:
		pointTracker000Position      = pointTracker000.getPosition()
		pointTracker001Position      = pointTracker001.getPosition()
		pointTracker002Position      = pointTracker002.getPosition()
		pointTracker003Position      = pointTracker003.getPosition()
		pointTracker004Position      = pointTracker004.getPosition()
		pointTracker005Position      = pointTracker005.getPosition()
		pointTracker006Position      = pointTracker006.getPosition()
		pointTracker007Position      = pointTracker007.getPosition()
		pointTracker008Position      = pointTracker008.getPosition()
		pointTracker009Position      = pointTracker009.getPosition()
		pointTracker010Position      = pointTracker010.getPosition()
		pointTracker011Position      = pointTracker011.getPosition()
		pointTracker012Position      = pointTracker012.getPosition()
		pointTracker013Position      = pointTracker013.getPosition()
		pointTracker014Position      = pointTracker014.getPosition()
		pointTracker015Position      = pointTracker015.getPosition()
		pointTracker016Position      = pointTracker016.getPosition()
		pointTracker017Position      = pointTracker017.getPosition()
		pointTracker018Position      = pointTracker018.getPosition()
		pointTracker019Position      = pointTracker019.getPosition()
		pointTracker020Position      = pointTracker020.getPosition()
		pointTracker021Position      = pointTracker021.getPosition()
		pointTracker022Position      = pointTracker022.getPosition()
		pointTracker023Position      = pointTracker023.getPosition()
		pointTracker024Position      = pointTracker024.getPosition()
		pointTracker025Position      = pointTracker025.getPosition()
		pointTracker026Position      = pointTracker026.getPosition()
		pointTracker027Position      = pointTracker027.getPosition()
		pointTracker028Position      = pointTracker028.getPosition()
		pointTracker029Position      = pointTracker029.getPosition()
		pointTracker030Position      = pointTracker030.getPosition()
		pointTracker031Position      = pointTracker031.getPosition()
		pointTracker032Position      = pointTracker032.getPosition()
		pointTracker033Position      = pointTracker033.getPosition()
		pointTracker034Position      = pointTracker034.getPosition()
		pointTracker035Position      = pointTracker035.getPosition()
		pointTracker036Position      = pointTracker036.getPosition()
		pointTracker037Position      = pointTracker037.getPosition()
		#06.09.
		pointTracker038Position      = pointTracker038.getPosition()

	except:
		#pointTracker000Position = myLink1.getPosition()
		pointTracker001Position = [-1.0, -1.0, -1.0]
		pointTracker002Position = [-1.0, -1.0, -1.0]
		pointTracker003Position = [-1.0, -1.0, -1.0]
		pointTracker004Position = [-1.0, -1.0, -1.0]
		pointTracker005Position = [-1.0, -1.0, -1.0]
		pointTracker006Position = [-1.0, -1.0, -1.0]
		pointTracker007Position = [-1.0, -1.0, -1.0]
		pointTracker008Position = [-1.0, -1.0, -1.0]
		pointTracker009Position = [-1.0, -1.0, -1.0]
		pointTracker010Position = [-1.0, -1.0, -1.0]
		pointTracker011Position = [-1.0, -1.0, -1.0]
		pointTracker012Position = [-1.0, -1.0, -1.0]
		pointTracker013Position = [-1.0, -1.0, -1.0]
		pointTracker014Position = [-1.0, -1.0, -1.0]
		pointTracker015Position = [-1.0, -1.0, -1.0]
		pointTracker016Position = [-1.0, -1.0, -1.0]
		pointTracker017Position = [-1.0, -1.0, -1.0]
		pointTracker018Position = [-1.0, -1.0, -1.0]
		pointTracker019Position = [-1.0, -1.0, -1.0]
		pointTracker020Position = [-1.0, -1.0, -1.0]
		pointTracker021Position = [-1.0, -1.0, -1.0]
		pointTracker022Position = [-1.0, -1.0, -1.0]
		pointTracker023Position = [-1.0, -1.0, -1.0]
		pointTracker024Position = [-1.0, -1.0, -1.0]
		pointTracker025Position = [-1.0, -1.0, -1.0]
		pointTracker026Position = [-1.0, -1.0, -1.0]
		pointTracker027Position = [-1.0, -1.0, -1.0]
		pointTracker028Position = [-1.0, -1.0, -1.0]
		pointTracker029Position = [-1.0, -1.0, -1.0]
		pointTracker030Position = [-1.0, -1.0, -1.0]
		pointTracker031Position = [-1.0, -1.0, -1.0]
		pointTracker032Position = [-1.0, -1.0, -1.0]
		pointTracker033Position = [-1.0, -1.0, -1.0]
		pointTracker034Position = [-1.0, -1.0, -1.0]
		pointTracker035Position = [-1.0, -1.0, -1.0]
		pointTracker036Position = [-1.0, -1.0, -1.0]
		pointTracker037Position = [-1.0, -1.0, -1.0]
		#06.09.
		pointTracker038Position = [-1.0, -1.0, -1.0]

	listenarray = [	pointTracker000Position[0], pointTracker000Position[1], pointTracker000Position[2],
					pointTracker001Position[0], pointTracker001Position[1], pointTracker001Position[2],
					pointTracker002Position[0], pointTracker002Position[1], pointTracker002Position[2],
					pointTracker003Position[0], pointTracker003Position[1], pointTracker003Position[2],
					pointTracker004Position[0], pointTracker004Position[1], pointTracker004Position[2],
					pointTracker005Position[0], pointTracker005Position[1], pointTracker005Position[2],
					pointTracker006Position[0], pointTracker006Position[1], pointTracker006Position[2],
					pointTracker007Position[0], pointTracker007Position[1], pointTracker007Position[2],
					pointTracker008Position[0], pointTracker008Position[1], pointTracker008Position[2],
					pointTracker009Position[0], pointTracker009Position[1], pointTracker009Position[2],
					pointTracker010Position[0], pointTracker010Position[1], pointTracker010Position[2],
					pointTracker011Position[0], pointTracker011Position[1], pointTracker011Position[2],
					pointTracker012Position[0], pointTracker012Position[1], pointTracker012Position[2],
					pointTracker013Position[0], pointTracker013Position[1], pointTracker013Position[2],
					pointTracker014Position[0], pointTracker014Position[1], pointTracker014Position[2],
					pointTracker015Position[0], pointTracker015Position[1], pointTracker015Position[2],
					pointTracker016Position[0], pointTracker016Position[1], pointTracker016Position[2],
					pointTracker017Position[0], pointTracker017Position[1], pointTracker017Position[2],
					pointTracker018Position[0], pointTracker018Position[1], pointTracker018Position[2],
					pointTracker019Position[0], pointTracker019Position[1], pointTracker019Position[2],
					pointTracker020Position[0], pointTracker020Position[1], pointTracker020Position[2],
					pointTracker021Position[0], pointTracker021Position[1], pointTracker021Position[2],
					pointTracker022Position[0], pointTracker022Position[1], pointTracker022Position[2],
					pointTracker023Position[0], pointTracker023Position[1], pointTracker023Position[2],
					pointTracker024Position[0], pointTracker024Position[1], pointTracker024Position[2],
					pointTracker025Position[0], pointTracker025Position[1], pointTracker025Position[2],
					pointTracker026Position[0], pointTracker026Position[1], pointTracker026Position[2],
					pointTracker027Position[0], pointTracker027Position[1], pointTracker027Position[2],
					pointTracker028Position[0], pointTracker028Position[1], pointTracker028Position[2],
					pointTracker029Position[0], pointTracker029Position[1], pointTracker029Position[2],
					pointTracker030Position[0], pointTracker030Position[1], pointTracker030Position[2],
					pointTracker031Position[0], pointTracker031Position[1], pointTracker031Position[2],
					pointTracker032Position[0], pointTracker032Position[1], pointTracker032Position[2],
					pointTracker033Position[0], pointTracker033Position[1], pointTracker033Position[2],
					pointTracker034Position[0], pointTracker034Position[1], pointTracker034Position[2],
					pointTracker035Position[0], pointTracker035Position[1], pointTracker035Position[2],
					pointTracker036Position[0], pointTracker036Position[1], pointTracker036Position[2],
					pointTracker037Position[0], pointTracker037Position[1], pointTracker037Position[2],
					#06.09.
					pointTracker038Position[0], pointTracker038Position[1], pointTracker038Position[2],
					time.time()]

	if (os.path.isfile(ORDNERPFAD + filename2)):
		with open("F:\\"+filename2,'ab+') as f_handle:
			for i in listenarray:
				s = pack('f',i)
				f_handle.write(s)
		f_handle.close()
	else:
		with open("F:\\"+filename2,'wb+') as f_handle:
			for i in listenarray:
				s = pack('f',i)
				f_handle.write(s)
		f_handle.close()

	if (os.path.isfile("F:\\" + filename3)):
		with open(filename3,'ab+') as f_handle:
			np.savetxt(f_handle, [[getEventstring(), str(time.time())]], newline='\r', delimiter = ';', fmt='%s')
		f_handle.close()
	else:
		listenheader2 = "Event; Zeit"

		with open("F:\\" + filename3, 'wb+') as f_handle:
			np.savetxt(f_handle, [[getEventstring(), str(time.time())]], newline='\r', header=listenheader2, delimiter = ';', fmt='%s')
		f_handle.close()

		del listenheader2

	setEventstring('')

def onTimer(num):
    print('Timer id',num,'expired')


#def onKeyDownStopInstructions(key):
#    if key == viz.KEY_UP:
#
#		print ('KeyUp was pressed')
#		setfirstRunInstruction(False)
#
#viz.callback(viz.KEYDOWN_EVENT,onKeyDownStopInstructions)
#
#def mykeyboard(whichkey):
#	if whichkey == viz.KEY_F1:
#		setFirstRunInstruction(False)
		
def showMoveInstruction():
	global InteractionAdded
	global moveInstruction
	global firstRunInstructionMovement
	global text4
		
	if InteractionAdded is 'InteractionAdded':
		text4.message('')
		fadeInOutMovementInstruction = vizact.sequence(vizact.fadeTo(1,time=1),vizact.waittime(20),vizact.fadeTo(0,time=1))
		moveInstruction = viz.addText3D('Achtung: Nun folgen mehrere Versuche, \n in denen sich der Ball, während du \n nach ihm greifst, nach links oder \n rechts wegbewegen wird. Dabei kann \n er über die Kante des Regals rollen \n und hinunterfallen, wenn du nicht \n schnell genug nach ihm greifst. \n Dies zählt dann als Fehlversuch.  ')
		moveInstruction.setPosition([0.06, 0, 0.1])
		moveInstruction.fontSize(1)
		moveInstruction.setCenter([0.0, 0.05, 0.3])
		moveInstruction.setScale([0.0175]*3)
		moveInstruction.alignment(viz.ALIGN_CENTER_TOP)
		
		
		moveInstruction.setParent(VIEWBALL)
		moveInstruction.setPosition(moveInstruction.getCenter())
		
		moveInstruction.add(fadeInOutMovementInstruction)
		
		setFirstRunInstructionMovement(False)
		
		
	

#try to implement instructions 03.09.
def showInstructions():
	#global isGrabbed
	#global isReleased
	global startpointpassed
	global instruction_text1
	global text2
	global text3
	global text4
	global firstRunInstruction
	
	if startpointpassed is '':
		instruction_text1 = viz.addText3D('Tritt bitte vor das blaue Regal,\n und stelle dich auf die in den \n Boden gezeichneten Fußabdrücke. \n Halte den Controller dann in \n die runde Startkugel rechts vor dir')
		instruction_text1.setPosition([0.06, 0, 0.1])
		instruction_text1.fontSize(1)
		instruction_text1.setCenter([0.0, 0.05, 0.3])
		instruction_text1.setScale([0.0175]*3)
		instruction_text1.alignment(viz.ALIGN_CENTER_TOP)
		
		
		instruction_text1.setParent(VIEWBALL)
		instruction_text1.setPosition(instruction_text1.getCenter())
	else: 
		if startpointpassed is 'startpointpassed': # isGrabbed==False and isReleased==True:
			
			#del instruction_text1 
			instruction_text1.message('')
			
			text2 = viz.addText3D('Bewege den Controller nun in \n Richtung des Balls auf dem Regal \n vor dir und greife diesen, \n indem du den Knopf an der \n Unterseite des Controllers drückst \n und anschließend gedrückt hältst')
			text2.fontSize(1)
			text2.setCenter([0.0, 0.05, 0.3])
			text2.setScale([0.0175]*3)
			text2.alignment(viz.ALIGN_CENTER_TOP)
			
			text2.setParent(VIEWBALL)
			text2.setPosition(text2.getCenter())
		else:
			pass
		
	
	if startpointpassed is 'isGrabbed':
		text2.message('')
		
		text3 = viz.addText3D('Halte den Knopf gedrückt, \n bis du den Ball werfen willst. \n Du wirfst den Ball, \n indem du den Knopf loslässt. \n Versuche den Ball in das \n kreisförmige Ziel zu treffen, \n welches sich vor dir befindet')
		text3.fontSize(1)
		text3.setCenter([0.0, 0.05, 0.3])
		text3.setScale([0.0175]*3)
		text3.alignment(viz.ALIGN_CENTER_TOP)
		
		text3.setParent(VIEWBALL)
		text3.setPosition(text3.getCenter())
		
	if startpointpassed is 'isReleased': 
		text3.message('')
		fadeInOut = vizact.sequence(vizact.fadeTo(1,time=1),vizact.waittime(2),vizact.fadeTo(0,time=1))
		text4 = viz.addText3D('Prima! Es folgen nun zwei \n Trainingsblöcke, in denen du üben kannst.')
		text4.fontSize(1)
		text4.setCenter([0.0, 0.05, 0.3])
		text4.setScale([0.0175]*3)
		text4.alignment(viz.ALIGN_CENTER_TOP)
		
		text4.setParent(VIEWBALL)
		text4.setPosition(text4.getCenter())
		text4.add(fadeInOut)
		
#	if startpointpassed is 'BallMovement': 
#		text4.message('')
#		#fadeInOut = vizact.sequence(vizact.fadeTo(1,time=1),vizact.waittime(2),vizact.fadeTo(0,time=1))
#		text5 = viz.addText3D('Achtung: Nun folgen mehrere Versuche, \n in denen sich der Ball, \n während du nach ihm greifst, \n nach links oder rechts wegbewegen wird. \n Dabei kann er über die Kante des Regals rollen \n und hinunterfallen, wenn du nicht \n schnell genug nach ihm greifst. \n Dies zählt dann als Fehlversuch.  ')
#		text5.fontSize(1)
#		text5.setCenter([0.0, 0.8, 3.0])
#		text5.setScale([0.125]*3)
#		text5.alignment(viz.ALIGN_CENTER_TOP)
#		
#		text5.setParent(VIEWBALL)
#		text5.setPosition(text5.getCenter())
		#text5.add(fadeInOut)

#		yield viztask.waitKeyDown('g')
#		#viz.callback(viz.KEYDOWN_EVENT,onKeyDown)
#		#vizact.onkeydown('g',text4.remove)
		
		setFirstRunInstruction(False)

		
	#yield viztask.waitKeyDown('g')
		#viz.callback(viz.KEYDOWN_EVENT,onKeyDown)
		#vizact.onkeydown('g',text4.remove)
		#setFirstRunInstruction(False)
#viz.callback(viz.KEYDOWN_EVENT, mykeyboard)

##
# This method writes the log-file.
# It creates a \c filename of the variables \ref int_i and \ref vpn_id<a></a>:\n
# <code>filename = getVPNid()+"_"+str(getBlock())+"_log.csv"</code>\n\n
# If the does file not exists, it creates one with following columnnames:
# "VPN; Block; Trial; TrialType; Zeitdruck; TrailDuration; Zielregal; 
# Distance(Ball_center, Perfect_Position); Viapoint passed;
# Intersection(Ball,Placement); Success; Event; Zeit; Sensorgroesse; 
# Ball_x; Ball_y; Ball_z; Ball_yaw; Ball_pitch; Ball_roll; Ball_P1_x; 
# Ball_P1_y; Ball_P1_z; Ball_P2_x; Ball_P2_y; Ball_P2_z; Ball_P3_x; 
# Ball_P3_y; Ball_P3_z; Ball_P4_x; Ball_P4_y; Ball_P4_z; Ball_P5_x; 
# Ball_P5_y; Ball_P5_z; Ball_P6_x; Ball_P6_y; Ball_P6_z; Ball_P7_x; 
# Ball_P7_y; Ball_P7_z; Ball_P8_x; Ball_P8_y; Ball_P8_z; Ballsize; 
# Placement_x; Placement_y; Placement_z; Distance(Ball_center,Placement_center); 
# Perfect_Position_x; Perfect_Position_y; Perfect_Position_z; Viewpoint_x; 
# Viewpoint_y; Viewpoint_z; Viewpoint_yaw; Viewpoint_pitch; Viewpoint_roll; 
# Lefthand_x; Lefthand_y; Lefthand_z; Lefthand_yaw; Lefthand_pitch; 
# Lefthand_roll; Righthand_x; Righthand_y; Righthand_z; Righthand_yaw; 
# Righthand_pitch; Righthand_roll; Head_x; Head_y; Head_z; Head_yaw; 
# Head_pitch; Head_roll".
# It also reads out the positions of placement and ball and calculates the distance between them.
# \param eventstring: string, which will be put in column 'Event'
# \see ORDNERPFAD, placement, ball, varTrialID, int_i, vpn_id, viapointpassed, 
# varPlacementBallIntersection, myLink1, myLink2, rTracker, varTrailDuration
def writeCSVfile(eventstring):
	global ORDNERPFAD
	global varTrialID
	global ball
	global viapointpassed
	global rTracker
	global varTrailDuration
	global overTheEdge
	global pointTracker000
	global pointTracker001
	global pointTracker002
	global pointTracker003
	global pointTracker004
	global pointTracker005
	global pointTracker006
	global pointTracker007
	global pointTracker008
	global pointTracker009
	global pointTracker010
	global pointTracker011
	global pointTracker012
	global pointTracker013
	global pointTracker014
	global pointTracker015
	global pointTracker016
	global pointTracker017
	global pointTracker018
	global pointTracker019
	global pointTracker020
	global pointTracker021
	global pointTracker022
	global pointTracker023
	global pointTracker024
	global pointTracker025
	global pointTracker026
	global pointTracker027
	global pointTracker028
	global pointTracker029
	global pointTracker030
	global pointTracker031
	global pointTracker032
	global pointTracker033
	global pointTracker034
	global pointTracker035
	global pointTracker036
	global pointTracker037
	global tracker
	global linkable1
	global linkable2
	global linkable3
	global linkable4
	global linkable5
	global linkable6
	global linkable7
	global linkable8
	global linkable9
	global linkable10
	global linkable11
	global linkable12
	global linkable13
	global linkable14
	global linkable15
	global linkable16
	global linkable17
	global linkable18
	global linkable19
	global linkable20
	global linkable21
	global linkable22
	global linkable23
	global linkable24
	global linkable25
	global linkable26
	global linkable27
	global linkable28
	global linkable29
	global linkable30
	global linkable31
	global linkable32
	global linkable33
	global linkable34
	global linkable35
	global linkable36
	global linkable37
	global linkable38
	global linkable39

	
	try:
		pointTracker000Position      = pointTracker000.getPosition()
		pointTracker001Position      = pointTracker001.getPosition()
		pointTracker002Position      = pointTracker002.getPosition()
		pointTracker003Position      = pointTracker003.getPosition()
		pointTracker004Position      = pointTracker004.getPosition()
		pointTracker005Position      = pointTracker005.getPosition()
		pointTracker006Position      = pointTracker006.getPosition()
		pointTracker007Position      = pointTracker007.getPosition()
		pointTracker008Position      = pointTracker008.getPosition()
		pointTracker009Position      = pointTracker009.getPosition()
		pointTracker010Position      = pointTracker010.getPosition()
		pointTracker011Position      = pointTracker011.getPosition()
		pointTracker012Position      = pointTracker012.getPosition()
		pointTracker013Position      = pointTracker013.getPosition()
		pointTracker014Position      = pointTracker014.getPosition()
		pointTracker015Position      = pointTracker015.getPosition()
		pointTracker016Position      = pointTracker016.getPosition()
		pointTracker017Position      = pointTracker017.getPosition()
		pointTracker018Position      = pointTracker018.getPosition()
		pointTracker019Position      = pointTracker019.getPosition()
		pointTracker020Position      = pointTracker020.getPosition()
		pointTracker021Position      = pointTracker021.getPosition()
		pointTracker022Position      = pointTracker022.getPosition()
		pointTracker023Position      = pointTracker023.getPosition()
		pointTracker024Position      = pointTracker024.getPosition()
		pointTracker025Position      = pointTracker025.getPosition()
		pointTracker026Position      = pointTracker026.getPosition()
		pointTracker027Position      = pointTracker027.getPosition()
		pointTracker028Position      = pointTracker028.getPosition()
		pointTracker029Position      = pointTracker029.getPosition()
		pointTracker030Position      = pointTracker030.getPosition()
		pointTracker031Position      = pointTracker031.getPosition()
		pointTracker032Position      = pointTracker032.getPosition()
		pointTracker033Position      = pointTracker033.getPosition()
		pointTracker034Position      = pointTracker034.getPosition()
		pointTracker035Position      = pointTracker035.getPosition()
		pointTracker036Position      = pointTracker036.getPosition()
		pointTracker037Position      = pointTracker037.getPosition()
		#06.09.
		pointTracker038Position      = tracker.getPosition()
		
	except:
		pointTracker000Position = [-1.0, -1.0, -1.0]
		#test 26.11.20
		#pointTracker000Position = pointTracker006.getPosition()
		pointTracker001Position = [-1.0, -1.0, -1.0]
		pointTracker002Position = [-1.0, -1.0, -1.0]
		pointTracker003Position = [-1.0, -1.0, -1.0]
		pointTracker004Position = [-1.0, -1.0, -1.0]
		pointTracker005Position = [-1.0, -1.0, -1.0]
		pointTracker006Position = [-1.0, -1.0, -1.0]
		pointTracker007Position = [-1.0, -1.0, -1.0]
		pointTracker008Position = [-1.0, -1.0, -1.0]
		pointTracker009Position = [-1.0, -1.0, -1.0]
		pointTracker010Position = [-1.0, -1.0, -1.0]
		pointTracker011Position = [-1.0, -1.0, -1.0]
		pointTracker012Position = [-1.0, -1.0, -1.0]
		pointTracker013Position = [-1.0, -1.0, -1.0]
		pointTracker014Position = [-1.0, -1.0, -1.0]
		pointTracker015Position = [-1.0, -1.0, -1.0]
		pointTracker016Position = [-1.0, -1.0, -1.0]
		pointTracker017Position = [-1.0, -1.0, -1.0]
		pointTracker018Position = [-1.0, -1.0, -1.0]
		pointTracker019Position = [-1.0, -1.0, -1.0]
		pointTracker020Position = [-1.0, -1.0, -1.0]
		pointTracker021Position = [-1.0, -1.0, -1.0]
		pointTracker022Position = [-1.0, -1.0, -1.0]
		pointTracker023Position = [-1.0, -1.0, -1.0]
		pointTracker024Position = [-1.0, -1.0, -1.0]
		pointTracker025Position = [-1.0, -1.0, -1.0]
		pointTracker026Position = [-1.0, -1.0, -1.0]
		pointTracker027Position = [-1.0, -1.0, -1.0]
		pointTracker028Position = [-1.0, -1.0, -1.0]
		pointTracker029Position = [-1.0, -1.0, -1.0]
		pointTracker030Position = [-1.0, -1.0, -1.0]
		pointTracker031Position = [-1.0, -1.0, -1.0]
		pointTracker032Position = [-1.0, -1.0, -1.0]
		pointTracker033Position = [-1.0, -1.0, -1.0]
		pointTracker034Position = [-1.0, -1.0, -1.0]
		pointTracker035Position = [-1.0, -1.0, -1.0]
		pointTracker036Position = [-1.0, -1.0, -1.0]
		pointTracker037Position = [-1.0, -1.0, -1.0]
		#06.09.
		pointTracker038Position = [-1.0, -1.0, -1.0]

	try:
		linkable1Position      = linkable1.getPosition()
		linkable2Position      = linkable2.getPosition()
		linkable3Position      = linkable3.getPosition()
		linkable4Position      = linkable4.getPosition()
		linkable5Position      = linkable5.getPosition()
		linkable6Position      = linkable6.getPosition()
		linkable7Position      = linkable7.getPosition()
		linkable8Position      = linkable8.getPosition()
		linkable9Position      = linkable9.getPosition()
		linkable10Position      = linkable10.getPosition()
		linkable11Position      = linkable11.getPosition()
		linkable12Position      = linkable12.getPosition()
		linkable13Position      = linkable13.getPosition()
		linkable14Position      = linkable14.getPosition()
		linkable15Position      = linkable15.getPosition()
		linkable16Position      = linkable16.getPosition()
		linkable17Position      = linkable17.getPosition()
		linkable18Position      = linkable18.getPosition()
		linkable19Position      = linkable19.getPosition()
		linkable20Position      = linkable20.getPosition()
		linkable21Position      = linkable21.getPosition()
		linkable22Position      = linkable22.getPosition()
		linkable23Position      = linkable23.getPosition()
		linkable24Position      = linkable24.getPosition()
		linkable25Position      = linkable25.getPosition()
		linkable26Position      = linkable26.getPosition()
		linkable27Position      = linkable27.getPosition()
		linkable28Position      = linkable28.getPosition()
		linkable29Position      = linkable29.getPosition()
		linkable30Position      = linkable30.getPosition()
		linkable31Position      = linkable31.getPosition()
		linkable32Position      = linkable32.getPosition()
		linkable33Position      = linkable33.getPosition()
		linkable34Position      = linkable34.getPosition()
		linkable35Position      = linkable35.getPosition()
		linkable36Position      = linkable36.getPosition()
		linkable37Position      = linkable37.getPosition()
		#06.09.
		linkable38Position      = linkable38.getPosition()
		linkable39Position      = linkable39.getPosition()
		
	except:
		linkable0Position = [-1.0, -1.0, -1.0]
		#test 26.11.20
		#linkable0Position = linkable6.getPosition()
		linkable1Position = [-1.0, -1.0, -1.0]
		linkable2Position = [-1.0, -1.0, -1.0]
		linkable3Position = [-1.0, -1.0, -1.0]
		linkable4Position = [-1.0, -1.0, -1.0]
		linkable5Position = [-1.0, -1.0, -1.0]
		linkable6Position = [-1.0, -1.0, -1.0]
		linkable7Position = [-1.0, -1.0, -1.0]
		linkable8Position = [-1.0, -1.0, -1.0]
		linkable9Position = [-1.0, -1.0, -1.0]
		linkable10Position = [-1.0, -1.0, -1.0]
		linkable11Position = [-1.0, -1.0, -1.0]
		linkable12Position = [-1.0, -1.0, -1.0]
		linkable13Position = [-1.0, -1.0, -1.0]
		linkable14Position = [-1.0, -1.0, -1.0]
		linkable15Position = [-1.0, -1.0, -1.0]
		linkable16Position = [-1.0, -1.0, -1.0]
		linkable17Position = [-1.0, -1.0, -1.0]
		linkable18Position = [-1.0, -1.0, -1.0]
		linkable19Position = [-1.0, -1.0, -1.0]
		linkable20Position = [-1.0, -1.0, -1.0]
		linkable21Position = [-1.0, -1.0, -1.0]
		linkable22Position = [-1.0, -1.0, -1.0]
		linkable23Position = [-1.0, -1.0, -1.0]
		linkable24Position = [-1.0, -1.0, -1.0]
		linkable25Position = [-1.0, -1.0, -1.0]
		linkable26Position = [-1.0, -1.0, -1.0]
		linkable27Position = [-1.0, -1.0, -1.0]
		linkable28Position = [-1.0, -1.0, -1.0]
		linkable29Position = [-1.0, -1.0, -1.0]
		linkable30Position = [-1.0, -1.0, -1.0]
		linkable31Position = [-1.0, -1.0, -1.0]
		linkable32Position = [-1.0, -1.0, -1.0]
		linkable33Position = [-1.0, -1.0, -1.0]
		linkable34Position = [-1.0, -1.0, -1.0]
		linkable35Position = [-1.0, -1.0, -1.0]
		linkable36Position = [-1.0, -1.0, -1.0]
		linkable37Position = [-1.0, -1.0, -1.0]
		#06.09.
		linkable38Position = [-1.0, -1.0, -1.0]
		linkable39Position = [-1.0, -1.0, -1.0]

	temp_view_pos = viz.MainView.getPosition()
	temp_view_euler = viz.MainView.getEuler()
	filename = getVPNid()+"_"+str(getBlock())+"_log.csv"

	try:
		ballposition = ball.getBallPosition()
		balleuler = ball.getBallEuler()
		#ballsize = ball.getBallSize()
	except:
		ballposition = [-1.0, -1.0, -1.0]
		balleuler = [-1.0, -1.0, -1.0]
		distance = -1.0
		#ballsize = -1.0
		perfectpos = [-1.0, -1.0, -1.0]
		
		
	try:
		controllerPos = controllersteam.getPosition()
		controllerEuler = controllersteam.getEuler()
	except:
		controllerPos = [-1.0, -1.0, -1.0]
		controllerEuler = [-1.0, -1.0, -1.0]


	try:
		headTrackerPos = headTracker.getPosition()
		headTrackerEuler = headTracker.getEuler()
	except:
		headTrackerPos = [-1.0, -1.0, -1.0]
		headTrackerEuler = [-1.0, -1.0, -1.0]

	try:
		distance2 = vizmat.Distance(ballposition,perfectpos)
		cp = ball.getCornerPoints()
		if notinthevrlab:
			pos_link1   = myLink1.getPosition()
			pos_link2   = [-1.0, -1.0, -1.0]
			euler_link1 = myLink1.getEuler()
			euler_link2 = [-1.0, -1.0, -1.0]
		else:
			pos_link1   = myLink1.getPosition()
			euler_link1 = myLink1.getEuler()
			pos_link2   = myLink2.getPosition()
			euler_link2 = myLink2.getEuler()
	except:
		distance2 = -1.0
		cp = [[-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, -1.0]]
		pos_link1   = [-1.0, -1.0, -1.0]
		pos_link2   = [-1.0, -1.0, -1.0]
		euler_link1 = [-1.0, -1.0, -1.0]
		euler_link2 = [-1.0, -1.0, -1.0]

	listenarray = [[getVPNid(), getBlock(), varTrialID, getTrialType(), #getShowTime(), mF2Sac(varTrailDuration), #getPlacementDestination(),
#					mF2Sac(distance2),
					viapointpassed, overTheEdge,
#					(viapointpassed), #and varPlacementBallIntersection),#(viapointpassed and vartorusBallIntersection),
					eventstring,
					str(time.time()), mF2Sac(getSensorSize()),
					mF2Sac(ballposition[0]), mF2Sac(ballposition[1]), mF2Sac(ballposition[2]), mF2Sac(balleuler[0]), mF2Sac(balleuler[1]), mF2Sac(balleuler[2]),
#					mF2Sac(cp[0][0]), mF2Sac(cp[0][1]), mF2Sac(cp[0][2]),
#					mF2Sac(cp[1][0]), mF2Sac(cp[1][1]), mF2Sac(cp[1][2]),
#					mF2Sac(cp[2][0]), mF2Sac(cp[2][1]), mF2Sac(cp[2][2]),
#					mF2Sac(cp[3][0]), mF2Sac(cp[3][1]), mF2Sac(cp[3][2]),
#					mF2Sac(cp[4][0]), mF2Sac(cp[4][1]), mF2Sac(cp[4][2]),
#					mF2Sac(cp[5][0]), mF2Sac(cp[5][1]), mF2Sac(cp[5][2]),
#					mF2Sac(cp[6][0]), mF2Sac(cp[6][1]), mF2Sac(cp[6][2]),
#					mF2Sac(cp[7][0]), mF2Sac(cp[7][1]), mF2Sac(cp[7][2]),
					mF2Sac(headTrackerPos[0]), mF2Sac(headTrackerPos[1]), mF2Sac(headTrackerPos[2]),
					mF2Sac(headTrackerEuler[0]), mF2Sac(headTrackerEuler[1]), mF2Sac(headTrackerEuler[2]),
					mF2Sac(controllerPos[0]), mF2Sac(controllerPos[1]), mF2Sac(controllerPos[2]),
					mF2Sac(controllerEuler[0]), mF2Sac(controllerEuler[1]), mF2Sac(controllerEuler[2]),
					pointTracker000Position[0], pointTracker000Position[1], pointTracker000Position[2],
					pointTracker001Position[0], pointTracker001Position[1], pointTracker001Position[2],
					pointTracker002Position[0], pointTracker002Position[1], pointTracker002Position[2],
					pointTracker003Position[0], pointTracker003Position[1], pointTracker003Position[2],
					pointTracker004Position[0], pointTracker004Position[1], pointTracker004Position[2],
					pointTracker005Position[0], pointTracker005Position[1], pointTracker005Position[2],
					pointTracker006Position[0], pointTracker006Position[1], pointTracker006Position[2],
					pointTracker007Position[0], pointTracker007Position[1], pointTracker007Position[2],
					pointTracker008Position[0], pointTracker008Position[1], pointTracker008Position[2],
					pointTracker009Position[0], pointTracker009Position[1], pointTracker009Position[2],
					pointTracker010Position[0], pointTracker010Position[1], pointTracker010Position[2],
					pointTracker011Position[0], pointTracker011Position[1], pointTracker011Position[2],
					pointTracker012Position[0], pointTracker012Position[1], pointTracker012Position[2],
					pointTracker013Position[0], pointTracker013Position[1], pointTracker013Position[2],
					pointTracker014Position[0], pointTracker014Position[1], pointTracker014Position[2],
					pointTracker015Position[0], pointTracker015Position[1], pointTracker015Position[2],
					pointTracker016Position[0], pointTracker016Position[1], pointTracker016Position[2],
					pointTracker017Position[0], pointTracker017Position[1], pointTracker017Position[2],
					pointTracker018Position[0], pointTracker018Position[1], pointTracker018Position[2],
					pointTracker019Position[0], pointTracker019Position[1], pointTracker019Position[2],
					pointTracker020Position[0], pointTracker020Position[1], pointTracker020Position[2],
					pointTracker021Position[0], pointTracker021Position[1], pointTracker021Position[2],
					pointTracker022Position[0], pointTracker022Position[1], pointTracker022Position[2],
					pointTracker023Position[0], pointTracker023Position[1], pointTracker023Position[2],
					pointTracker024Position[0], pointTracker024Position[1], pointTracker024Position[2],
					pointTracker025Position[0], pointTracker025Position[1], pointTracker025Position[2],
					pointTracker026Position[0], pointTracker026Position[1], pointTracker026Position[2],
					pointTracker027Position[0], pointTracker027Position[1], pointTracker027Position[2],
					pointTracker028Position[0], pointTracker028Position[1], pointTracker028Position[2],
					pointTracker029Position[0], pointTracker029Position[1], pointTracker029Position[2],
					pointTracker030Position[0], pointTracker030Position[1], pointTracker030Position[2],
					pointTracker031Position[0], pointTracker031Position[1], pointTracker031Position[2],
					pointTracker032Position[0], pointTracker032Position[1], pointTracker032Position[2],
					pointTracker033Position[0], pointTracker033Position[1], pointTracker033Position[2],
					pointTracker034Position[0], pointTracker034Position[1], pointTracker034Position[2],
					pointTracker035Position[0], pointTracker035Position[1], pointTracker035Position[2],
					pointTracker036Position[0], pointTracker036Position[1], pointTracker036Position[2],
					pointTracker037Position[0], pointTracker037Position[1], pointTracker037Position[2],
					#06.09.
					pointTracker038Position[0], pointTracker038Position[1], pointTracker038Position[2],
					linkable1Position[0], linkable1Position[1], linkable1Position[2],
					linkable2Position[0], linkable2Position[1], linkable2Position[2],
					linkable3Position[0], linkable3Position[1], linkable3Position[2],
					linkable4Position[0], linkable4Position[1], linkable4Position[2],
					linkable5Position[0], linkable5Position[1], linkable5Position[2],
					linkable6Position[0], linkable6Position[1], linkable6Position[2],
					linkable7Position[0], linkable7Position[1], linkable7Position[2],
					linkable8Position[0], linkable8Position[1], linkable8Position[2],
					linkable9Position[0], linkable9Position[1], linkable9Position[2],
					linkable10Position[0], linkable10Position[1], linkable10Position[2],
					linkable11Position[0], linkable11Position[1], linkable11Position[2],
					linkable12Position[0], linkable12Position[1], linkable12Position[2],
					linkable13Position[0], linkable13Position[1], linkable13Position[2],
					linkable14Position[0], linkable14Position[1], linkable14Position[2],
					linkable15Position[0], linkable15Position[1], linkable15Position[2],
					linkable16Position[0], linkable16Position[1], linkable16Position[2],
					linkable17Position[0], linkable17Position[1], linkable17Position[2],
					linkable18Position[0], linkable18Position[1], linkable18Position[2],
					linkable19Position[0], linkable19Position[1], linkable19Position[2],
					linkable20Position[0], linkable20Position[1], linkable20Position[2],
					linkable21Position[0], linkable21Position[1], linkable21Position[2],
					linkable22Position[0], linkable22Position[1], linkable22Position[2],
					linkable23Position[0], linkable23Position[1], linkable23Position[2],
					linkable24Position[0], linkable24Position[1], linkable24Position[2],
					linkable25Position[0], linkable25Position[1], linkable25Position[2],
					linkable26Position[0], linkable26Position[1], linkable26Position[2],
					linkable27Position[0], linkable27Position[1], linkable27Position[2],
					linkable28Position[0], linkable28Position[1], linkable28Position[2],
					linkable29Position[0], linkable29Position[1], linkable29Position[2],
					linkable30Position[0], linkable30Position[1], linkable30Position[2],
					linkable31Position[0], linkable31Position[1], linkable31Position[2],
					linkable32Position[0], linkable32Position[1], linkable32Position[2],
					linkable33Position[0], linkable33Position[1], linkable33Position[2],
					linkable34Position[0], linkable34Position[1], linkable34Position[2],
					linkable35Position[0], linkable35Position[1], linkable35Position[2],
					linkable36Position[0], linkable36Position[1], linkable36Position[2],
					linkable37Position[0], linkable37Position[1], linkable37Position[2],
					#06.09.
					linkable38Position[0], linkable38Position[1], linkable38Position[2],
                    linkable39Position[0], linkable39Position[1], linkable39Position[2]]]

	if (os.path.isfile(ORDNERPFAD + filename)):
		with open(filename,'a') as f_handle:
			np.savetxt(f_handle, listenarray, newline='\r', delimiter = ';', fmt='%s')
		f_handle.close()
	else:
		listenheader = "VPN; Block; Trial; TrialType;\
		Success;\
		Over_edge;\
		Event;\
		Zeit; Sensorgroesse; \
		Ball_x; Ball_y; Ball_z; Ball_yaw; Ball_pitch; Ball_roll; \
		Head_x; Head_y; Head_z; \
		Head_yaw; Head_pitch; Head_roll; \
		Controller_x; Controller_y; Controller_z; \
		Controller_yaw; Controller_pitch; Controller_roll; \
		pointTracker000_x; pointTracker000_y; pointTracker000_z; \
		pointTracker001_x; pointTracker001_y; pointTracker001_z; \
		pointTracker002_x; pointTracker002_y; pointTracker002_z; \
		pointTracker003_x; pointTracker003_y; pointTracker003_z; \
		pointTracker004_x; pointTracker004_y; pointTracker004_z; \
		pointTracker005_x; pointTracker005_y; pointTracker005_z; \
		pointTracker006_x; pointTracker006_y; pointTracker006_z; \
		pointTracker007_x; pointTracker007_y; pointTracker007_z; \
		pointTracker008_x; pointTracker008_y; pointTracker008_z; \
		pointTracker009_x; pointTracker009_y; pointTracker009_z; \
		pointTracker010_x; pointTracker010_y; pointTracker010_z; \
		pointTracker011_x; pointTracker011_y; pointTracker011_z; \
		pointTracker012_x; pointTracker012_y; pointTracker012_z; \
		pointTracker013_x; pointTracker013_y; pointTracker013_z; \
		pointTracker014_x; pointTracker014_y; pointTracker014_z; \
		pointTracker015_x; pointTracker015_y; pointTracker015_z; \
		pointTracker016_x; pointTracker016_y; pointTracker016_z; \
		pointTracker017_x; pointTracker017_y; pointTracker017_z; \
		pointTracker018_x; pointTracker018_y; pointTracker018_z; \
		pointTracker019_x; pointTracker019_y; pointTracker019_z; \
		pointTracker020_x; pointTracker020_y; pointTracker020_z; \
		pointTracker021_x; pointTracker021_y; pointTracker021_z; \
		pointTracker022_x; pointTracker022_y; pointTracker022_z; \
		pointTracker023_x; pointTracker023_y; pointTracker023_z; \
		pointTracker024_x; pointTracker024_y; pointTracker024_z; \
		pointTracker025_x; pointTracker025_y; pointTracker025_z; \
		pointTracker026_x; pointTracker026_y; pointTracker026_z; \
		pointTracker027_x; pointTracker027_y; pointTracker027_z; \
		pointTracker028_x; pointTracker028_y; pointTracker028_z; \
		pointTracker029_x; pointTracker029_y; pointTracker029_z; \
		pointTracker030_x; pointTracker030_y; pointTracker030_z; \
		pointTracker031_x; pointTracker031_y; pointTracker031_z; \
		pointTracker032_x; pointTracker032_y; pointTracker032_z; \
		pointTracker033_x; pointTracker033_y; pointTracker033_z; \
		pointTracker034_x; pointTracker034_y; pointTracker034_z; \
		pointTracker035_x; pointTracker035_y; pointTracker035_z; \
		pointTracker036_x; pointTracker036_y; pointTracker036_z; \
		pointTracker037_x; pointTracker037_y; pointTracker037_z; \
		pointTracker038_x; pointTracker038_y; pointTracker038_z; \
		linkable1_x; linkable1_y; linkable1_z; \
		linkable2_x; linkable2_y; linkable2_z; \
		linkable3_x; linkable3_y; linkable3_z; \
		linkable4_x; linkable4_y; linkable4_z; \
		linkable5_x; linkable5_y; linkable5_z; \
		linkable6_x; linkable6_y; linkable6_z; \
		linkable7_x; linkable7_y; linkable7_z; \
		linkable8_x; linkable8_y; linkable8_z; \
		linkable9_x; linkable9_y; linkable9_z; \
		linkable10_x; linkable10_y; linkable10_z; \
		linkable11_x; linkable11_y; linkable11_z; \
		linkable12_x; linkable12_y; linkable12_z; \
		linkable13_x; linkable13_y; linkable13_z; \
		linkable14_x; linkable14_y; linkable14_z; \
		linkable15_x; linkable15_y; linkable15_z; \
		linkable16_x; linkable16_y; linkable16_z; \
		linkable17_x; linkable17_y; linkable17_z; \
		linkable18_x; linkable18_y; linkable18_z; \
		linkable19_x; linkable19_y; linkable19_z; \
		linkable20_x; linkable20_y; linkable20_z; \
		linkable21_x; linkable21_y; linkable21_z; \
		linkable22_x; linkable22_y; linkable22_z; \
		linkable23_x; linkable23_y; linkable23_z; \
		linkable24_x; linkable24_y; linkable24_z; \
		linkable25_x; linkable25_y; linkable25_z; \
		linkable26_x; linkable26_y; linkable26_z; \
		linkable27_x; linkable27_y; linkable27_z; \
		linkable28_x; linkable28_y; linkable28_z; \
		linkable29_x; linkable29_y; linkable29_z; \
		linkable30_x; linkable30_y; linkable30_z; \
		linkable31_x; linkable31_y; linkable31_z; \
		linkable32_x; linkable32_y; linkable32_z; \
		linkable33_x; linkable33_y; linkable33_z; \
		linkable34_x; linkable34_y; linkable34_z; \
		linkable35_x; linkable35_y; linkable35_z; \
		linkable36_x; linkable36_y; linkable36_z; \
		linkable37_x; linkable37_y; linkable37_z; \
		linkable38_x; linkable38_y; linkable38_z; \
		linkable39_x; linkable39_y; linkable39_z"

		with open(filename,'a') as f_handle:
			np.savetxt(f_handle, listenarray, newline='\r', header=listenheader, delimiter = ';', fmt='%s')
		f_handle.close()

		del listenheader

	del filename
	del ballposition
	del temp_view_pos
	del temp_view_euler
	del listenarray
	del cp
	del headTrackerPos
	del headTrackerEuler
	del	controllerPos
	del	controllerEuler
	del euler_link1
	del euler_link2
	del pos_link1
	del pos_link2
#	del ballsize

##
# Makes a red rectangle on floor.
# \param rlength: float, which defines the length of the rectangle. The default value of variable is \ref varLength.
# \param rwidth: float, which defines the width of the rectangle. The default value of variable is \ref varWidth
# \see varLength, varWidth
# \see init
def makeARect(rlength = varLength, rwidth = varWidth):
	#Falls immer noch nicht dick genug durch planes ersetzen
	viz.startLayer(viz.LINE_STRIP, "Raumrand1")
	fl = rlength/2.0
	fw = rwidth/2.0
	viz.vertexColor([1.0, 0.0, 0.0])
	viz.vertex([-fl, 0.0, -fw])
	viz.vertex([-fl, 0.0,  fw])
	viz.vertex([ fl, 0.0,  fw])
	viz.vertex([ fl, 0.0, -fw])
	viz.vertex([-fl, 0.0, -fw])
	rect = viz.endLayer()
	rect.setPosition([0,0,0])

	viz.startLayer(viz.LINE_STRIP, "Raumrand2")
	fl = rlength/2.0+0.0005
	fw = rwidth/2.0+0.0005
	viz.vertexColor([1.0, 0.0, 0.0])
	viz.vertex([-fl, 0.0, -fw])
	viz.vertex([-fl, 0.0,  fw])
	viz.vertex([ fl, 0.0,  fw])
	viz.vertex([ fl, 0.0, -fw])
	viz.vertex([-fl, 0.0, -fw])
	rect2 = viz.endLayer()
	rect2.setPosition([0.0,0.0,0.0])

##
# This function returns \c True if the number of seconds of the actual time
# is even. Otherwise it returns \c False. So there is a fifty-fifty chance to get
# the boolean value \c True returned.
# \returns a boolean
def getFiftyFifty():
	myTime = time.localtime(time.time())
	print "getFiftyFifty: " + str(myTime[5])
	if (myTime[5]%2 == 0):
		del myTime
		return True
	else:
		del myTime
		return False

##
# Adds a <b>sensor</b> to the manager and defines the <b>function</b>, which is to call
# when <b>sensor</b> triggers an event.\n
# The parameter <b>varint</b> tells the method to whom of the manager it has to add the <b>sensor</b>.
# <b>varint</b> can has the value 1,2 or 4 where:
# \li 1 is for \ref manager
# \li 2 is for \ref manager2
# \li 4 is for \ref manager4
# \li 5 is for \ref manager5
# \n
# \param varint: an interger, which says what manager is to use
# \param sensor: sensor generated with the object before and now will be added to the manager
# \param sensorname: name of sensor; a string defined by your own
# \param function: function defined in this code (mySchedule.py), that will be executed when the sensor triggers
# \param destination: destination object of the object, which was generated before; default \c None
# \see manager, manager2, manager4
# \see EnterProximity, ExitProximity, moveThePlacement, grabEvent, playSound, sendMyCustomEvent
def addSensorToManager(varint, sensor, sensorname, function, destination=None):
	global manager
	global manager4

	temp_manager = None

	if (varint==1):
		temp_manager = manager
	elif (varint==2):
		temp_manager = manager2
	elif (varint==4):
		temp_manager = manager4
	else:
		assert(varint in [1,2,4,5]), "This manager does not exist. varint can has the values 1,2 or 4. Found: " + str(varint)

	temp_manager.addSensor(sensor)

	if (destination == None):
		temp_manager.onEnter(sensor, function)
	else:
		temp_manager.onEnter(sensor, function, destination)

	temp_manager.onEnter(sensor, EnterProximity, sensorname)
	temp_manager.onExit(sensor, ExitProximity, sensorname)
	print "addSensorToManager: ",
	#print varint
	
	print temp_manager.getSensors()
	del temp_manager



def failOverTheEdge():
	

	global torus
	global greentorusColor
	global redtorusColor
	global success2
	global fail
	global ball
	global overTheEdge
	
	if (overTheEdge): 
		setvarTrialAchievement(True)
		
		print("was a FailTrial")
		#setWrongBalls(getWrongBalls() + 1)
		redtorusColor = torus.color(viz.RED)
		fail.play()
		
	else:
		pass

##
# Adds an interaction to an object. \n
# An object can be a \ref ball or a \ref placement. The sensor that will be used an generated
# by this method have all the type torus. A \b destination is always one of the four shelfobjects.
# \param varint: an interger, which says what manager is to use, \see addSensorToManager
# \param varobject: Contains the object, here it is \ref ball or \ref placement
# \param sensorname: Name of sensor. A string defined by your own
# \param sensorsize: sensor of the size. Distance to the object, when it should start to interact
# \param eventmethod: When triggered, which method should be used.
# \param destination: Location of the object, deault \c None
# \see addSensorToManager
# \see ball, placement, shelfA, shelfB, shelfC, shelfD
def addInteraction(varint, varobject, sensorname, sensorsize, eventmethod, destination=None):
	global InteractionAdded
#	setStartpointpassed('BallMovement')
#	if firstRunInstruction:
#		showInstructions()
#	else:
#		pass

	assert (type(destination) is Shelfobject) or (destination==None), "destination is not a Shelfobject or it is not None."
	eventSensor = varobject.addTheSensor(sensorsize, 1)
	yield addSensorToManager(varint, eventSensor, sensorname, eventmethod, destination)
	#yield failOverTheEdge()
	writeCSVfile("Sensor '{0}' added. It has the size {1}.".format(sensorname, sensorsize))

	setInteractionAdded('InteractionAdded')
	
	if firstRunInstructionMovement:
		showMoveInstruction()
	else:
		pass
		
	InteractionAdded = True
	
	del eventSensor

##
# Logs everytime when a target enters a sensor.
# \param e: the event that has been triggered
# \param sensorname: the sensorname, which has been triggered by a target
def EnterProximity(e, sensorname, Boolean = True):
	mytime = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
	varstring = "entered " + str(sensorname) + " by " + str(e.target) + " managed by " +str(e.manager) + "  " + str(e.manager.getActiveTargets(e.sensor)) + "at {0}".format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
	print varstring
	print manager4
	writeCSVfile(varstring)
	del varstring

##
# Logs everytime when a target exits a sensor.
# \param e: the event that has been triggered
# \param sensorname: the sensorname, which has been triggered by a target
def ExitProximity(e, sensorname):
	varstring = "exited " + str(sensorname) + " by " + str(e.target) + " managed by " +str(e.manager)
	print varstring
	writeCSVfile(varstring)
	del varstring

##
# This method generates and places the \ref viapoint with the size \ref viapointsize. It uses \ref varKoerpergroesse to set
# the height of the \ref viapoint<a></a>.\n
# The height is <code>varKoerpergroesse['Augenhoehe']</code>.
# \param pos_x: float; x-Position of the \ref viapoint
# \param pos_z: float; z-Position of the \ref viapoint
# \see viapoint, varKoerpergroesse, viapointsize
def placeViapoint(pos_x, pos_z):
	global varKoerpergroesse
	global viapoint
	global viapointsize


	viapoint = vizshape.addSphere(radius=viapointsize/3.0)
	viapoint.disable(viz.INTERSECTION)
	viapoint.color(1.0, 1.0, 1.0)
	viapoint.alpha(0.5)
	viapoint.setPosition(pos_x, varKoerpergroesse['Augenhoehe']/1.6, pos_z)
	writeCSVfile('set viapoint at [{0},{1},{2}]'.format(pos_x, varKoerpergroesse['Augenhoehe'], pos_z))
	viapoint.visible(viz.ON)

def placefootplane():
	global varKoerpergroesse
	global footplane
	
	footplane = vizshape.addPlane([0.3, 0.3],vizshape.AXIS_Y)
	footTex = viz.addTexture('path2995.png')
	footplane.texture(footTex)
	footplane.setPosition(1-varKoerpergroesse['Armlaenge'], 0.01, 0.075)
	footplane.setEuler(90,0,0)
	
	
##
# A method, which is used together with a viztask in \ref doTypeA, \ref doTypeB, \ref doTypeC, \ref doTypeD.
# \returns \c True, if the distance between the position of the viewpoint (aka headtarget) and the \ref viapoint is bigger than \c viapointsize+0.2.
# Otherwise \c False.
# \see headtarget, viapoint, viapointsize
# \see doTypeA, doTypeB, doTypeC, doTypeD
def waitForExitTheViapoint():
	global headtarget
	global viapoint
	global viapointsize

	return vizmat.Distance(headtarget.getPosition(),viapoint.getPosition()) > viapointsize+0.2

##	
# A method, which is used together with a viztask in \ref doTypeA, \ref doTypeB, \ref doTypeC, \ref doTypeD.
# \returns \c True, if the distance between the position of the viewpoint 
# (aka headtarget) and the \ref viapoint is smaller than \c viapointsize/2.0-0.08.
# Otherwise \c False.
# \see headtarget, viapoint, viapointsize
# \see doTypeA, doTypeB, doTypeC, doTypeD
def inStartSensor():
	global headtarget
	global viapoint
	global viapointsize

	return vizmat.Distance(headtarget.getPosition(),viapoint.getPosition()) < viapointsize/2.0-0.08

##
# This method adds the sensor 'viapoint-Sound-Sensor' to the \ref viapoint. The sensor is managed by
# \ref manager4. It uses the method \ref playSound.
# \see manager4, viapoint, sensorarray
# \see playSound
def addSoundSensor(pos_x, pos_z):
	global viapoint
	global viapointsize
	global manager4
	global sensorarray
	global torusSensor
	global ball
	global failAreaRight
	global torus
	global torusSensor

	viapoint.remove()
	viapoint = None
	#viapoint = vizshape.addBox([viapointsize, viapointsize, viapointsize])
	#viapoint.disable(viz.INTERSECTION)
	#viapoint.color(1.0, 1.0, 1.0)
	#viapoint.alpha(0.5)
	#Original 13.11.20
	#viapoint.setPosition(pos_x, varKoerpergroesse['Schulterhoehe']+varKoerpergroesse['Kopfhoehe']/2.0, pos_z)
	#viapoint.setPosition(pos_x, varKoerpergroesse['Augenhoehe'], pos_z)
	#viapoint.visible(viz.ON)

	#sensor = vizproximity.Sensor(vizproximity.Box([viapointsize, viapointsize, viapointsize]),viapoint)
	#
	#addSensorToManager(4, sensor, 'viapoint-Sound-Sensor', playSound)
	manager4.setDebug(viz.ON)
	#print "torussensor"
	#print torusSensor
	#torussensor
	#torus = vizshape.addTorus(radius=0.33, tubeRadius=0.01, sides=40, slices=40, axis=vizshape.AXIS_X)
	
	addSensorToManager(4, torusSensor, 'torus-Sensor', playSound)
	#manager4.addSensor(torusSensor)
	sensorarray.append(torusSensor)
	ballTarget = vizproximity.Target(ball.getNode())
	manager4.addTarget(ballTarget)
	#manager4.onEnter(torusSensor, EnterProximity)

	#del sensor

##
# This method is triggered by \ref manager4 and play the sound for the viapoint.
# It also sets the variable \ref viapointpassed to \c True.
# \param e: Event that has been triggered
# \see manager4, sound_bonusseconds, viapointpassed, audio1, sensorarray, headtarget
def playSound(e):
	global target1
	global sound_bonusseconds
	global manager4
	global viapointpassed
	#global audio1
	global sensorarray
	print "playSound"
	#print sensorarray
	if (e.sensor in sensorarray):
		manager4.clearSensors()

		temp_string = 'Torus: Torus passed at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
		writeCSVfile(temp_string)
		setEventstring(temp_string)

		del temp_string
		print sensorarray
		#audio1.play()
		viapointpassed = True
		manager4.removeTarget(target1)
		
#		if (viapointpassed):
#			greentorusColor = torus.color(viz.GREEN)
#			
#		else: 
#			redtorusColor = torus.color(viz.RED)

	else:
		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
		assert(e.sensor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)

##
# This method adds the sensor 'viapoint-Sound-Sensor' to the \ref viapoint. The sensor is managed by
# \ref manager4. It uses the method \ref doTypeA, \ref doTypeB, \ref doTypeC and \ref doTypeD.
# \see manager4, viapoint, sensorarray
# \see playSound, doTypeA, doTypeB, doTypeC, doTypeD
def addStartSensor():
	global viapoint
	global viapointsize
	global manager4
	global sensorarray

	sensor = vizproximity.Sensor(vizproximity.Sphere(radius=viapointsize/3.0),viapoint)
	sensorarray.append(sensor)
	addSensorToManager(4, sensor, 'viapoint-Start-Sensor', sendMyCustomEvent)
	manager4.setDebug(viz.ON)

	del sensor
	

def addBallSensor():
	global ball
	global manager
	global sensorarray

	sensor = vizproximity.Sensor(vizproximity.Sphere(radius= 0.045),ball.getNode())
	sensorarray.append(sensor)
	addSensorToManager(1, sensor, 'Ball-Sensor', sendMyCustomEvent2)
#	manager.setDebug(viz.ON)

	del sensor

def setOverTheEdge(val):
	global overTheEdge 
	overtTheEdge = val
	

def enteredFailSensor(e):
	global manager2
	global sensorarray
	global overTheEdge
	
	if (e.sensor in sensorarray):
		manager2.clearSensors()

		temp_string = 'Ball rolled over the edge' 
		writeCSVfile(temp_string)
		setEventstring(temp_string)

		del temp_string
		print sensorarray
		#audio1.play()
		overTheEdge = True
		#manager2.removeTarget(target1)
		print('entered fail sensor')
#		print("was a FailTrial")
#		setWrongBalls(getWrongBalls() + 1)
#		redtorusColor = torus.color(viz.RED)
#		fail.play()
	else:
		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
		assert(e.sensor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)

def addFailSensor():
	global ball
	global manager2
	global failArea
	global sensorarray
	global shelfA
	
	#vizshape.addQuad(size=(1.0,1.0),axis=-vizshape.AXIS_Z,cullFace=False,cornerRadius=0.0)
	#shelfnode = shelfA.getNode()
	#manager4.addSensor(torusSensor)
	
#	failArea = vizshape.addGrid(size=(0.5,2), step=1.0, boldStep=0.0, axis=vizshape.AXIS_Y, lighting=False)
#	failArea.setPosition([1,,0])
	
	failSensor = vizproximity.Sensor(vizproximity.Box([0.2,0.02,1]),failArea)
	
	sensorarray.append(failSensor)
	addSensorToManager(2, failSensor, 'failSensor', enteredFailSensor)
##	
	manager2.removeTarget(target1)
	ballTarget = vizproximity.Target(ball.getNode())
	manager2.addTarget(ballTarget)
	#manager2.setDebug(viz.ON)
##
	del failSensor
		
def setStartpointpassed(val):
	global startpointpassed
	startpointpassed = val
	
def setInteractionAdded(val):
	global InteractionAdded
	InteractionAdded = val
	
##
# If the sensor of event \c e is in the \c sensorarray, it sets setCUSTOM(True) and is a sensor event for \ref manager4, which 
# acts for the \ref viapoint (activated by \ref headtarget). It also clears the sensor for 
# \ref manager4 and sets the \ref eventstring to <code>Viapoint: startpoint passed at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])</code>.
# It also calls \ref writeCSVfile and sets the \ref eventstring.
# \param e: an event
# \see manager4, sensorarray
# \see setCUSTOM, setEventstring, writeCSVfile
def sendMyCustomEvent(e):
	global manager4
	global sensorarray
	global startpointpassed
	
	print("sendMyCustomEvent called")
	
	if (e.sensor in sensorarray):
		setCUSTOM(True)
		manager4.clearSensors()
		temp_string = 'Startball: startpoint passed' 
		writeCSVfile(temp_string)
		setEventstring(temp_string)
		
		setStartpointpassed('startpointpassed')
		
		if firstRunInstruction:
			showInstructions()
		else:
			pass
			
#		if firstRunInstructionMovement:
#			showMoveInstruction()
#		else:
#			pass
			
		startpointpassed = True
		print ("Startpoint passed")

		del temp_string
	else:
		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
		assert(e.sesnor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)
		


#def sendMyCustomEventI(e):
#	global manager4
#	global sensorarray
#	global startpointpassed
#	global instruction_text1
#	
#	print("sendMyCustomEvent called")
#	
#	if (e.sensor in sensorarray):
#		setCUSTOM(True)
#		manager4.clearSensors()
#		temp_string = 'Viapoint: startpoint passed at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
#		writeCSVfile(temp_string)
#		setEventstring(temp_string)
#		startpointpassed = True
#		print startpointpassed
#		print ("Startpoint passed")
#		
#		del instruction_text1 
#		
#		text2 = viz.addText3D('Bewege den Controller nun in Richtung \
#		\n des blauen Balls auf dem Regal vor dir \
#		\n und greife diesen, indem du den Knopf \
#		\n an der Unterseite des Controllers drückst \
#		\n und anschließend gedrückt hältst')
#		text2.fontSize(1)
#		text2.setCenter([0.0, 0.0, 3.0])
#		text2.setScale([0.125]*3)
#		text2.alignment(viz.ALIGN_CENTER_TOP)
#		
#		text2.setParent(VIEWBALL)
#		text2.setPosition(text2.getCenter())
#
#		del temp_string
#	else:
#		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
#		assert(e.sesnor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)




def sendMyCustomEvent2(e):
	global manager
	global sensorarray
	
	print("sendMyCustomEvent2 called")
	
	if (e.sensor in sensorarray):
		setCUSTOM(True)
		manager.clearSensors()
		temp_string = 'Controller and ball have an intersection' 
		writeCSVfile(temp_string)
		setEventstring(temp_string)

		del temp_string
	else:
		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
		assert(e.sensor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)
		
def passedOverTheEdge(e):
	global manager4
	global sensorarray
	
	print("passedOverTheEdge called")
	
	if (e.sensor in sensorarray):
		setCUSTOM(True)
		manager.clearSensors()
		temp_string = 'Ball passed the edge at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
		writeCSVfile(temp_string)
		setEventstring(temp_string)
		setOverTheEdge = True

		del temp_string
	else:
		assert(len(sensorarray)==1), "Fehler bei Sensorarray = " + str(sensorarray)
		assert(e.sensor in sensorarray), "Fehler bei Sensorarray = " + str(sensorarray)

##
# This method returns the value of \ref boolCUSTOM_EVENT. It is used by \ref doTypeA, 
# \ref doTypeB, \ref doTypeC and \ref doTypeD. There it is used to define a \c viztask.waitTrue.
# \returns a boolean
# \see boolCUSTOM_EVENT
# \see doTypeA, doTypeB, doTypeC, doTypeD, setCUSTOM
def getCUSTOM():
	global boolCUSTOM_EVENT
	
	return boolCUSTOM_EVENT

##
# This method sets the variable \ref boolCUSTOM_EVENT. It will be set \c False in \ref doTypeA, 
# \ref doTypeB, \ref doTypeC and \ref doTypeD, if the \c getvarTrialAchievement returns \c False. 
# It is also used by \ref sendMyCustomEvent. There it will be set to \c True.
# \param val: a boolean
# \see boolCUSTOM_EVENT
# \see doTypeA, doTypeB, doTypeC, doTypeD, getCUSTOM, sendMyCustomEvent
def setCUSTOM(val):
	global boolCUSTOM_EVENT
	
	boolCUSTOM_EVENT = val

##
# This is a little helpful function, which 'converts' the string \c varstring to an object.
# \param varstring: a string, which can has the values 'ShelfA', 'ShelfB', 'ShelfC' or 'ShelfD'
# \return the object variable shelfA, shelfB, shelfC or shelfD
# \see shelfA, shelfB, shelfC or shelfD
# \see Versuchsszenario.py
def getShelf(varstring):
	global shelfA

	assert(varstring=='ShelfA' or varstring=='ShelfB' or varstring=='ShelfC' or varstring=='ShelfD'), "Destination should be ShelfA, ShelfB, ShelfC, ShelfD. Found: "+str(varstring)
	
	if (varstring == 'ShelfA'):
		return shelfA
#	else:
#		if (varstring == 'ShelfB'):
#			return shelfB
#		else:
#			if (varstring == 'ShelfC'):
#				return shelfC

##
# Returns the current destination of the trial.
# \returns a string, which can be \c 'ShelfA', \c 'ShelfB', \c 'ShelfC' or \c 'ShelfD'
# \see setDestination, shrinkTheBall, moveTheBall, moveThePlacement
def getDestination():
	global destination
	
	return destination

##
# This method sets the variable destination.
# \param varstring a string, which can be \c 'ShelfA', \c 'ShelfB', \c 'ShelfC' or \c 'ShelfD'
# \see destination
# \see getDestination, doTypeA, doTypeB, doTypeC, doTypeD
def setDestination(varstring):
	global destination
	
	destination	= varstring

##
# Makes the \ref plane (the startsquare) visible and sets its position. The z-coordinate is
# set to 0.001 to avoid occlusion conflicts.
# \param varX: x-coordinate of the \ref plane; default 0
# \param varZ: z-coordinate of the \ref plane; default 0
# \see plane
def showPlane(varX=0, varZ=0):
	global plane
	
	
	plane.setPosition(varX,0.001,varZ)
	plane.visible(viz.ON)

##
# Makes the \ref plane invisible and sets its position in height of 10 meters.
# \see plane
def hidePlane():
	global plane

	plane.visible(viz.OFF)
	plane.setPosition(0.0,10.0,0.0)


##
# Sets the \c position of the \ref ball and adds the sensors for grabbing (\c ballGrabSensor) and gazing (\c gazeSensor).
# \param position: float-array with x, y and z for the ball's position; default value is <code>[0.0, 0.0, 0.0]</code>
# \see ball, tool, notinthevrlab, manager3, manager5, manager
# \see writeCSVfile
def showBall(position = [0.0, 0.0, 0.0]):
	global ball
	global tool
	global notinthevrlab
	global manager3
	global controllerGrabber

	if (notinthevrlab):
		pass
	else:
		pass

	# add the ball to tool as a grabbable one
	#print "Hier ist tool Liste Items", 
	#print tool.getItems()
	
	tool.addItems([ball.getNode()])
	tool.setItems([ball.getNode()])

	#print tool.getItems()
	
	#ball.setVelocity(0,10,0)

	# position should be a position on the middle of a rack of startshelf
	yield ball.setBallPosition(position)
	print "ball placed at startshelf at {0}".format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])

	yield writeCSVfile("ball placed at startshelf at {0}".format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]))

	# Wird in prepareForNextTrial wieder deaktiviert
	yield writeCSVfile('vizact.ontimer(writeCSVfile) -> start')
	varonupdate.setEnabled(viz.ON)
	
	#del ballGrabSensor

##
# Moves the ball. Ball is always on \ref shelfA. When sensor was triggered and the \ref actionevent was 
# perfomed, the sensor will be removed from the manager (\ref manager). It also sets the \ref eventstring 
# (via \ref setEventstring) and logs it (via \ref  writeCSVfile). 
# \param e: the event, which has been triggered
# \see shelfA, ball, manager, actionevent, writeCSVfile, setEventstring, getFiftyFifty
def moveTheBall(e):
	global ball
	global shelfA
	global manager
	global actionevent
	global overTheEdge

	temp_string = 'Event: ball movement starts at {0}. Sensorsize = {1}. Destination = {2}'.format( datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3], getSensorSize(), getDestination())
	writeCSVfile(temp_string)
	setEventstring(temp_string)

	del temp_string

	myball = ball.getNode()
	tinydistance = 0.05
	adjustment = abs(Shelfobject.varShelfWidth/1.8)#-tinydistance)
	z = 0

	if (getFiftyFifty()):
		z = -adjustment #nach rechts
	else:
		z = adjustment #nach links

	ballposition = myball.getPosition()
	manager.removeSensor(e.sensor)
	actionevent = vizact.moveTo([ballposition[0], ballposition[1], ballposition[2]+z], time=0.7)
		
	if z == -adjustment:
		actionevent2 = vizact.spinTo(euler=[0,-180,0], speed=500)
		#05.1.22 Modification
		print 'ball has been moved to the left at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
		writeCSVfile('Perturbation left')
		
	else:
		actionevent2 = vizact.spinTo(euler=[0,180,0], speed=500)
		#05.1.22 Modification
		print 'ball has been moved to the right at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
		writeCSVfile('Perturbation right')
		
	print("moveTheBall")
	print(z)
	
	myball.addAction(actionevent, 0)
	myball.addAction(actionevent2, 1)
	myball.runAction(actionevent, 0)
	myball.runAction(actionevent2, 1)
	

	del z
	del myball
	del tinydistance
	del adjustment
	del ballposition



##
# This method is triggered by the sensor \ref showBall "ballGrabSensor" of \ref manager. It uses the variable
# \ref ignore to check if just one hand entered the \ref ball sensor. If so, it sets \ref grableftright. Otherwise
# it performes the grab. It also adds a new sensor to \ref manager, which calls \ref releaseTheBall.
# \see tool, grabberLefthand, grabberRighthand, myLink1, myLink2, grableftright, ignore, ball, manager, manager3, 
# \see writeCSVfile

#def goOn(e):
#	global ball 
#	
#	if ball is None and startpointpassed is 'isReleased' and e.button == steamvr.BUTTON_TRACKPAD:
#		print('touchpad pressed')
#		setFirstRunInstruction(False)
#	else:
#		pass
		

def grabEvent(e):
	
	global controllersteam
	global firstGrab
	
	global ball
#	print "ungrabbed by controller"
#	print controllersteam
	i = controllersteam.getTrigger()
	
	print i	
	global tool
	global manager
	global manager2
	global manager3
	global isGrabbed

	print "ball = ",
	print ball
	

	if ball is not None:
		sphere = ball.getNode().getBoundingSphere()
		radius = sphere.radius
		print sphere
		print radius
#		manager2.removeTarget(target1)
#		manager2.addTarget(ball.getNode())
		
	#	if vizmat.Distance(tool.getPosition(), ball.getNode().getPosition()) <= radius/2:
#			print 'controller and ball have an intersection at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
#			writeCSVfile('controller and ball have an intersection at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]))
			
		if e.button == steamvr.BUTTON_TRIGGER and vizmat.Distance(tool.getPosition(), ball.getNode().getPosition()) <= radius/2 and firstGrab == True:
			tool.grab()
			isGrabbed = True
			firstGrab = False
			setStartpointpassed('isGrabbed')
			if firstRunInstruction:
				showInstructions()
			else:
				pass
			print 'ball has been grabbed at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
			writeCSVfile('ball has been grabbed')
	

		else:
			print "Es war Button ",
			print e.button
			pass
	else:
		pass

	#eventobject = (e.target).getSourceObject()


## 
# Method to use, when not in the vr-lab.
# \see notinthevrlab
# \see grabEvent
def grabEvent2(e):
	global tool
	global grabberLefthand
	global grabberRighthand
	global manager
	global manager3
	global target1

	eventobject = (e.target).getSourceObject()

	if (not ignore):
		if (grableftright == None):
			if(eventobject == grabberLefthand):
				assert(eventobject == grabberLefthand)
				grableftright = False
				viz.link(grabberLefthand,tool)
			else:
				assert(eventobject == grabberRighthand), "event triggered from the wrong target: " + eventobject
				viz.link(grabberRighthand,tool)
				grableftright = True
		else:
			newsensoristheold = e.sensor
			
			if(grableftright and (eventobject == grabberLefthand)):
				tool.grab()
				manager3.removeTarget(target1)
				manager.removeSensor(e.sensor)
				manager.addSensor(newsensoristheold)
				manager.onExit(newsensoristheold, releaseTheBall, "releaseTheBall-Sensor")
				ignore = True
			else:
				assert(eventobject == grabberLefthand)
				
				if((not grableftright) and (eventobject == grabberLefthand)):
					assert(not grableftright)
					manager3.removeTarget(target1)
					# beware: difference between grabAndHold und grab
					tool.grab()
					manager.removeSensor(e.sensor)
					manager.addSensor(newsensoristheold)
					manager.onExit(newsensoristheold, releaseTheBall, "releaseTheBall-Sensor")
					ignore = True
				else:
					assert(eventobject in [grabberRighthand, grabberLefthand] and grableftright in [True, False]), "Grabbing went wrong :-("

	del eventobject
	
##
# Used in releaseTheBall.
# \param val: a boolean.
# \see varTrialAchievement
# \see releaseTheBall, getvarTrialAchievement
def setvarTrialAchievement(val):
	global varTrialAchievement
	
	assert type(val) is BooleanType, "val is not a boolean: %r" % val
	varTrialAchievement = val

##
# Returns the value of \ref varTrialAchievement. 
# \returns value of varTrialAchievement (\c True or \c False)
# \see setvarTrialAchievement, doTypeA, doTypeB, doTypeC, doTypeD
def getvarTrialAchievement():
	global varTrialAchievement
	
	return varTrialAchievement


queue = [[0,0,0],[0,0,0]] #current and last position of foot


def queuing (): #keeps track of position of rigidTracker, updates ten times per second
	global queue, controller

	queue[1] = queue[0]
	queue[0] = controller.getPosition()


def dir_vec(): #returns the direction of movement in the last tenth second
	global queue

	last = queue[0]
	prelast = queue[1]
	x = last[0]-prelast[0]
	y = last[1]-prelast[1]
	z = last[2]-prelast[2]

	return ([x,y,z])	

vizact.ontimer(.1,queuing) 	


	
##
# If activated by an event \c e, it runs on \ref tool the command \c release. Which means the \ref ball will
# be released. It also set \ref grableftright to \c None. Furthermore it sets \ref ignore and 
# \ref varTrialAchievement to \c False. It also send the \ref MY_SUPER_SPECIAL_CUSTOM_EVENT and logs
# the sentence "releaseTheBall: ball has been released". It plays the sound \ref sad.
# \param e: the event, which triggers (e. g. \c viz.KEYDOWN_EVENT)
# \param sensorname: a string
# \see ignore, tool, grableftright, manager, manager3, ball, placement, actionevent, MY_SUPER_SPECIAL_CUSTOM_EVENT
# \see setvarTrialAchievement, writeCSVfile
def releaseTheBall(e):
	global tool
	global manager
	global manager3
	global ball
	global actionevent
	global MY_SUPER_SPECIAL_CUSTOM_EVENT
	global isGrabbed
	#global isReleased

#	sphere = ball.getNode().getBoundingSphere()
#	radius = sphere.radius
#	print sphere
#	print radius	

	if ball is not None:
		sphere = ball.getNode().getBoundingSphere()
		radius = sphere.radius
		print sphere
		print radius
		manager.removeTarget(target1)
		manager2.removeTarget(target1)
		manager3.removeTarget(target1)
		if e.button == steamvr.BUTTON_TRIGGER and isGrabbed == True and  vizmat.Distance(tool.getPosition(), ball.getNode().getPosition()) <= radius*5:
			myballnode = ball.getNode()
			pos = ball.getBallPosition()
			velo = ball.getBallVelocity()
			print velo
			print pos
			dirvec =  dir_vec()
#			print dirvec
#			velo = myballnode.getVelocity(mode=viz.REL_PARENT)
#			print velo
#			velo = myballnode.getVelocity(mode=viz.REL_GLOBAL)
#			print velo
#			ball.applyForceToBall(dirvec)
			#myballnode.applyForce(dir = [dirvec[0], dirvec[1], dirvec[2]])#, duration=3)
			#myballnode.applyForce(dir = [0, 1, 0])#, duration=3)
			print("")			
			setvarTrialAchievement(True)
			setStartpointpassed('isReleased')
			if firstRunInstruction:
				showInstructions()
			else:
				pass
			viz.sendEvent(MY_SUPER_SPECIAL_CUSTOM_EVENT)
			tool.release()
			writeCSVfile('releaseTheBall: ball has been released') 
			print("releaseTheBall: ball has been released at {0}".format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]))
			print("")
			isGrabbed=False
		else:
			pass
	else:
		pass
		
#	if pos[1] == 0:
#		print 'ball has touched the ground'

##
# This method just contains a viztask object.
def waitForSpace():
	yield viztask.waitKeyDown(' ')

##
# This method helps to log the key events during the experiment.
# It logs it via \ref writeCSVfile. If 'd' was pressed ,it toggles the debug mode
# \ref manager and \ref manager3. If 't' ist pressed, it releases the \ref ball
# (a debug feature).
# \param key: which was pressed
# \see manager, manager3
# \see writeCSVfile, releaseTheBall
def onKeyDown(key):
	global manager
	global manager2
	global manager3
	global text4
	global firstRunInstruction

	stringattached = ''

	if (key == 'd'):
		manager.setDebug(viz.TOGGLE)
		manager2.setDebug(viz.TOGGLE)
		manager3.setDebug(viz.TOGGLE)
		stringattached = ", manager debugmode toggled."
	elif (key == 't'): # der Nothaken
		calculateTrial()
	elif (key == 'n'):
		stringattached = ", Programmstart."
	elif (key == ' '):
		stringattached = ", '<space> was pressed'"
#	elif (key == 'g'):
#		setFirstRunInstruction(False)
#		text4.message('')
	else:
		pass

	viz.logNotice("'" + str(key) + "'-key pressed" + stringattached)
	writeCSVfile("'" + str(key) + "'-key pressed" + stringattached)

	del stringattached

##
# It log the start and end message of trial.
# \param type: the type of the trial, which can be \c 'TypeA', \c 'TypeB', \c 'TypeC' or \c 'TypeD'
# \param boolean: a boolean, which should be set to \c True if the trial starts
# \see setEventstring, writeCSVfile
def messageStartEnd(type, boolean=True):
	varstring = ''
	mytime = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
	
	if(boolean):
		varstring = "{0} starts at {1}".format(type, mytime)
	else:
		varstring = "{0} ends at {1}".format(type, mytime)

	writeCSVfile(varstring)
	setEventstring(varstring)
	viz.logNotice(varstring)

	del varstring

##
# Puts the \ref ball on in the middle of the rack \c number of the start shelf.
# \c number can have the value \c 1 to \c 3. Where \c 1 is the highest rack of a shelf.
# Example of \c ballcode for a Typ A-trial. Here \c number has the value \c 2:
# \code{.py}
#						'Ball' : {'Rack': 2, 'Destination': 'ShelfB', 'Placement': 3}
# \endcode
# \param ballcode: contains the rack \c number, the destination shelf and number
# of the rack, where the placement has to appear.
# \see doTypeA, doTypeB, doTypeC, doTypeD, putPlacementOnRackNr, getRackOfShelf
# \see shelfA
def putBallOnRackNr(ballcode):
	global shelfA

	number = ballcode['Rack']
	rackOfShelf = shelfA.getRackOfShelf(number)
	rackpos = rackOfShelf.getPosition(viz.ABS_GLOBAL)
	yield showBall([rackpos[0], rackpos[1]+0.1/2+Shelfobject.varShelfBoardThickness/2, rackpos[2]])#pivot of ball is in the center

	del number
	del rackOfShelf
	del rackpos

##
# Same as \ref putBallOnRackNr, just with start shelf definitions.
# \param ballcode: contains the rack \c number, the destination shelf and number
# \see doTypeA, doTypeB, doTypeC, doTypeD, putPlacementOnRackNr, getRackOfShelf
# \see shelfA
def putBallOnRackNr2(ballcode):
	global shelfA
	rackpos = [0.0, 0.0, 0.0]
	global failArea
	
	number = ballcode['Rack']
	startshelf = ballcode['Start']
	if (startshelf == 'ShelfA'):
		rackOfShelf = shelfA.getRackOfShelf(number)
		rackpos = rackOfShelf.getPosition(viz.ABS_GLOBAL)
	else:
		pass
	
	
	yield showBall([rackpos[0], rackpos[1]+0.1/2+Shelfobject.varShelfBoardThickness/2, rackpos[2]])#pivot of ball is in the center
	#ball = viz.addChild('beachball.osgb', cache = viz.CACHE_COPY)
	#ball.setPosition([rackpos[0], rackpos[1]+0.1/2+Shelfobject.varShelfBoardThickness/2, rackpos[2]])
	#viz.link(ball.getNode(),ball)
	failArea = vizshape.addGrid(size=(0.15,1), step=0.01, boldStep=0.0, axis=vizshape.AXIS_Y, lighting=False)
	failArea.setPosition(rackpos[0],rackpos[1]-0.005,rackpos[2])
	#yield addFailSensor()
#	failSensor = vizproximity.Sensor(vizproximity.Box([0.5,0.01,1]),failArea)
#	sensorarray.append(failSensor)
#	addSensorToManager(4, failSensor, 'failSensorRight', setOverTheEdge)
	

	
#	
##	#manager4.setDebug(viz.ON)
#
	del number
	
	del rackpos
	del startshelf

##
# This function sets the value of \ref numberOfBalls.
# \param val: the new value for \ref numberOfBalls
# \see numberOfBalls
# \see handleBlock
def setNumberOfBalls(val):
	global numberOfBalls
	
	numberOfBalls = val

##
# It returns the value of \ref numberOfBalls.
# \returns number of balls in the current trial
# \see numberOfBalls
# \see handleBlock
def getNumberOfBalls():
	global numberOfBalls
	
	return numberOfBalls

##
# It sets the value of \ref goodballs.
# \param val: an integer
# \see goodballs
# \see getGoodBalls
def setGoodBalls(val):
	global goodballs
	
	goodballs = val

##
# It returns the value of \ref goodballs.
# \returns an integer
# \see goodballs
# \see handleBlock, TrialCountUpTask, TrialCountDownTask, setGoodBalls
def getGoodBalls():
	global goodballs
	
	return goodballs

##
# It sets the value of \ref wrongballs.
# \param val: an integer
# \see wrongballs
# \see handleBlock, TrialCountUpTask, TrialCountDownTask
def setWrongBalls(val):
	global wrongballs
	
	wrongballs = val

##
# It returns the value of \ref wrongballs.
# \returns an integer
# \see wrongballs
# \see handleBlock, TrialCountUpTask, TrialCountDownTask
def getWrongBalls():
	global wrongballs
	
	return wrongballs

##
# It returns the value of \ref trial_duration_temp.
# \returns an integer, which means \a seconds
# \see trial_duration_temp
def getTrialDurationTemp():
	global trial_duration_temp
	
	return trial_duration_temp

##
# It returns the value of \ref TRIAL_DURATION.
# \returns an integer, which means \a seconds
# \see TRIAL_DURATION
def getTrialDuration():
	global TRIAL_DURATION
	
	return TRIAL_DURATION

##
#  This method counts up the last five seconds of a trial. It is used by \ref handleBlock<a></a>.
# \see remain, wrongball_text, ball_text
# \see getGoodBalls, getNumberOfBalls, getWrongBalls, TrialCountDownTask
def TrialCountUpTask():
	global remain
	global wrongball_text
	global ball_text

	"""Task that count downs to time limit for trial"""
		# Action for text fading out
	text_fade = vizact.parallel(vizact.fadeTo(0, time=0.8, interpolate=vizact.easeOut), vizact.sizeTo([1.5,1.5,1.0], time=0.8, interpolate=vizact.easeOut))

	ball_text.clearActions()
	ball_text.alpha(1.0)
	ball_text.color(viz.GREEN)
	ball_text.setScale([0.01]*3)
	ball_text.message(str(getGoodBalls()) + "/" + str(int(getNumberOfBalls())))

	wrongball_text.clearActions()
	wrongball_text.alpha(1.0)
	wrongball_text.color(viz.RED)
	wrongball_text.setScale([0.01]*3)
	wrongball_text.message(str(getWrongBalls()))

	# Countdown from time limit
	start_time = viz.getFrameTime()
	last_remain = int(0)

	while (True):
		# Compute remaining whole seconds
		remain = int(math.ceil((viz.getFrameTime() - start_time)))

		# Update text if time remaining changed
		if (remain != last_remain):
			ball_text.message(str(getGoodBalls()) + "/" + str(int(getNumberOfBalls())))
			wrongball_text.message(str(getWrongBalls()))
			last_remain = remain

		# Wait tenth of second
		yield viztask.waitTime(0.1)

	del start_time
	del last_remain

##
#  This method counts down the last five seconds of a trial. It is used by \ref handleBlock<a></a>.
# \see TRIAL_DURATION, trial_duration_temp, remain, time_text, ball_text, wrongball_text, beep
# \see getGoodBalls, getNumberOfBalls, getWrongBalls, TrialCountUpTask
def TrialCountDownTask():
	global TRIAL_DURATION
	global trial_duration_temp
	global remain
	global time_text
	global ball_text
	global wrongball_text
	global beep

	"""Task that count downs to time limit for trial"""
	# Action for text fading out
	text_fade = vizact.parallel( vizact.fadeTo(0, time=0.8, interpolate=vizact.easeOut), vizact.sizeTo([1.5, 1.5, 1.0], time=0.8, interpolate=vizact.easeOut)	)

	# Reset time text
	time_text.clearActions()
	time_text.alpha(1.0)
	time_text.color(viz.WHITE)
	time_text.setScale([0.01]*3)
	time_text.message(str(int(TRIAL_DURATION)))

	ball_text.clearActions()
	ball_text.alpha(1.0)
	ball_text.color(viz.GREEN)
	ball_text.setScale([0.01]*3)
	ball_text.message(str(getGoodBalls()) + "/" + str(int(getNumberOfBalls())))

	wrongball_text.clearActions()
	wrongball_text.alpha(1.0)
	wrongball_text.color(viz.RED)
	wrongball_text.setScale([0.01]*3)
	wrongball_text.message(str(getWrongBalls()))

	# Countdown from time limit
	start_time = viz.getFrameTime()
	#TODO getTrialDuration getTrialDurationTemp letztres wird wirklich gebraucht???
	last_remain = int(TRIAL_DURATION)
	trial_duration_temp = int(TRIAL_DURATION)

	while (viz.getFrameTime() - start_time) < TRIAL_DURATION:
		trial_duration_temp = getTrialDurationTemp() #TODO wird wirklich gebraucht??? nur TRIAL_DURATION????
		# Compute remaining whole seconds
		remain = int(math.ceil(trial_duration_temp - (viz.getFrameTime() - start_time)))

		# Update text if time remaining changed
		if (remain != last_remain):

			if (remain <= 5):
				time_text.alpha(1.0)
				time_text.color(viz.RED)
				time_text.setScale([0.01]*3)
				time_text.runAction(text_fade)
				beep.play()

			time_text.message(str(remain))
			ball_text.message(str(getGoodBalls()) + "/" + str(int(getNumberOfBalls())))
			wrongball_text.message(str(getWrongBalls()))
			last_remain = remain

		# Wait a tenth of second
		yield viztask.waitTime(0.1)

	del start_time
	del last_remain

##
# It sets a new value for \ref int_i. \ref int_i
# stands for block number.
# \see int_i
# \see getBlock
def setBlock(number):
	global int_i
	
	int_i = number

##
# It returns the value of \ref int_i.
# \returns an integer
# \see int_i
# \see setBlock
def getBlock():
	global int_i
	
	return int_i

##
# Sets the variable \ref varTrialID.
# \param number: integer, which will be the new value
# \see varTrialID
def setTrial(number):
	global varTrialID
	
	varTrialID = number

##
# This function checks if the \c filename for the current log already exists.
# It is used by \ref myTaskSchedule and generates a filelist with the variable \ref ORDNERPFAD.
# \param filename: a string; name of the logfile
# \returns \c True if it exists, else \c False
# \see ORDNERPFAD
# \see myTaskSchedule
def fileExists(filename):
	global ORDNERPFAD
	
	filelist = os.listdir(ORDNERPFAD)

	return (filename in filelist)

##
# It sets a new value for \ref varTrialType.
# \param val: a string
# \see varTrialType
# \see getTrialType
def setTrialType(val):
	global varTrialType
	
	varTrialType = val

##
# It returns the value of \ref varTrialType.
# \returns a single character, which can be \c A, \c B, \c C od \c D
# \see varTrialType
# \see setTrialType
def getTrialType():
	global varTrialType
	
	return varTrialType

##
# It sets the variable \ref show_time to a new value.
# \param val: a boolean, which is \c True, if the text for time has to be on screen
# \see show_time
# \see getShowTime
def setShowTime(val):
	global show_time
	
	show_time = val

##
# It return the value of \ref show_time.
# \returns \c True of \c False
# \see show_time
# \see setShowTime
def getShowTime():
	global show_time
	
	return show_time

##
# The function checks if the current velocity vector is close to zero. If so, it returns \c True.
# \returns a boolean, which is \c True, if the \ref ball has nearly no velocity anymore
# \see doTypeA, doTypeB, doTypeC, doTypeD,
def isVelocityZero():
	global ball
	
	myballnode = ball.getNode()
	velo = myballnode.getVelocity()
	return (np.allclose(velo[0], 0.0) and np.allclose(velo[1], 0.0) and np.allclose(velo[2], 0.0))

def settorusBallIntersection(val):	
	global vartorusBallIntersection

	vartorusBallIntersection = val
	
def gettorusBallIntersection():	
	global vartorusBallIntersection
	
	return vartorusBallIntersection

def getBallVelocity():
	global ball
	
	myballnode = ball.getNode()
	velocity = myballnode.getVelocity()
	return velocity
	print(velocity)
	
##
# This method increments the variable \ref goodballs, if 
# \ref viapointpassed and \ref varPlacementBallIntersection are 
# \c True. Otherwise it increments \ref wrongballs. It also updates the variable \ref varPlacementBallIntersection for logging in \ref writeCSVfile.
# \param varplacement a boolean; it is set in \ref doTypeA, \ref doTypeB, \ref doTypeC or \ref doTypeD.
# \see viapointpassed, varPlacementBallIntersection
# \see doTypeA, doTypeB, doTypeC, doTypeD, writeCSVfile, setWrongBalls, getWrongBalls, setGoodBalls, getGoodBalls, sad
def calculateTrial():
	global viapointpassed
	global torus
	global greentorusColor
	global redtorusColor
#	#global varPlacementBallIntersection
#	global vartorusBallIntersection
	global sad
#	vartorusBallIntersection = val
	global success2
	global fail
	global ball
	global overTheEdge
	
	#vartorusBallIntersection = torusBallIntersection
	#varPlacementBallIntersection = varplacement
	#stattdessen torusBallIntersection mit Enterproximity oder manager.onEnter?
	#print('torus and ball have an intersection = ' + str(torusBallIntersection),)
	#print("viapointpassed = " + str(viapointpassed) + " and placement.hasIntersection() = " + str(torusBallIntersection),)

#	if (viapointpassed and varPlacementBallIntersection): #viapoint raus und nur torusBallIntersection?
#		print("was a GoodTrial")
#		setGoodBalls(getGoodBalls() + 1)
	myball = ball.getNode()
#	if (getFiftyFifty()):
#		z = -adjustment #nach rechts
#	else:
#		z = adjustment #nach links
	ballposition = myball.getPosition()
	
	if (viapointpassed):
		print("was a GoodTrial")
		setGoodBalls(getGoodBalls() + 1)
		greentorusColor = torus.color(viz.GREEN)
		success2.play()
#		
##	elif (overTheEdge): 
##		print("was a FailTrial")
##		setWrongBalls(getWrongBalls() + 1)
##		redtorusColor = torus.color(viz.RED)
##		fail.play()
#
	else:
		print("was a FailTrial")
		setWrongBalls(getWrongBalls() + 1)
		redtorusColor = torus.color(viz.RED)
		fail.play()

#	if not (viapointpassed):
#		print("was a FailTrial")
#		setWrongBalls(getWrongBalls() + 1)
#		redtorusColor = torus.color(viz.RED)
#		fail.play()






##
# This method sets a new value for the variable \ref varSensorsize.
# \see varSensorsize
# \see getSensorSize
def setSensorSize(val):
	global varSensorsize
	
	varSensorsize = val

##
# It returns the value of \ref varSensorsize.
# \see varSensorsize
# \see setSensorSize
def getSensorSize():
	global varSensorsize
	
	return varSensorsize

##
# Handles the dictionary by blocks. It is a recursive call.
# \brief Parameter \c b contains at the first call the whole dictionary, which is defined in \c vardict in \c Versuchsszenario*.\c py.
# \param b: contains the content of \c vardict
# \see getBlock, setBlock, handleBlock, handleDict
def handleDict(b):
	if (len(b) > 0):
		viz.logNotice('Starting of Block {0}.'.format(getBlock()))

		temp_string = 'Block{0}'.format(getBlock())
		#print b
		temp = b[temp_string]

		del b[temp_string]
		del temp_string

		returnval = yield handleBlock(temp)
		del temp

		viz.logNotice(returnval)
		del returnval

		yield setBlock(getBlock()+1)

		yield handleDict(b)
	else:
		assert(getBlock()>0), 'Nothing was in the dictionary. 0_O'
		pass

##
# This method creates the shelfes. It sets the positions and directions of the shelfes. Directions and positions are defined
# in \c ShelfDef in \c Versuchsszenario*.\c py.
# \param b: snippet of \c vardict.
# \see varKoerpergroesse, shelfA, shelfB, shelfC, shelfD, shelfAcolors, shelfBcolors, shelfCcolors, shelfDcolors, plane_v
# \see writeCSVfile, Shelfobject.setShelfPosition , Shelfobject.setShelfDirection, Shelfobject.setShelfColor, Shelfobject.setShelfPosition
def handleShelfes(b):
	global shelfA
	global shelfAcolors
	global varKoerpergroesse
	global plane_v

	writeCSVfile("Koerpergroesse = " + str(varKoerpergroesse['Koerpergroesse']))
	writeCSVfile("Bodyweight = " + str(varBodyweight))
	writeCSVfile("Shoulder-to-shoulder length = " + str(varShoulderToShoulderLength))
	writeCSVfile("Upper arm length = " + str(varUpperArmLength))
	writeCSVfile("Fore arm length = " + str(varForeArmLength))
	
	
	# build shelfes
	shelfA = Shelfobject((varKoerpergroesse['Koerpergroesse']-0.5), (varKoerpergroesse['Schulterhoehe'])-(varKoerpergroesse['Armlaenge']/2), (varKoerpergroesse['Kopfhoehe']*2), (varKoerpergroesse['Armlaenge']*0.9) )
	shelfA.setShelfColor(shelfAcolors[0],shelfAcolors[1],shelfAcolors[2])
	writeCSVfile('Color of ShelfA (color, ambient, emissive): ' + str(shelfAcolors))
	temp_shelf = b['ShelfA']
	shelfDirection = temp_shelf['Direction']
	shelfA.setShelfDirection(shelfDirection)
	writeCSVfile('Direction of ShelfA: ' + str(shelfDirection))
	position = temp_shelf['Position']
	shelfA.setShelfPosition(position)
	writeCSVfile('Position of ShelfA: ' + str(position))
	writeCSVfile("shelfA is " + str(shelfA.getShelfChildren()) )
	del b['ShelfA']

	del position
	del temp_shelf
	del shelfDirection

##
# It sets the starttime of the current trial.
# \see varTrailStartTime
# \see handleTrials
def setTrialStartTime():
	global varTrailStartTime
	
	varTrailStartTime = time.time()

##
# Calculates the duration of a trial. It is used in \ref handleTrials and sets the value for \ref varTrailDuration.
# \see varTrailStartTime, varTrailDuration
# \see handleTrials
def calculateTrialDurationTime():
	global varTrailStartTime
	global varTrailDuration
	
	varTrailDuration = (time.time() - varTrailStartTime)
	
##
# Sets the effect of a trial. It is used in \ref handleTrials<a></a>.
# \param varstring: a string, which can be \c 'LOOKATINVISIBILTY', \c 'HYSTERESIS', \c 'OCCLUSION' or \c 'ALWAYSVISIBLE'
# \param varnumber: a float, which can mean \a seconds (case \c 'HYSTERESIS') or \a diameter \a in \a cm (case \c 'OCCLUSION'); default is \c 0.
# \see BALLALWAYSVISIBLE, BALLHYSTERESIS, BALLOCCLUSION
# \see setEffectstring, setCountdownHysteresis, setOcclusionCylinderDiameter
def setEffect(varstring, varnumber = 0):
	global BALLALWAYSVISIBLE
	
	if (varstring is 'LOOKATINVISIBILTY'):
		BALLALWAYSVISIBLE = False
		BALLHYSTERESIS = False
		BALLOCCLUSION = False
	elif (varstring is 'ALWAYSVISIBLE'):
		BALLALWAYSVISIBLE = True
		BALLHYSTERESIS = False
		BALLOCCLUSION = False
	
	yield setEffectstring(varstring)

def getfirstRunInstruction():
	global firstRunInstruction
	return firstRunInstruction
	
def setFirstRunInstruction(val):
	global firstRunInstruction
	firstRunInstruction = val

def getfirstRunInstructionMovement():
	global firstRunInstructionMovement
	return firstRunInstructionMovement
	
def setFirstRunInstructionMovement(val):
	global firstRunInstructionMovement
	firstRunInstructionMovement = val
	
##
# It handles every single trial in a block. The method is called by \ref handleBlock<a></a>.
# \param b: a snippet of dictionary \c vardict, which contains all trials of the current block
# \see varTrialAchievement, ball, placement
# \see writeCSVfile, setTrial, setTrialType, setTrialStartTime, setEffect, doTypeA, doTypeB, doTypeC, doTypeD, prepareForNextTrial, calculateTrialDurationTime
def handleTrials(b):
	global varTrialAchievement
	global ball
	global firstRunInstruction
	global text4


	variter = len(b)

	assert type(variter) is IntType, "variter is not an integer: %r" % variter

	viz.logNotice(str(variter) + " progams were detected.")
	viz.logNotice("Length of block: " + str(len(b)))

	for a in range(variter):
		assert 'Type' in b[str(a+1)], "\'Type\' not found."
		yield setTrial(a+1)
		vartrial = b[str(a+1)]
		vartype = vartrial['Type']
		del vartrial['Type']
		
		print  "b =", b[str(a+1)]
		assert 'Effect' in  b[str(a+1)], "\'Effect\' not found."
		
		vareffect = vartrial['Effect']
		del vartrial['Effect']

		assert(vareffect in ['ALWAYSVISIBLE', 'HYSTERESIS', 'OCCLUSION', 'LOOKATINVISIBILTY']), "vareffect has the value '%s', but it should be \'ALWAYSVISIBLE\', \'HYSTERESIS\', \'LOOKATINVISIBILTY\' or \'OCCLUSION\'" % vareffect
		
		if (vareffect is 'ALWAYSVISIBLE' or vareffect is 'LOOKATINVISIBILTY'):
			yield setEffect(vareffect, 0)
			vareffectvalue = 0
		else: 
			assert 'Effectvalue' in  b[str(a+1)], "\'Effectvalue\' not found."
			vareffectvalue = vartrial['Effectvalue']	
			del vartrial['Effectvalue']
			yield setEffect(vareffect, vareffectvalue)
		
		#writeCSVfile('Effect for this trial is ' + vareffect + " and the angle/seconds number has the value " + str(vareffectvalue))
		viz.logNotice("\nTrial {0}: ".format(a+1)),

		assert(b[str(a+1)] == vartrial)
		assert(vartype in ['A', 'B', 'C', 'D']),  "this type is not exiting: %r" % vartype

		yield setTrialType(vartype)
		yield setTrialStartTime()
	
#		intr = getfirstRunInstruction()
		
#		if intr == False:
#			text4.message('')
#		else:
#			pass
		
		if(vartype == 'A'):
			yield doTypeA(vartrial)
		else:
			if(vartype == 'B'):
				yield doTypeB(vartrial)
			else:
				if (vartype == 'C'):
					yield doTypeC(vartrial)
				else:
					yield doTypeD(vartrial)


		del vartrial
		del vartype
		del vareffect
		del b[str(a+1)]
		
		# Wurde in showBall aktiviert
		varonupdate.setEnabled(viz.OFF)
		yield writeCSVfile('vizact.ontimer(writeCSVfile) -> end')
		yield viztask.waitTime(0.1)
		yield writeCSVfile('lastLine? Trialduration: ' + str(calculateTrialDurationTime()) )
		yield prepareForNextTrial()

	del variter

##
# The method handles the blocks of a dictionary. It waits for <code>\<space\></code>-key to start the current block \c b.
# It also waits for a <code>\<space\></code>-key to prepare the next block and calls \ref prepareForNextBlock. If the block 
# has a time limit, it calls \ref setShowTime. It set the 3D-texts \ref wrongball_text and \ref ball_text with
# the values of \ref getGoodBalls, \ref getWrongBalls and \ref getNumberOfBalls. If \ref getShowTime returns \c True, it
# will call \ref TrialCountDownTask, otherwise it calls \ref TrialCountUpTask.
# \param b: a snippet of the dictionary, which is the current block to handle
# \see prepareForNextBlock, handleShelfes, handleTrials, waitForSpace, setShowTime, getShowTime, setNumberOfBalls, 
# getNumberOfBalls, getWrongBalls, getGoodBalls, TrialCountDownTask, TrialCountUpTask
# \see remain, ball_text, wrongball_text
def handleBlock(b):
	global remain
	global ball_text
	global wrongball_text
	
	viz.logNotice('BlockStart *****************************************************************')
		
	
	yield waitForSpace()
#	varonupdate2.setEnabled(viz.ON)

	yield handleShelfes(b['ShelfDef'])
	del b['ShelfDef']
	
	yield setNumberOfBalls(len(b['Trials']))
	wait_trials = handleTrials(b['Trials'])
	del b['Trials']

	if (b['Time'] == 'No'):
		yield setShowTime(False)
	else:
		assert(b['Time'] == 'Yes')
		yield setShowTime(True)

	del b['Time']

	if (getShowTime()):
		wait_time = viztask.waitTask( TrialCountDownTask() )
		data = yield viztask.waitAny([wait_time, wait_trials])
		writeCSVfile('Time left: ' + str(remain) + ' seconds.')
	else:
		assert(not show_time)
		wait_time = viztask.waitTask( TrialCountUpTask() )
		data = yield viztask.waitAny([wait_time, wait_trials])
		writeCSVfile('Time needed: ' + str(remain) + ' seconds.')

	"""
	if data.condition is wait_time:
		print "data.condition is wait_time"
		temp = TRIAL_DURATION
		TRIAL_DURATION = 0
		TRIAL_DURATION = temp
	else:
		pass
	"""
	ball_text.message(str(getGoodBalls()) + "/" + str(int(getNumberOfBalls())))
	wrongball_text.message(str(getWrongBalls()))
	
	del wait_time
	del wait_trials
	#TODO varonupdate2.setEnabled(viz.ON)
	#varonupdate2.setEnabled(viz.OFF)
	yield waitForSpace()
	yield prepareForNextBlock()
	viztask.returnValue('BlockEnd *******************************************************************\n')

##
# Executes a trial with type A.
# \brief Typ A: Experimentee gets on the startplane, the \ref ball appears at the start shelf. When the experimentee
# tries to grab the ball, but it starts moving.\n
#
# \brief Start position of ball is always
# in the middle of a rack. Parameter <b>b</b> is snippet of the actual trial. The function is expecting
# definitions for position of the startplane and for \ref ball, where it appears on the startshelf (which rack) and where to
# place it (which placement rack on destination shelf). Example content of variable <b>b</b>:\n
# \code{.py}
#						'Startplane' : [0.0,0.0],
#						'Ball' : {'Rack': 2, 'Destination': 'ShelfB', 'Placement': 2},
#						'Sensorsize': 0.25
# \endcode
# The trials ends if the velocity of the ball is near zero. See \ref isVelocityZero.
# \param b: snippet of the actual trial / snippet of the dictionary
# \see ball, placement, varPlacementDim, manager4, actionevent, audio2, sensorarray
# \see doTypeB, doTypeC, doTypeD, putPlacementOnRackNr, putBallOnRackNr, calculateTrial, inStartSensor, getCUSTOM, isVelocityZero, getvarTrialAchievement, setDestination, setSensorSize, addInteraction, addSoundSensor
# \see Placementobject.py, Ballobject.py
def doTypeA(b):
	global ball
	global varTrialAchievement
	global manager2
	global manager4
	global actionevent
	#global audio2
	global sensorarray
	global firstRunInstructionMovement
	global varKoerpergroesse
	global torus
	global torusSensor
	
	#setStartpointpassed('BallMovement')
#	if firstRunInstruction:
#		showInstructions()
#	else:
#		pass
	assert('Type' not in b)

	viz.logNotice('doTypeA **********************************************************************')
	yield messageStartEnd('TypeA')

	x,z = b['Startplane']
	del b['Startplane']

	yield placefootplane()
	yield placeViapoint(x-varKoerpergroesse['Armlaenge']/1.9, z+0.3)
	yield addStartSensor()
	#yield failOverTheEdge()
	
	#yield showPlane(x-0.7, z+0.305)
	
#	if getfirstRunInstruction():
#		print '##############################################'
#		yield showInstructions()
#	else:
#		pass
	if getfirstRunInstructionMovement():
		print '##############################################'
		yield showMoveInstruction()
	else:
		pass
	
	wait_trialAchivement = viztask.waitTrue(lambda: getvarTrialAchievement())
	wait_true = viztask.waitTrue(lambda: inStartSensor())
	wait_true2 = viztask.waitTrue(lambda: getCUSTOM())
	wait_true3 = viztask.waitTrue(lambda: failOverTheEdge())

	data = yield viztask.waitAny([wait_true, wait_true2, wait_trialAchivement, wait_true3])

	if (data.condition is not wait_trialAchivement):
		setCUSTOM(False)
		#audio2.play()
		print "sensorarray "
		print sensorarray
		sensorarray.remove(sensorarray[0])
		print sensorarray
		print "data.condition = " + str(data.condition)

		writeCSVfile("data.condition = " + str(data.condition))
		sensorsize = b['Sensorsize']
		balldef = b['Ball']

		del b['Sensorsize']
		del b['Ball']

		yield setSensorSize(sensorsize)
		yield setDestination(balldef['Destination'])
		temp_shelf = getShelf(balldef['Destination'])
		shelfcolor, shelfcolorambient, shelfcoloremissive = temp_shelf.getShelfColor()
		#ball = Ballobject(np.subtract(shelfcolor, [0.1, 0.1, 0.1]).tolist(), shelfcolorambient, shelfcoloremissive)
		ball = Ballobject([1, 1, 1], [1, 1, 1], [1, 1, 1])
		
		#torusSensor = vizproximity.Sensor( vizproximity.Box([0,1.1,1.1]), torus )

		del shelfcolor
		del shelfcolorambient
		del shelfcoloremissive
		del temp_shelf

		yield addInteraction(1, ball, 'ballMove', sensorsize, moveTheBall)

		del sensorsize

		yield putBallOnRackNr2(balldef)
		yield addFailSensor()
		#yield failOverTheEdge()
	
		print(ball.getBallPosition)
		
		yield addBallSensor()

		del balldef

		wait_exit = viztask.waitTrue(lambda: waitForExitTheViapoint())
		data = yield viztask.waitAny([wait_exit, wait_trialAchivement])

		if (data.condition is not wait_trialAchivement):
			torus = vizshape.addTorus(radius=0.33, tubeRadius=0.01, sides=40, slices=40, axis=vizshape.AXIS_X)
			torusSensor = vizproximity.Sensor( vizproximity.Sphere(radius = 0.33), torus )
			torus.setPosition([5,3,0])
			yield addSoundSensor(x,z)
			wait_action = viztask.waitActionEnd(ball.getNode(), actionevent)
			data = yield viztask.waitAny([wait_action, wait_trialAchivement])
		

			if (data.condition is wait_action):
				yield writeCSVfile('ball has been moved') 
				viz.logNotice('ball has been moved at {0}'.format(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]))
				
			else:
				pass
				
			#yield viztask.waitTrue(lambda: getvarTrialAchievement())
			 
			data = yield viztask.waitAny([wait_trialAchivement, wait_true3])
			del wait_action
		else:
			pass

		print "Start waiting for velocity..."
		yield viztask.waitTrue(lambda: getBallVelocity()<[2,1,1] or viapointpassed or overTheEdge )
		#yield viztask.waitTrue(lambda: isVelocityZero() or viapointpassed)
		yield calculateTrial()
		print "velocity: ball is not moving anymore"

		del wait_exit
	else:
		pass

	yield messageStartEnd('TypeA', False)
	viztask.returnValue('******************************************************************************')

	del x
	del z
	del data
	del wait_trialAchivement
	del wait_event
	del wait_true


##
# Executes a trial with type C.
# \brief Typ C: Experimentee gets on the startplane, the ball appears at the start shelf. The experimentee
# transports the ball to the destination place. Normal environment.\n
#
# For more details please see \ref doTypeA.
# \param b: snippet of the actual trial.
# \see ball, placement, varPlacementDim, varTrialAchievement, manager4, audio2, sensorarray
# \see doTypeA, doTypeC, doTypeD, putPlacementOnRackNr, putBallOnRackNr, calculateTrial, isVelocityZero
def doTypeB(b):
	global ball
	global varTrialAchievement
	global manager4
	#global audio2
	global sensorarray
	global firstRunInstruction
	global torus
	global torusSensor

	assert('Type' not in b)

	viz.logNotice('doTypeB **********************************************************************')
	yield messageStartEnd('TypeB')

	x,z = b['Startplane']
	del b['Startplane']

	if getfirstRunInstruction():
		print '##############################################'
		yield showInstructions()
	else:
		pass
		
	yield placefootplane()	
	yield placeViapoint(x-varKoerpergroesse['Armlaenge']/1.9, z+0.3)
	yield addStartSensor()
	#yield failOverTheEdge()

	
	#yield showPlane(x-0.7, z+0.305)

	wait_trialAchivement = viztask.waitTrue(lambda: getvarTrialAchievement())
	wait_true = viztask.waitTrue(lambda: inStartSensor())
	wait_true2 = viztask.waitTrue(lambda: getCUSTOM())


	#data = yield viztask.waitAny([wait_event, wait_true, wait_trialAchivement])
	data = yield viztask.waitAny([wait_true, wait_true2, wait_trialAchivement])
	#data = yield viztask.waitAny([wait_event, wait_trialAchivement])
	#print wait_event,
	#print wait_true
	#manager4.clearSensors()

	if (data.condition is not wait_trialAchivement):
		setCUSTOM(False)
#		audio2.play()
		sensorarray.remove(sensorarray[0])
		print "data.condition = " +str(data.condition)
		writeCSVfile("data.condition = " +str(data.condition))
		sensorsize = b['Sensorsize']
		del b['Sensorsize']
		balldef = b['Ball']
		del b['Ball']

		yield setSensorSize(sensorsize)
		yield setDestination(balldef['Destination'])
		temp_shelf = getShelf(balldef['Destination'])
		shelfcolor, shelfcolorambient, shelfcoloremissive = temp_shelf.getShelfColor()
		#ball = Ballobject(np.subtract(shelfcolor, [0.1, 0.1, 0.1]).tolist(), shelfcolorambient, shelfcoloremissive)
		ball = Ballobject([1, 1, 1], [1, 1, 1], [1, 1, 1])
		del shelfcolor
		del shelfcolorambient
		del shelfcoloremissive
		del temp_shelf

		yield putBallOnRackNr2(balldef)
		yield addFailSensor()
		yield failOverTheEdge()
		
		
		
		print(ball.getBallPosition)
		yield addBallSensor()
		
		del balldef

		wait_exit = viztask.waitTrue(lambda: waitForExitTheViapoint())

		data = yield viztask.waitAny([wait_exit, wait_trialAchivement])

		if (data.condition is not wait_trialAchivement):
			torus = vizshape.addTorus(radius=0.33, tubeRadius=0.01, sides=40, slices=40, axis=vizshape.AXIS_X)
			torusSensor = vizproximity.Sensor( vizproximity.Sphere(radius = 0.33), torus )
			torus.setPosition([5,3,0])
			yield addSoundSensor(x,z)
			#yield viztask.waitTrue(lambda: getvarTrialAchievement())
			data = yield viztask.waitAny([wait_trialAchivement])
		else:
			pass

		print "Start waiting for velocity..."
		yield viztask.waitTrue(lambda: getBallVelocity()<[2,1,1] or viapointpassed)
		yield calculateTrial()
		print "velocity: ball is not moving anymore"

		del wait_exit
	else:
		pass

	yield messageStartEnd('TypeB', False)
	viztask.returnValue('******************************************************************************')

	del x
	del z
	del data
	del wait_true
	del wait_event
	del wait_trialAchivement
	


#def doTypeC(b):
#	global ball
#	global varTrialAchievement
#	global manager4
#	#global audio2
#	global sensorarray
#
#	assert('Type' not in b)
#
#	viz.logNotice('doTypeC **********************************************************************')
#	yield messageStartEnd('TypeC')
#
#	x,z = b['Startplane']
#	del b['Startplane']
#	
#	yield instruction1()
#	yield placeViapoint(x-0.6, z)
#	yield addStartSensor()
#	yield showPlane(x-0.7, z+0.305)
#
#	wait_trialAchivement = viztask.waitTrue(lambda: getvarTrialAchievement())
#	wait_true = viztask.waitTrue(lambda: inStartSensor())
#	wait_true2 = viztask.waitTrue(lambda: getCUSTOM())
#
#
#	#data = yield viztask.waitAny([wait_event, wait_true, wait_trialAchivement])
#	data = yield viztask.waitAny([wait_true, wait_true2, wait_trialAchivement])
#	#data = yield viztask.waitAny([wait_event, wait_trialAchivement])
#	#print wait_event,
#	#print wait_true
#	#manager4.clearSensors()
#
#	if (data.condition is not wait_trialAchivement):
#		setCUSTOM(False)
##		audio2.play()
#		sensorarray.remove(sensorarray[0])
#		print "data.condition = " +str(data.condition)
#		writeCSVfile("data.condition = " +str(data.condition))
#		sensorsize = b['Sensorsize']
#		del b['Sensorsize']
#		balldef = b['Ball']
#		del b['Ball']
#
#		yield setSensorSize(sensorsize)
#		yield setDestination(balldef['Destination'])
#		temp_shelf = getShelf(balldef['Destination'])
#		shelfcolor, shelfcolorambient, shelfcoloremissive = temp_shelf.getShelfColor()
#		ball = Ballobject(np.subtract(shelfcolor, [0.1, 0.1, 0.1]).tolist(), shelfcolorambient, shelfcoloremissive)
#
#		del shelfcolor
#		del shelfcolorambient
#		del shelfcoloremissive
#		del temp_shelf
#
#		yield putBallOnRackNr2(balldef)
#		
#		yield addBallSensor()
#
#		del balldef
#
#		wait_exit = viztask.waitTrue(lambda: waitForExitTheViapoint())
#
#		data = yield viztask.waitAny([wait_exit, wait_trialAchivement])
#
#		if (data.condition is not wait_trialAchivement):
#			yield addSoundSensor(x,z)
#			#yield viztask.waitTrue(lambda: getvarTrialAchievement())
#			data = yield viztask.waitAny([wait_trialAchivement])
#		else:
#			pass
#
#		print "Start waiting for velocity..."
#		yield viztask.waitTrue(lambda: getBallVelocity()<[5,1,1] or viapointpassed)
#		yield calculateTrial()
#		print "velocity: ball is not moving anymore"
#
#		del wait_exit
#	else:
#		pass
#
#	yield messageStartEnd('TypeB', False)
#	viztask.returnValue('******************************************************************************')
#
#	del x
#	del z
#	del data
#	del wait_true
#	del wait_event
#	del wait_trialAchivement


##
# It returns the value of \ref varKoerpergroesse2.
# \returns an integer
# \see setKoerpergroesse
def getKoerpergroesse():
	global varKoerpergroesse2
	
	return varKoerpergroesse2

##
# It sets the new value for \ref varKoerpergroesse2.
# \see varKoerpergroesse2
# \see getKoerpergroesse
def setKoerpergroesse(val):
	global varKoerpergroesse2

	varKoerpergroesse2 = val

##
# It sets the data from the participant info panel. It sets 
# \ref vpn_id and \ref varKoerpergroesse2.
# \param a: a string, the vpn
# \param arr: a string, but it only contains integers (for height)
# \param bw: bodyweight
# \param sts: shoulder-to-shoulder length
# \param ual: upper arm length
# \param fal: fore arm length
# \see varKoerpergroesse2, vpn_id, varBodyweight, varShoulderToShoulderLength, varUpperArmLength, varForeArmLength
# \see setVPNid, setKoerpergroesse, setBodyweight, setShoulderToShoulderLength, setUpperArmLength, setForeArmLength
def setData(a, arr, bw, sts, ual, fal):
	setVPNid(a.get())
	temp = arr.get()
	setBodyweight(bw.get())
	setShoulderToShoulderLength(sts.get())
	setUpperArmLength(ual.get())
	setForeArmLength(fal.get())
	
	
	if (temp.isdigit()):
		setKoerpergroesse(float(temp)/100.0)
	else:
		setKoerpergroesse(1.0)
		assert(temp.isdigit()), "Please just enter digits in the textbox 'bodyheight'."
		viz.quit()
		
	del temp

##
# It makes some preparations:
# It calculates the bodymeasures (calls \ref participantInfo) and sets up the timers \ref varonupdate, \ref varonupdate2 and \ref occlusionupdater. Only \ref varonupdate2 
# is left enabled.
# It also calls \ref writeTransformationMatrix and sets the eyeheight of the mainview.
# \see handleBlock, shelfA, shelfB, shelfC, shelfD, varKoerpergroesse, varKoerpergroesse2, view, varonupdate, varonupdate2, occlusionupdater, participantInfo, notinthevrlab
# \see writeTransformationMatrix, getKoerpergroesse, KP.calculateKP
def init():
	global varKoerpergroesse
	global varKoerpergroesse2
	global view
	global varonupdate
	global varonupdate2
	global participantInfo
	global occlusionupdater
	global notinthevrlab
	
	# Opens a dialog-gui for entering bodysize and vp-id
	yield viztask.waitTrue(lambda: getKoerpergroesse() > 0.0)
	participantInfo.remove()
	varKoerpergroesse = KP.calculateKP(varKoerpergroesse2)

	if (notinthevrlab):
		view = viz.MainView
		view.eyeheight(varKoerpergroesse['Koerpergroesse'])
	else:
		pass

	yield writeTransformationMatrix()

	viz.callback(viz.KEYDOWN_EVENT, onKeyDown)

	#varonupdate      = vizact.ontimer(0.04166, writeCSVfile, '') #24Hz
	varonupdate      = vizact.ontimer(0.0166666666666666666666666666667, writeCSVfile, '') #60Hz
	#varonupdate2     = vizact.ontimer(0.0166666666666666666666666666667, writeSuitData) #60Hz

	
	varonupdate.setEnabled(viz.OFF)
#	varonupdate2.setEnabled(viz.ON)


	viz.logNotice('******************************************************************************')
	viz.logNotice('******************************************************************************\n')

def test(e):
	global controllersteam
#	print "ungrabbed by controller"
#	print controllersteam
	i = controllersteam.getTrigger()
	print i

viz.callback(viz.SENSOR_DOWN_EVENT, grabEvent)
viz.callback(viz.SENSOR_UP_EVENT, releaseTheBall)

#viz.callback(viz.SENSOR_DOWN_EVENT, goOn, priority=-50)

#def RemoveInstructions(e):
#	if e.button == steamvr.BUTTON_TRACKPAD_TOUCH:
#		setFirstRunInstruction(False)
		

##set velocity for the ball object
def onRelease(e):
	print "onRelease: ",
	print e.released
	e.released.setVelocity([x * 4 for x in e.released.getVelocity()])
	
viz.callback(grabber.RELEASE_EVENT, onRelease)

##
# Controls the scheduler.
# \c vardict from Versuchsszenario.py will be used.
# The <code>filename = vpn_id+"_"+str(getBlock())+"_log.csv"</code>
# is set.
# \see vardict
# \see init, handleDict, getBlock, setBlock, getVPNid, validation
# \see Versuchsszenario.py
def myTaskSchedule(args=[]):
	global vardict

	yield init()

	viz.logNotice("Experiment: "+str(vardict))
	viz.logNotice("Please press <n> for start.")

	filename = getVPNid()+"_"+str(getBlock())+"_log.csv"

	while (fileExists(filename)):
		print("Already exists... ", filename)
		del vardict['Block'+str(getBlock())]
		setBlock(getBlock()+1)
		filename = getVPNid()+"_"+str(getBlock())+"_log.csv"

	#TODO raus?
	filename = getVPNid()+"_"+str(getBlock())+"_log.csv"
	
	#yield showInstruction()

	if (getBlock() != 1):
		

		yield viztask.waitKeyDown('n')
		viz.logNotice('{0} Blocks detected.'.format(len(vardict)))
		yield handleDict(vardict)
	else:
		#TODO back to False
		
		
		yield viztask.waitKeyDown('n')
		writeCSVfile("Starting with Block Number 1.")
		viz.logNotice('{0} Blocks detected.'.format(len(vardict)))
		yield handleDict(vardict)

	viz.logNotice("Finished.###################################################################")
	viz.logNotice("############################################################################")
	viz.logNotice("############################################################################")
	viz.logNotice("############################################################################")
	viz.logNotice("############################################################################")

# needs to be here
vizact.onbuttondown(submitButton, setData, textbox_id, textbox_kp, textbox_bw, textbox_sts, textbox_ual, textbox_fal)





