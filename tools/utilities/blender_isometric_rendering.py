#!BPY
# -*- coding: utf-8 -*-
# ###################################################
# Copyright (C) 2008-2010 The Zero-Projekt team
# http://zero-projekt.net
# info@zero-projekt.net
# This file is part of Zero "Was vom Morgen blieb"
#
# The Zero-Projekt codebase is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

#"""
#Name: 'ZAR v. 0.95'
#Blender:248
#Group: 'Render'
#Tooltip: 'Rotates & renders characters including XML file creation for FIFE'
#"""

__author__ = "Chewie based on Shadowrunner's ZAR based on ZAR by Giselher"
__version__ = "0.95"
__bpydoc__ = """\
Automated Render and Rotation Script
"""

import os, sys, os, glob
import Blender, string
from Blender import *
from Blender.Scene import Render
from Blender.sys import time
import Blender.Mathutils
import bpy

# constants for xml creation
_DEFAULT_NAMESPACE = "http://zp.net/"
_DEFAULT_DIRECTIONS = [0, 120, 150, 180, 300, 330]
_DEFAULT_FILENAME = 'animation.xml'
_DEFAULT_ANIMATION_START_TAG = '<animation delay="%d" namespace="%s" id="%s" x_offset="%d" y_offset="%d">'
_DEFAULT_FRAME_TAG = '\t<frame source="%s" />'
_DEFAULT_ANIMATION_END_TAG = '</animation>'

# default values gui
DEFAULT_X_OFFSET = 0
DEFAULT_Y_OFFSET = -25
DEFAULT_DELAY = 40
DEFAULT_OBJID = "idle:"
DEFAULT_NAMESPACE = "agents"

# bounderies
# NOTE: MAX_STRING_LENGTH is a blender value - it can't be higher then 399!
MAX_STRING_LENGTH = 399
# feel free to alter these, though (in a way that makes sense)
MIN_OFFSET = -200
MAX_OFFSET = 200
MIN_DELAY = 0
MAX_DELAY = 500

# don't touch this!
EV_btn_OK = 0
EV_btn_Chancel = 1
EV_num_X_OFFSET = 2
EV_num_Y_OFFSET = 3
EV_num_DELAY = 4
EV_btn_OBJID = 5
EV_btn_NAMESPACE = 6

class ZARGui(object):
	""" """
	def __init__(self):
		super(ZARGui, self).__init__()
		# gui layout (7 lines, each 25px high)
		self.layout = list(25 * i + 5 for i in range(7))

		self.data = {
			'id' : DEFAULT_OBJID,
			'ns' : DEFAULT_NAMESPACE,
			'delay': DEFAULT_DELAY,
			'x_offset' : DEFAULT_X_OFFSET,
			'y_offset' : DEFAULT_Y_OFFSET,		
		}
	
		self.ok_btn = Draw.Create("Render")
		self.chancel_btn = Draw.Create("Chancel")
		self.x_offset_btn = Draw.Create(DEFAULT_X_OFFSET)
		self.y_offset_btn = Draw.Create(DEFAULT_Y_OFFSET)
		self.delay_btn = Draw.Create(DEFAULT_DELAY)
		self.objid_btn = Draw.Create(DEFAULT_OBJID)
		self.namespace_btn = Draw.Create(DEFAULT_NAMESPACE)
	
		Draw.Register(self.draw, self.event, self.button_event)
		
	def draw(self):
		"""	
		Number(name, event, x, y, width, height, initial, min, max, tooltip, callback) 
		PushButton(name, event, x, y, width, height, tooltip, callback) 
		String(name, event, x, y, width, height, initial, length, tooltip, callback) 
		"""
		# loop through the layout 
		for line in self.layout:
			BGL.glRasterPos2i(5, line)
			
		self.ok_btn = Draw.PushButton("Render", EV_btn_OK, 5, 5, 60, 20, "Start rendering process")
		self.chancel_btn = Draw.PushButton("Chancel", EV_btn_Chancel, 80, 5, 60, 20, "Yet another chancel button")		
		self.y_offset_btn = Draw.Number("y offset: ", EV_num_Y_OFFSET, 5, 30, 300, 20, self.y_offset_btn.val, MIN_OFFSET, MAX_OFFSET, "y offset of the whole animation")
		self.x_offset_btn = Draw.Number("x offset: ", EV_num_X_OFFSET, 5, 55, 300, 20, self.x_offset_btn.val, MIN_OFFSET, MAX_OFFSET, "x offset of the whole animation")
		self.delay_btn = Draw.Number("delay (ms): ", EV_num_DELAY, 5, 80, 300, 20, self.delay_btn.val, MIN_DELAY, MAX_DELAY, "Delay between all frames")
		self.objid_btn = Draw.String("object id: ", EV_btn_OBJID, 5, 105, 300, 20, self.objid_btn.val, MAX_STRING_LENGTH, "The id of the object, e.g. 'idle:'")
		self.namespace_btn = Draw.String("Namespace: ", EV_btn_NAMESPACE, 5, 130, 300, 20, self.namespace_btn.val, MAX_STRING_LENGTH, "Enter the namespace, e.g. 'agents'")
		
	def event(self, event, val):
		""" """
		return
	
	def button_event(self, event):
		""" """
		if event == EV_btn_OBJID:
			self.data['id'] = self.objid_btn.val
			return
		if event == EV_btn_NAMESPACE:
			self.data['ns'] = self.namespace_btn.val
			return
		if event == EV_num_X_OFFSET:
			self.data['x_offset'] = self.x_offset_btn.val
			return
		if event == EV_num_Y_OFFSET:
			self.data['y_offset'] = self.y_offset_btn.val
			return
		if event == EV_num_DELAY:
			self.data['delay'] = self.delay_btn.val
			return

		if event == EV_btn_OK:
			self.process_input()
			
