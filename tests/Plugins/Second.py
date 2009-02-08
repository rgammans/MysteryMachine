"""
A simple but identifiable plugin which can be used to test the plugin
infra stucture.
"""

from MysteryMachine.Extension  import Extension

class Second(Extension):
	def __init__(self):
		Extension.__init__(self)

	def activate(self):
		print "Second activated"

	def deactivated(self):
		print "Second Deactivated"
