#!/usr/bin/env python
#   			systree.py - Copyright Roger Gammans 
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
Provides a tree view of a MM attribute. 
"""

import wx
from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMSystem import MMSystem


Ui_Id = 2000
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 

ID_LABEL        = NewUI_ID()
ID_CONTENT        = NewUI_ID()

class AttributePanel(wx.Panel):
    def __init__(self,parent,attribute):
        super(AttributePanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(200,400))
        self.attribute = attribute
        self.notebook = parent.nb
        self.buildUi()
        parent.FitInside()
        self.Layout()


    def buildUi(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.title = wx.StaticText(self,ID_LABEL)
        self.title.SetLabel(repr(self.attribute)) 
        self.sizer.Add(self.title,0)

        deffont = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
        self.content  = wx.TextCtrl(self,ID_CONTENT,style = (wx.TE_MULTILINE ))
        self.sizer.Add(self.content,1,wx.EXPAND)
        self.content.SetFont(deffont)
        self.content.SetValue(str(self.attribute)) 



        self.sizer.Layout()

    def getPanelName(self):
        return repr(self.attribute)