#			print "Object attributes: "
#			print "x: ", self.x_offset_btn.val
#			print "y: ", self.y_offset_btn.val
#			print "id: ", self.objid_btn.val
#			print "ns: ", self.namespace_btn.val
#			print "delay: ", self.delay_btn.val
		
		if event == EV_btn_Chancel:
			Draw.Exit()
			
	def process_input(self):
		""" use the given data from the gui and start
			
			- render process
			- XML file creation
		"""
		animrender = AnimRotationRenderer()
		animrender.run()

		#create xml files:
		render_dir = Blender.Get("renderdir")
		
		xmlwriter = XMLAnimationCreator(**self.data)
		xmlwriter.set_base_path(render_dir)
		xmlwriter.run()

class XMLAnimationCreator(object):
	""" The B{XMLAnimationCreator} walks through an action directory and generates
	animation.xml files for all available *.png frames of a direction.
	
	The direction is given by the folder name (e.g. "0" -> direction 0 degree)
	
	@type	namespace:	string
	@ivar	namespace:	the namespace of the object - typically an url
	@type	delay:		int
	@ivar	delay:		the delay for frames in ms
	@type	id:			string
	@ivar	id:			a concatenated string, made out of object id, action and direction, e.g. "boar001:idle:0"
	@type	offset:		dict
	@ivar	offset:		contains the x and y offset the animation should have (current usage: animation tag, not frame tag)	
	"""
	def __init__(self, **kwargs):
		super(XMLAnimationCreator, self).__init__()
		
		self.base_path = "Output/"
		
		self.namespace = None
		self.delay = None
		self.id_base = None
		self.id = None
		
		self.offset = {
			'x'	: DEFAULT_X_OFFSET,
			'y'	: DEFAULT_Y_OFFSET
		}

		self.validate(kwargs)
		
	def set_base_path(self, path):
		""" """
		self.base_path = path + self.base_path
		
	def validate(self, kwargs):
		""" check the given arguments and / or set default values if necessary """
		if not kwargs.has_key("ns"):
			if kwargs.has_key("namespace"):
				self.namespace = _DEFAULT_NAMESPACE + kwargs["namespace"]
			else:
				self.namespace = DEFAULT_NAMESPACE
		else:
			self.namespace = _DEFAULT_NAMESPACE + str(kwargs["ns"])
			
		if not kwargs.has_key("delay"):
			self.delay = DEFAULT_FRAME_DELAY
		else:
			self.delay = int(kwargs["delay"])
			
		if kwargs.has_key("x_offset"):
			self.offset['x'] = int(kwargs['x_offset'])

		if kwargs.has_key("y_offset"):
			self.offset['y'] = int(kwargs['y_offset'])
			
		if not kwargs.has_key("id"):
			raise Exception("We need the id of an action!")
		else:
			self.id_base = str(kwargs["id"])
			
	def set_id(self, direction):
		""" generate an id for the current direction (= directory name)
			
		@type	direction:	int
		@param	direction:	the current direction (e.g. 0, 120 ...)
		"""
		self.id = self.id_base + str(direction)

	def set_files(self, direction):
		""" get all *.png files of the current direction dir and set the ivar accordingly
		
		@type	direction:	int
		@param	direction:	the current direction (e.g. 0, 120 ...)		
		"""
		path = self.base_path + str(direction) + os.path.sep
		files = glob.glob(path + '*.png')
		
		self.files = []
		
		for file in files:
			pieces = file.split(os.path.sep)
			index = len(pieces)-1
			filename = pieces[index]			
			self.files.append(filename)
		
		self.files.sort()
			
		
	def create_XML(self, direction):
		""" run through all files in a direction dir and create a list with the XML
		
		@type	direction:	int
		@param	direction:	the current direction (e.g. 0, 120 ...)
		"""
		output_lst = []
		
		output_lst.append(_DEFAULT_ANIMATION_START_TAG % (float(self.delay), str(self.namespace), str(self.id), self.offset['x'], self.offset['y']))
		
		for file in self.files:

			output_lst.append(_DEFAULT_FRAME_TAG % str(file))
		
		output_lst.append(_DEFAULT_ANIMATION_END_TAG)
		
		self.write_file(direction, output_lst)
		
	def write_file(self, direction, content):
		"""

		@type	direction:	int
		@param	direction:	the current direction (e.g. 0, 120 ...)
		@type	content:	list
		@param	content:	the XML output we want to write to the animation file		
		"""
		filename = _DEFAULT_FILENAME
		path = self.base_path + str(direction) + os.path.sep + filename
		
		try:
			os.remove(path)
		except:
			pass
		
		file = open(path, 'a')
		
		for line in content:
			file.write(line)
			file.write('\n')
		file.close()	

	def run(self):
		""" iterate through all available directions and create the XML files """
		for direction in _DEFAULT_DIRECTIONS:
			print "Creating XML file for direction %d ..." % direction
			self.set_id(direction)
			self.set_files(direction)
			self.create_XML(direction)
			print "\t done."

