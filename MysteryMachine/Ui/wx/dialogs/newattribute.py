#!/usr/bin/env python
#   			newattribute.py - Copyright %author%
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

import logging

import wx
import wx.lib.newevent

import MysteryMachine
from MysteryMachine.schema.MMAttribute import MMAttribute , MMUnstorableAttribute
from MysteryMachine.schema.MMAttributeValue import MakeAttributeValue
from MysteryMachine.schema.MMAttributeValue import GetAttributeTypeList
from MysteryMachine.Ui.wx.attribute_controls import GetWidgetFor

logger = logging.getLogger(__name__)

def _apply_default(name,default,kwargs):
    if name not in kwargs: kwargs[name] = default

def _get_arg(args,name,default = None):
    rv = args.get(name,default)
    if name in args:
        del args[name]
    return rv

class NewAttributeDialog(wx.Dialog):
    """This dialog get the initial values for a new attribute.

    This ask the user the type of the atribute and presents and
    appropriate widget for the user to enter the data into.
    """
    ID_CHOICE = wx.NewId()

    def __init__(self,parent,id,*args,**kwargs):
        _apply_default('size',(400,400),kwargs)
        self.parent_node   = _get_arg(kwargs,"owner")
        self.writemethod   = _get_arg(kwargs,"write",default = "set_value")
        self.name          = _get_arg(kwargs,"item",default = "")
        if self.writemethod not in ("set_value","insert","append"):
            raise ValueError("write value `%s' not known"%self.writemethod)

        super(NewAttributeDialog,self).__init__(parent,id,**kwargs)
        self.typepanels = {}
        self.current_type = None
        self.BuildUi()



    def BuildUi(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
    
        self.namefield =wx.TextCtrl(self,wx.ID_ANY)       
        self.sizer.Add(self.namefield,0,wx.EXPAND)
        self.namefield.SetValue(unicode(self.name))
        self.namefield.Show(self.writemethod == "set_value")
        
        self.typechoice = wx.Choice(self,self.__class__.ID_CHOICE,choices =sorted(GetAttributeTypeList()) )
        self.sizer.Add(self.typechoice,0,wx.EXPAND)

        wx.EVT_CHOICE(self,self.__class__.ID_CHOICE,self.onTypeChanged)

        self.panel = wx.Panel(self,wx.ID_ANY) 
        self.sizer.Add(self.panel,4,wx.EXPAND)        
        self.panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.panelsizer)
        
        sizer2=wx.StdDialogButtonSizer()
        sizer2.Add(wx.Button(self,wx.ID_OK,"OK"))
        sizer2.Add(wx.Button(self,wx.ID_CANCEL,"Cancel"))

        self.sizer.Add(sizer2,1)
        #self.sizer.Fit(self) 

        wx.EVT_BUTTON(self,wx.ID_OK,self.onOK)
        wx.EVT_BUTTON(self,wx.ID_CANCEL,self.onCancel)
        self.Show()
        self.SetAutoLayout(True)

    def onTypeChanged(self,evt):
        chosen_type = self.typechoice.GetStringSelection()
        logger.debug("type changed %s"%chosen_type)
        if chosen_type not in self.typepanels:
             tempattr = MMUnstorableAttribute(".temporary",
                                              MakeAttributeValue(chosen_type, {} ),
                                              self.parent_node)
             self.typepanels[chosen_type] = (tempattr , GetWidgetFor(tempattr,self.panel))

        if self.current_type is not None:
             self.typepanels[self.current_type][1].Show(False)

        self.current_type = chosen_type
        currentpanel = self.typepanels[self.current_type][1]
        #currentpanel.SetSize(self.panel.GetSize())
        currentpanel.Show(True)
        self.panelsizer.Remove(0)
        self.panelsizer.Add(currentpanel,0,wx.EXPAND)
        self.panel.Layout()

    def onOK(self,event):
        attribute , currentpanel = self.typepanels[self.current_type]
        attribute_name = self.namefield.GetValue()
        if self.writemethod == "set_value": self.parent_node[attribute_name] = attribute
        if self.writemethod == "append": self.parent_node.append(attribute)
        if self.writemethod == "insert": self.parent_node.insert(attribute_name,attribute)

        self.Close()
        self.Destroy()


    def onCancel(self,event):
        self.Close()
        self.Destroy()



