#!/usr/bin/env python
#   			attribute_controls.py - Copyright Roger Gammans 
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

import wx
import functools

from dialogs.objectpicker import ObjectPicker, EVT_OBJECTPICKED_EVENT

_Factory = {}

Ui_Id = wx.ID_HIGHEST
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 

ID_LABEL        = NewUI_ID()

def GetWidgetFor(attribute, parent = None):
    """Creates an appropriate bound attribute for the passed widget"""
    attr_type = attribute.get_value().get_type()
    widget_factory = _Factory[attr_type]
    return widget_factory(parent,attribute)


##Create a widget for a Null attribute to prevent crashes..
def _null(parent,attribute):
    return wx.Panel(parent,-1)
_Factory["null"] = _null

class BasicMMAttributeValidator(wx.PyValidator):
    def __init__(self,*args,**kwargs):
        super(BasicMMAttributeValidator,self).__init__(*args)
        self.attribute = kwargs.get('attribute')

    def Clone(self): 
       return BasicMMAttributeValidator(attribute = self.attribute )

    def Validate(self): 
        return True 

    def TransferToWindow(self):
        print "TTW"
        self.GetWindow().SetValue(str(self.attribute))
        return True 

    def TransferFromWindow(self):
        if self.GetWindow().IsModified():
            print "TFW"
            self.attribute.set_value(self.GetWindow().GetValue())
        return True 


def _writeback(ctrl,event): 
    print "_Writeback"
    ctrl.GetValidator().TransferFromWindow()

ID_ATTRTEXTCTRL = NewUI_ID()
def simple_wx_widget(parent,attribute):

        # XXX
        # I can't find the most sensible way of find the users
        # prefered monospace font. Since attributes are rst based
        # monospace editting is pretty much mandantory.
        #
        #
        # Here I used a wx call which only seems to work on windows
        # then fall back to just asking fro a 9pt monospace.
        # - if the user had a 10py monospace a adefault I'm not
        # sure what we do... 
        # XXX XXX
        #
        deffont = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
        if not deffont.IsFixedWidth():
            deffont =wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
         
        content  = wx.TextCtrl(parent,ID_ATTRTEXTCTRL,style = (wx.TE_MULTILINE ))
        wx.EVT_KILL_FOCUS(content,functools.partial(_writeback,content))
        content.SetFont(deffont)
        #content.SetValue(str(attribute)) 
        content.SetValidator(BasicMMAttributeValidator(attribute = attribute))
        
        return content

_Factory["simple"]      = simple_wx_widget
_Factory["simple_utf8"] = simple_wx_widget


class _list_wx_widget(wx.PyPanel):
    def __init__(self,parent,attribute):
        super(_list_wx_widget,self).__init__(parent,-1)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        sizer = wx.FlexGridSizer(wx.VERTICAL,3,len(attribute))
        self.SetSizer(sizer) 
        i = 0
        for element in attribute:
            index_label = wx.StaticText(self,ID_LABEL)
            index_label.SetLabel(str(i))
            stable_idx  = wx.StaticText(self,ID_LABEL)
            stable_idx.SetLabel(element.name)
            data        = GetWidgetFor(element, parent = self)

            sizer.Add(index_label)
            sizer.Add(stable_idx)
            sizer.Add(data)
            i += 1

_Factory["list"]      = _list_wx_widget


class MMRefAttributeValidator(wx.PyValidator):
    def __init__(self,*args,**kwargs):
        super(MMRefAttributeValidator,self).__init__(*args)
        self.attribute = kwargs.get('attribute')

    def Clone(self): 
       return MMRefAttributeValidator(attribute = self.attribute )

    def Validate(self): 
        return True 

    def TransferToWindow(self):
        print "link update"
        self.GetWindow().label.SetLabel("Reference to " + str(self.attribute.getSelf()))
        self.GetWindow().Layout()
        return True 

    def UpdateValue(self,new_value):
        self.attribute.set_value(new_value)
        #Update display.
        self.TransferToWindow()
 
class _ref_wx_widget(wx.PyPanel):
    ID_OPENBUTTON   = NewUI_ID()
    ID_CHANGEBUTTON = NewUI_ID()
    ID_EXPANDBUTTON = NewUI_ID()
    def __init__(self,parent,attribute):
        super(_ref_wx_widget,self).__init__(parent,wx.ID_ANY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        self.attribute = attribute
        self.label = wx.StaticText(self,-1)
        self.SetValidator(MMRefAttributeValidator( attribute = self.attribute))
        sizer.Add(self.label)
        sizer.Add(wx.Button(self,self.__class__.ID_OPENBUTTON,label="Open"))
        sizer.Add(wx.Button(self,self.__class__.ID_CHANGEBUTTON,label="Change.."))
        sizer.Add(wx.Button(self,self.__class__.ID_EXPANDBUTTON,label="Expand"))

        wx.EVT_BUTTON(self,self.__class__.ID_CHANGEBUTTON,self.onChangeTarget)
        wx.EVT_BUTTON(self,self.__class__.ID_OPENBUTTON,self.onOpenTarget)
    
    def onChangeTarget(self,evt): 
        dlg = ObjectPicker(self,-1,title ="Chose new target",system = self.attribute.get_root(),
                            action = self.GetValidator().UpdateValue)
        dlg.Show()

    def onOpenTarget(self,evt):
        frame = self.GetTopLevelParent()
        frame.NewSchemaView(self.attribute.getSelf())

_Factory["ref"]      = _ref_wx_widget

#Bidi could do with a better widget that understands anchor points,
# but this will do for now. 
_Factory["bidilink"]      = _ref_wx_widget
