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


##Create a widget for a Null attribute to prevent crashes..
def _null(parent,attribute):
    return wx.Panel(parent,-1)
_Factory["null"] = _null


class MysterySchemaValidatorBase(wx.PyValidator):
    def __init__(self,*args,**kwargs):
        super(MysterySchemaValidatorBase,self).__init__(*args)
        self.attribute = kwargs.get('attribute')
        if self.attribute is not None: self.attribute.register_notify(self.notifychange)        


    def __del__(self):
        if self.attribute is not None: self.attribute.unregister_notify(self.notifychange)        

    def notifychange(self,attribute):
        assert attribute == self.attribute,"Misrouted notify"
        print "notified for %r"%self.attribute
        self.TransferToWindow()

    def Clone(self): 
       return self.__class__(attribute = self.attribute )

    def Validate(self): 
        return True 



class BasicMMAttributeValidator(MysterySchemaValidatorBase):
    def __init__(self,*args,**kwargs):
        super(BasicMMAttributeValidator,self).__init__(*args,**kwargs)

    def TransferToWindow(self):
        self.GetWindow().SetValue(str(self.attribute))
        return True 

    def TransferFromWindow(self):
        print "text TFW"
        if self.GetWindow().IsModified():
            self.attribute.set_value(self.GetWindow().GetValue())
        return True 

def _writeback(ctrl,event): 
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
    ID_APPENDBUTTON = NewUI_ID()
    def __init__(self,parent,attribute):
        super(_list_wx_widget,self).__init__(parent,-1)
        self.attribute = attribute
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        sizer = wx.FlexGridSizer(wx.VERTICAL,5,len(attribute))
        self.SetSizer(sizer) 
        self.newbutton = wx.Button(self,self.__class__.ID_APPENDBUTTON,label="Append")
        sizer.Add(self.newbutton)
        wx.EVT_BUTTON(self,self.__class__.ID_APPENDBUTTON,self.onAppend)
        sizer.Add(wx.Panel(self,wx.ID_ANY))
        sizer.Add(wx.Panel(self,wx.ID_ANY))
        sizer.Add(wx.Panel(self,wx.ID_ANY))
        sizer.Add(wx.Panel(self,wx.ID_ANY))

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
            sizer.Add(wx.Button(self,wx.ID_ANY,label="Insert After"))
            sizer.Add(wx.Button(self,wx.ID_ANY,label="Delete"))
            i += 1

    def onAppend(self,evt):
       from dialogs.newattribute import NewAttributeDialog
       dlg = NewAttributeDialog(self,-1,owner = self.attribute ,title ="Enter initial value",
                                write = "append")
       dlg.Show()

_Factory["list"]      = _list_wx_widget


class MMRefAttributeValidator(MysterySchemaValidatorBase):
    def __init__(self,*args,**kwargs):
        super(MMRefAttributeValidator,self).__init__(*args,**kwargs)

    def TransferToWindow(self):
        self.GetWindow().SetLabel("Reference to " + str(self.attribute.getSelf()))
        self.GetWindow().GetParent().Layout()
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
        self.attribute = attribute
        self.buildUI()

    def buildUI(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        self.label = wx.StaticText(self,-1)
        self.label.SetValidator(MMRefAttributeValidator( attribute = self.attribute))
        sizer.Add(self.label)
    
        openbutton = wx.Button(self,self.__class__.ID_OPENBUTTON,label="Open")
        openbutton.Enable(hasattr(self.GetTopLevelParent(),"NewSchemaView"))
        sizer.Add(openbutton)
        sizer.Add(wx.Button(self,self.__class__.ID_CHANGEBUTTON,label="Change.."))
        sizer.Add(wx.Button(self,self.__class__.ID_EXPANDBUTTON,label="Expand"))

        wx.EVT_BUTTON(self,self.__class__.ID_CHANGEBUTTON,self.onChangeTarget)
        wx.EVT_BUTTON(self,self.__class__.ID_OPENBUTTON,self.onOpenTarget)
    
    def onChangeTarget(self,evt): 
        from dialogs.objectpicker import ObjectPicker
        dlg = ObjectPicker(self,-1,title ="Chose new target",system = self.attribute.get_root(),
                            action = self.label.GetValidator().UpdateValue)
        dlg.Show()

    def onOpenTarget(self,evt):
        frame = self.GetTopLevelParent()
        frame.NewSchemaView(self.attribute.getSelf())

_Factory["ref"]      = _ref_wx_widget


class BidiAnchorValidator(MysterySchemaValidatorBase):
    def __init__(self,*args,**kwargs):
        super(BidiAnchorValidator,self).__init__(*args,**kwargs)

    def TransferToWindow(self):
        anchor = self.attribute.get_anchor()
        if anchor is not None:
            self.GetWindow().SetStringSelection(anchor.name)
            self.GetWindow().Layout()
        return True
   
    def TransferFromWindow(self):
        name = self.GetWindow().GetStringSelection()
        node = self.attribute
        while node is not None:
            if name == node.name:
                import MysteryMachine.schema.MMDLinkValue as dlk
                self.attribute.set_value(dlk.CreateAnchorPoint(node))
                break
            try:
                node = node.get_ancestor()
            except AttributeError: node = None
        self.TransferToWindow()

class BidiDestValidator(MMRefAttributeValidator):
    def TransferToWindow(self):
        super(BidiDestValidator,self).TransferToWindow()
        #Disable the anchor movement of the reference is set.
        self.GetWindow().GetParent().anchors.Enable(self.attribute.get_object() is None)

    def UpdateValue(self,new_value):
        import MysteryMachine.schema.MMDLinkValue as dlk
        self.attribute.set_value( dlk.ConnectTo(new_value))
        self.TransferToWindow()
 
class _bidi_wx_widget(_ref_wx_widget):
    ID_ANCHORCHOICE = NewUI_ID()
    def __init__(self,parent,attribute):
        super(_bidi_wx_widget,self).__init__(parent,attribute)
        #sizer = self.GetSizer()

    def SetSizer(self,sizer):
        if not self.GetSizer():
            super(_bidi_wx_widget,self).SetSizer(sizer)
        else:
            self.GetSizer().Add(sizer,0,wx.EXPAND)

    def buildUI(self):
        bidisizer   = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(bidisizer)
        anchorsizer = wx.BoxSizer(wx.HORIZONTAL)
        bidisizer.Add(anchorsizer)
        
        valid_anchors = self._get_valid_anchors()
        self.anchors = wx.Choice(self,self.__class__.ID_ANCHORCHOICE,choices = valid_anchors , 
                                 validator = BidiAnchorValidator(attribute = self.attribute))

        wx.EVT_CHOICE(self,self.__class__.ID_ANCHORCHOICE,functools.partial(_writeback,self.anchors))
        anchorsizer.Add(wx.StaticText(self,wx.ID_ANY,"Anchor:"))
        anchorsizer.Add(self.anchors)
        super(_bidi_wx_widget,self).buildUI()
        #Change validator for the link dest for one that know how to update Bidi attr's 
        self.label.SetValidator(BidiDestValidator( attribute = self.attribute))
        

    def _get_valid_anchors(self):
        anchors = []
        node = self.attribute
        while node is not None:
            anchors += [ node.name ]
            try:
                node = node.get_ancestor()
            except AttributeError: node = None

        return anchors


_Factory["bidilink"]      = _bidi_wx_widget
