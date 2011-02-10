#!/usr/bin/env python
#   			objectpanel.py - Copyright Roger Gammans 
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
Provides an editor pane for objects
"""

import wx
import wx.lib.scrolledpanel as sp

from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMSystem import MMSystem

from attribute_controls import *

Ui_Id = wx.ID_HIGHEST
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 


class ObjectPanel(sp.ScrolledPanel):
    def __init__(self,parent,obj):
        super(ObjectPanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(200,400))
        self.obj = obj
        self.buildUi()
        parent.FitInside()
        self.TransferDataToWindow()
        self.Layout()


    def getPanelName(self):
        return repr(self.obj)

    def buildUi(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.title = wx.StaticText(self,ID_LABEL)
        self.title.SetLabel(repr(self.obj) +" - \"" +str(self.obj)+"\"") 
        self.sizer.Add(self.title,0)

        #Walk down the inheritance hierachy Finding each object.
        current = self.obj
        done = []
        while current is not None:
            print repr(current)
            panel, included  = self._buildObjectPanel(current,done)
            #Skip parent's from which nothing is inherited..
            if included:
                self.sizer.Add(panel,0)
                done += included
            else:
                panel.Show(False)
                panel.Destroy()
            current = current.get_parent()



    def _buildObjectPanel(self,obj,ignore_list):
        """
        This builds a panel of attribute widget for obj , but excludes any attribute in 
        the ignore list.
        Returns tuple(panel , [ list of included attributes ])
        """
        included = []
        box = wx.StaticBox(self,-1, label = str(obj))
        sizer = wx.StaticBoxSizer(box,wx.VERTICAL)
        for attr in obj:
            #Skip if in ignore list..
            if attr.name in ignore_list: continue 
            included += [ attr.name ]
            label = wx.StaticText(self,-1,label = attr.name)
            sizer.Add(label)
            sizer.Add(GetWidgetFor(attr,parent = self))
        return sizer , included
