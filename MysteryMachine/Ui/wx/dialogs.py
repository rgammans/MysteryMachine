#!/usr/bin/env python
#   			widgets.py - Copyright %author%
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
#

"""
Provides an implementation of common dialoos.
""" 


import wx
import wx.lib.newevent

import MysteryMachine
from MysteryMachine.schema.MMSystem import MMSystem
from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMObject import MMObject

import widgets



ObjectPickedCommandEvent, EVT_OBJECTPICKED_EVENT = wx.lib.newevent.NewCommandEvent()



def _apply_default(name,default,kwargs):
    if name not in kwargs: kwargs[name] = default

def _get_argument(name,kwargs):
    rv = kwargs.get(name)
    if name in kwargs: del kwargs[name]
    return rv


class ObjectPicker(wx.Dialog):
    def __init__(self,parent,id,*args,**kwargs):
        self.system = _get_argument('system',kwargs)
        self.action = _get_argument('action',kwargs)

        _apply_default('size',(400,400),kwargs)
        super(ObjectPicker,self).__init__(parent,id,**kwargs)

        self.BuildUi()
        self.value = None

    def GetObject(self):
        return self.value

    def BuildUi(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.tree = widgets.MMTreeView(self,wx.ID_ANY,system = self.system, size =(0,0))
 
        self.Sizer.Add(self.tree,1,wx.EXPAND)
        
        sizer2=wx.StdDialogButtonSizer()
        sizer2.Add(wx.Button(self,wx.ID_OK,"OK"))
        sizer2.Add(wx.Button(self,wx.ID_CANCEL,"Cancel"))

        self.sizer.Add(sizer2)
        #self.sizer.Fit(self) 

        wx.EVT_BUTTON(self,wx.ID_OK,self.onOK)
        wx.EVT_BUTTON(self,wx.ID_CANCEL,self.onCancel)
        self.Show()
        self.SetAutoLayout(True)

 
    def onOK(self,event):
        value_id = self.tree.GetSelection()
        self.value=self.tree.GetItemData(value_id).GetData()
        self.Close()
        self.action(self.value)
        self.Destroy()


    def onCancel(self,event):
        self.Close()
        self.Destroy()

