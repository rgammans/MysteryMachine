"""
A simple but identifiable plugin which can be used to test the plugin
infra stucture.
"""

from MysteryMachine.Extension import Extension
import logging

class First(Extension):
	def __init__(self):
		self.logger = logger.getLogger("MysteryMachine.Extensions.First")
		Extension.__init__(self)

	def activate(self):
		self.logger.debug( "First activated" )

	def deactivated(self):
		self.logger.debug( "First Deactivated" )