# 08-01-09, chewie: added tranlation table for angles, fixed for loop with range()

class AnimRotationRenderer(object):
	def __init__(self):
		super(AnimRotationRenderer, self).__init__()
		self.scene = Scene.GetCurrent()
		self.context = self.scene.getRenderingContext()
		self.context.sFrame = Blender.Get('staframe') # Startframe
		self.context.eFrame = Blender.Get('endframe') # Endframe

		self.context.extensions = True 
#		self.scene.getCurrentCamera
		self.empty_object = "Empty"
		
		self.axis = (0, 0, 1) # rotation axis (x,z,y)
		
		self.armature = None
		self.rotation_object = None

		self.endframes = {
			'rat:idle'	: 1,
			'rat:attack'	: 15,
			'rat:kill01'	: 10,

			'itemless_walk'	:	24,
			'itemless_run'	:	24,
			'itemless_idle'	:	5,			
			'itemless_punch':	20,
			'itemless_kick'	:	23,		
			'itemless_combo':	23,		
			'itemless_hit01'	:	20,
			'itemless_death01'	:	23,		
			'itemless_use'	:	27,

			'hannes_shotgun_idle'	: 5,
			'hannes_shotgun_shot' 	: 37,
			'hannes_punch' 		: 32,
			'hannes_punch2'		: 32,
			'hannes_walk'		: 25,
			'hannes_G33_walk'	: 25,
			'hannes_G33_punch' 	: 32,

			'revolver_walk'	:	24,
			'revolver_run'	:	24,
			'revolver_idle'	:	5,			
			'revolver_punch':	20,					
			'revolver_shot'	:	20,		
			'revolver_reload':	65,		
			'revolver_hit01'	:	20,
			'revolver_death01'	:	23,		
					
			'G33_walk'	:	24,
			'G33_run'	:	24,
			'G33_idle'	:	5,			
			'G33_punch':	20,					
			'G33_shot'	:	20,		
			'G33_burst'	:	24,	
			'G33_reload':	64,		
			'G33_hit01'	:	20,
			'G33_death01'	:	23,	
			
			'zombie_walk'	: 24,
			'zombie_run'	: 25,
			'zombie_punch'	: 25,
			'zombie_punch2'	: 30,
			'zombie_kill1'	: 29,
			'zombie_kill2'	: 52,
			'zombie_idle'	: 5,
			'zombie_idle2'	: 28,
			'zombie_idle3'	: 40,
			'zombie_hit1'	: 20,
		}

		self.get_objects()	
		self.set_end_frame()
		self.set_layers()
	
	def set_layers(self):
		"""
		
		"""
		pass		
		
	def set_end_frame(self):
		""" set the end frame according to the selected action 
		
		NOTE:
			set_objects only searches for one Armature
			if there are more Armature objects, this one will 
			not work (e.g. the wrong amount of frames will be rendered)
		"""	
		if self.armature is None:
			return
		
		action = self.armature.getAction().getName()
		if self.endframes.has_key(action):
			self.context.eFrame = self.endframes[action]
		else:
			raise "Can't find endframe for given action %s" % action

	def get_objects(self):
		""" fetch the rotation object (default: empty with the name "Empty") 
			and the armature		
		"""
		all_meshes = self.scene.objects
		for mesh in all_meshes:
			if mesh.getAction() is not None and self.armature is None:
				self.armature = mesh
				continue
			if mesh.name != self.empty_object:
				continue
			self.rotation_object = mesh
			
		if self.rotation_object is None:
			raise "No mesh with the name %s found" % self.empty_object	

	def render(self, dir):
		""" """
