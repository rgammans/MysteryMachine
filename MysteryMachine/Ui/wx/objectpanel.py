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
import  wx.lib.scrolledpanel as scrolled


from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMSystem import MMSystem

from attribute_controls import *

Ui_Id = wx.ID_HIGHEST
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 


class ObjectPanel(scrolled.ScrolledPanel):
    def __init__(self,parent,obj):
        super(ObjectPanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(0,0))
        self.obj = obj
        self.buildUi()
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.TransferDataToWindow()
        self.Layout()
        self.SetAutoLayout(True)
        self.SetupScrolling()

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
            panel, included  = self._buildObjectPanel(current,done,self.obj)
            self.sizer.Add(panel,0,wx.EXPAND)
            done += included
            #Hide empty panel - but leave them to simply our sync algorithm
            if not included:  panel.Show(False)
            current = current.get_parent()

    def _syncUi(self):
        current = self.obj
        done = []
        for base_panel in self.GetChildren():
            if not isinstance(base_panel,_object_section): continue
            panel_obj = base_panel.get_object()
            
            if current is not panel_obj:
                #What exaclty ? Hmm.
                #This mean we're out of touch with the parent seq.
                #And we need to rewrite the sequence from here down.
                raise RuntimeError("NYI: Parent heirachy change detected")
            else:
                done_in_current =  [ ]
                for attrib_panel in base_panel.GetChildren():
                    print "P",attrib_panel
                    if not isinstance(attrib_panel,_attribute_section): continue
                    attribute = attrib_panel.attribute
                    print "C",repr(attribute), done_in_current
                    #If the attribute has been removed or overridden remove the panel.
                    if (attribute.name not in current) or (attribute.name in done):
                        base_panel.remove(attrib_panel)
                    else: done_in_current += [ attribute.name ]
                #Add panels for new attributes..
                done += done_in_current
                for attrib_obj in current:
                    print "I",repr(attrib_obj), done
                    if attrib_obj.name in done: continue
                    base_panel.add(_attribute_section(base_panel,-1,attrib_obj,self.obj))

            current = current.get_parent()

    def TransferDataToWindow(self):
        print "Op-TDTW"
        #TODO: Walk thru attributes and hide/show  overridden and new sections
        self._syncUi()
        super(ObjectPanel,self).TransferDataToWindow()
        self.Layout()

    def _buildObjectPanel(self,obj,overridden_list,top_object):
        section = _object_section(self,obj,overridden_list,top_object)
        return section, section.get_included()

class _object_section(wx.PyPanel):
    
    #def _buildObjectPanel(self,obj,overridden_list,top_object):
    def __init__(self,parent,obj,overridden_list,top_object):
        """
        This builds a panel of attribute widget for obj , but excludes any attribute in 
        the ignore list.
        Returns tuple(panel , [ list of included attributes ])
        """
        self.included = []
        self.obj = obj
        super(_object_section,self).__init__(parent,-1)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        box = wx.StaticBox(self,-1, label = str(obj))
        self.sizer = wx.StaticBoxSizer(box,wx.VERTICAL)
        self.SetSizer(self.sizer)
        for attr in obj:
            #Skip if in ignore list..
            if attr.name in overridden_list: continue 
            self.add(_attribute_section(self,-1,attr,top_object))
            


    def add(self,panel):
         self.included += [ panel.attribute.name ]
         self.sizer.Add(panel,0,wx.EXPAND)
         self.Show(True)
         self.Layout()

    def remove(self,panel):
        self.included.remove(panel.attribute.name)
        self.sizer.Remove(panel)
        panel.Show(False)
        panel.Destroy()
        if not self.included: self.Show(False)
        self.Layout()

    def get_included(self):
        return self.included

    def get_object(self):
        return self.obj

class _attribute_section(wx.PyPanel):
    ID_MYBUTTON = NewUI_ID()
    def __init__(self,parent,id,attribute,top_object):
        super(_attribute_section,self).__init__(parent,id)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.attribute = attribute
        self.top = top_object
        at_top = self.attribute.get_owner() is top_object
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        label = wx.StaticText(self,-1,label = self.attribute.name)
        headingsizer = wx.BoxSizer(wx.HORIZONTAL)
        headingsizer.Add(label)
        headingsizer.Add(wx.Button(self,self.__class__.ID_MYBUTTON,label ="Delete" if at_top else "Override"))
        wx.EVT_BUTTON(self, self.__class__.ID_MYBUTTON, self.onDelete if at_top else self.onOverride)
        sizer.Add(headingsizer)
        self.widget=GetWidgetFor(self.attribute,parent = self)
        self.widget.Enable(at_top)
        self.widget.Layout()
        sizer.Add(self.widget,0,wx.EXPAND)

    def onDelete(self,evt):
        print "on-delete"
        name = self.attribute.name
        owner =self.attribute.get_owner()
        del owner[name]
        self.GetParent().GetParent().TransferDataToWindow()


    def onOverride(self,evt):
        print "on-overrride"
        name = self.attribute.name
        self.top[name] = self.attribute
        self.GetParent().GetParent().TransferDataToWindow()
