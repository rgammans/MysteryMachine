#!/usr/bin/env python
#   			logpanel.py - Copyright Roger Gammans 
# 
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#

"""
Provides a display panel for logging messages.
"""

import logging
import sys
import wx

class loggingHandler(logging.Handler):
    def __init__(self,):
        logging.Handler.__init__(self)
        self.level = 0

    def emit(self,msg):
        print msg,msg.levelname,msg.levelno
        if msg.levelno <= logging.DEBUG:
            wx.LogDebug(str(msg))
        elif msg.levelno <= logging.INFO:
            wx.LogInfo(str(msg))
        elif msg.levelno <= logging.WARNING:
            wx.LogWarning(str(msg))
        elif msg.levelno <= logging.ERROR:
            wx.LogWarning(str(msg))
        else: 
            wx.LogError(str(msg))
            wx.MessageBox("Critical Error",str(msg),wx.OK | wx.ICON_ERROR)


class LogPanel(wx.PyPanel):
    def __init__(self,parent):
        super(LogPanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(0,0))
        self.buildUi()
        self.Layout()
        self.SetAutoLayout(True)
        wx.Log.SetActiveTarget(self.logger)
        logging.getLogger('').addHandler(loggingHandler())


    def buildUi(self):
        box_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        log_message_ctrl = wx.TextCtrl(self,wx.NewId(), style = wx.TE_MULTILINE )
        self.logger  =wx.LogTextCtrl(log_message_ctrl)

        box_sizer.Add( log_message_ctrl)
        self.SetSizer(box_sizer)
        self.Fit()

        #self.Bind(wx.EVT_CLOSE, self._on_close)



##We define this here to keep all the logging stuff together in
# one place.
def  log_exceptions(level =logging.INFO, debug_tb = False, logger = "MysteryMachine.Ui.wx.CaughtExceptions"):
    """This function returns a decorator which catches exceptions
    produced by the wrapped function and sends them to the 
    logging systems at the specified log level.

    If debug_tb is true the traceback is also logged at the
    debug severity level"""
    def decorator(func):
        logger_obj = logging.getLogger(logger)
        def wrapper(*args,**kwargs):
            try:
                return func(*args,**kwargs)
            except:
                c, e, tb =sys.exc_info()
                logger_obj.log(level,str(e))
                print str(e)
                if debug_tb:
                    import traceback
                    for line in traceback.format_tb(tb):
                        logger_obj.log(logging.DEBUG,line)

        wrapper.__name__ = func.__name__
        wrapper.__doc__  = func.__doc__
        return wrapper
    return decorator


