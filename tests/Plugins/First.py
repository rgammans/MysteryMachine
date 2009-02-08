"""
A simple but identifiable plugin which can be used to test the plugin
infra stucture.
"""

from MysteryMachine.Extension import Extension

class First(Extension):
	def __init__(self):
		Extension.__init__(self)

	def activate(self):
		print "First activated"

	def deactivated(self):
		print "First Deactivated"