#		print "%i to %s" % (dir, self.dir_table[str(dir)])
#		dir = self.dir_table[str(dir)]
		dir = str(dir)
		self.context.renderPath = "//Output/"+dir+"/" # creats a folder called output and subdirs 
		self.context.renderAnim()

	def rotate(self, degrees):
		""" """
		if self.rotation_object is None:
			raise "No rotation object available!"
			
		# construct desired quat to rotate around given axis and angle
		desiredQuat = Mathutils.Quaternion(self.axis, degrees)
		desiredMatrix = desiredQuat.toMatrix()
		finalRotation = desiredMatrix.resize4x4() * self.rotation_object.getMatrix("worldspace")
		self.rotation_object.setMatrix(finalRotation)
#		self.rotation_object.setLocation(self.rotation_object.getLocation()) # Without this, it doesn't seem to update its children
		Blender.Redraw()
		
	def run(self):
		""" Don't ask, just do it:
		
			rot	120	30	30	120	30	30
			dir	0	120	150	180	300	330	
		
		
		"""
		# blender initial rotation on file loading
		d = 0
		# fife angle
		f = 330
		
		d = 30
		
		self.rotate(d)
		self.render(f)
		
		d = 75
		f = 0
		
		self.rotate(d)
		self.render(f)
		
		d = 45
		f = 120
		
		self.rotate(d)
		self.render(f)
		
		d = 60
		f = 150
		
		self.rotate(d)
		self.render(f)

		d = 65
		f = 180
		
		self.rotate(d)
		self.render(f)
		
		d = 55
		f = 300
		
		self.rotate(d)
		self.render(f)
		
		# restore initial rotation:
		d = 30
		
		self.rotate(d)
		
		Blender.Redraw()
	
# "correct" rotation scheme, but not suitable for FIFE yet
#		self.rotate(120)
#		self.render(0)
		
#		self.rotate(30)
#		self.render(120)
		
#		self.rotate(30)
#		self.render(150)
		
#		self.rotate(120)
#		self.render(180)

#		self.rotate(30)
#		self.render(300)
		
#		self.rotate(30)
#		self.render(330)
		
if __name__ == "__main__":
	gui = ZARGui()
