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

    def TransferFromWindow(self):
        print "TFW"
        self.attribute.set_value(self.GetWindow().GetValue())

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
         
        content  = wx.TextCtrl(parent,-1,style = (wx.TE_MULTILINE ))
        content.SetFont(deffont)
        #content.SetValue(str(attribute)) 
        content.SetValidator(BasicMMAttributeValidator(attribute = attribute))
        
        return content

_Factory["simple"]      = simple_wx_widget
_Factory["simple_utf8"] = simple_wx_widget


def _list_wx_widget(parent,attribute):
    sizer = wx.FlexGridSizer(wx.VERTICAL,3,len(attribute))
    i = 0
    for element in attribute:
        index_label = wx.StaticText(parent,ID_LABEL)
        index_label.SetLabel(str(i))
        stable_idx  = wx.StaticText(parent,ID_LABEL)
        stable_idx.SetLabel(element.name)
        data        = GetWidgetFor(element, parent = parent)

        sizer.Add(index_label)
        sizer.Add(stable_idx)
        sizer.Add(data)
        i += 1

    return sizer
_Factory["list"]      = _list_wx_widget


def _ref_wx_widget(parent,attribute):
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    label = wx.StaticText(parent,-1)
    label.SetLabel("Reference to " + str(attribute.getSelf()))
    sizer.Add(label)
    sizer.Add(wx.Button(parent,-1,label="Goto"))
    sizer.Add(wx.Button(parent,-1,label="Change.."))
    return sizer

_Factory["ref"]      = _ref_wx_widget

#Bidi could do with a better widget that understands anchor points,
# but this will do for now. 
_Factory["bidilink"]      = _ref_wx_widget
