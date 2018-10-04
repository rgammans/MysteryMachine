"""
A simple but identifiable plugin which can be used to test the plugin
infra stucture.
"""

from MysteryMachine.Extension  import Extension
import logging

class Second(Extension):
	def __init__(self):
		self.logger = logging.getLogger("MysteryMachine.Extensions.Second")
		Extension.__init__(self)

	def activate(self):
		self.logger.debug( "Second activated")

	def deactivated(self):
		self.logger.debug( "Second Deactivated")
