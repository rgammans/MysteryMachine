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

from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMSystem import MMSystem

from attribute_controls import *
from widgets import NotifyClosure
import six

Ui_Id = wx.ID_HIGHEST
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 


class ObjectPanel(wx.PyPanel):
    """This is UI panel for a complete object showing all the attirbutes, 
        with a read/write sub-panel of attributes set at the top-level and readonly sub-panels of what is inherited"""

    def __init__(self,parent,obj):
        super(ObjectPanel,self).__init__(parent,-1,wx.DefaultPosition,)
        self.obj = obj
        self.buildUi()
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.TransferDataToWindow()
        self.Layout()
        self.SetAutoLayout(True)

    def getPanelName(self):
        return repr(self.obj)

    def buildUi(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.title = wx.StaticText(self,ID_LABEL)
        self.title.SetLabel(repr(self.obj) +" - \"" +six.text_type(self.obj)+"\"") 
        self.sizer.Add(self.title,0)
        self.notify = NotifyClosure(self,self.node_changed)

        self.attr_widgets_map = { }
        #Walk down the inheritance hierachy Finding each object.
        current = self.obj
        done = [ ]
        while current is not None:
            panel, included = self._buildObjectPanel(current,done,self.obj)
            self.sizer.Add(panel,0,wx.EXPAND)
            done += included.values()
            self.attr_widgets_map.update(included)
            #Hide empty panel - but leave them to simply our sync algorithm
            if not included:  panel.Show(False)
            current = current.get_parent()



    def node_changed(self,node):
        self.TransferDataToWindow()

    def _syncUi(self):
        current = self.obj
        done = set()
        for base_panel in self.GetChildren():
            if not isinstance(base_panel,_object_section): continue
            panel_obj = base_panel.get_object()

            if current is not panel_obj:
                #What exaclty ? Hmm.
                #This mean we're out of touch with the parent seq.
                #And we need to rewrite the sequence from here down.
                raise RuntimeError("NYI: Parent heirachy change detected")
            else:
                done_in_current =  set()
                for attrib_panel in base_panel.GetChildren():
                    if not isinstance(attrib_panel,_attribute_section): continue
                    attribute = attrib_panel.attribute
                    #If the attribute has been removed or overridden remove the panel.
                    if (attribute.name not in current) or (attribute.name in done):
                        base_panel.remove(attrib_panel)
                    else: done_in_current.add( attribute.name )
                #Add panels for new attributes..
                done.update( done_in_current)
                for attrib_obj in current:
                    if attrib_obj.name in done: continue
                    base_panel.add(_attribute_section(base_panel,-1,attrib_obj,self.obj))

            current = current.get_parent()

    def TransferDataToWindow(self):
        #TODO: Walk thru attributes and hide/show  overridden and new sections
        self._syncUi()
        super(ObjectPanel,self).TransferDataToWindow()
        self.Layout()

    def _buildObjectPanel(self,obj,overridden_list,top_object):
        section = _object_section(self,obj,overridden_list,top_object)
        self.notify.register(obj)
        return section, section.get_included()

class _object_section(wx.Panel):
    """This is a Ui Sub-panel , of ObjectPanel that only shows the attribute set directlt
    on the object it reflects.
    If obj and tob_obj are no thte same it is in a read-only mode.
    """

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
        box = wx.StaticBox(self, -1, label = six.text_type(obj))
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
    """This is a panel which manages an attribute. If Attr is not directly
    set in top_object it creates and override button which copies it there"""

    ID_MYBUTTON = NewUI_ID()
    def __init__(self,parent,id,attribute,top_object):
        super(_attribute_section,self).__init__(parent,id)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.attribute = attribute
        self.top = top_object
        self.at_top = parent.obj is top_object
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        label = wx.StaticText(self,-1,label = self.attribute.name)
        headingsizer = wx.BoxSizer(wx.HORIZONTAL)
        headingsizer.Add(label)
        self.button = wx.Button(self,self.__class__.ID_MYBUTTON,label ="Delete" if self.at_top else "Override")
        headingsizer.Add(self.button)
        wx.EVT_BUTTON(self, self.__class__.ID_MYBUTTON, self.eventfn)
        self.mode  = self.onDelete if self.at_top else self.onOverride
        sizer.Add(headingsizer)
        self.widget=GetWidgetFor(self.attribute,parent = self)
        self.widget.Enable(self.at_top)
        self.widget.Layout()
        sizer.Add(self.widget,0,wx.EXPAND)


    def eventfn(self,evt):
        ##We modify the node, so lets get the update target
        # independently and keep it out of the way in
        # case of multiupdates.
        panel_to_refresh = self.GetParent().GetParent()
        if self.mode:
            self.mode(evt)
        else:
            #logger.warning("button action not defined")
            pass
        panel_to_refresh.TransferDataToWindow()

    def onDelete(self,evt):
        name = self.attribute.name
        owner =self.attribute.get_ancestor()
        del owner[name]

    def onOverride(self,evt):
        name = self.attribute.name
        self.top[name] = self.attribute

    def TransferDataToWindow(self,):
        super(_attribute_section,self).TransferDataToWindow()
        self.mode  = self.onDelete if self.at_top else self.onOverride
        self.button.SetLabel("Delete" if self.at_top else "Override")




