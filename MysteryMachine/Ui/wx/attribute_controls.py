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

from widgets import  NotifyClosure

_Factory = {}

Ui_Id = wx.ID_HIGHEST
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 

ID_LABEL        = NewUI_ID()


def _pop(seq):
    try:
        return seq.pop(0)
    except IndexError: pass
    return None


def _compare_names_lt(a,b):
    """A comparsion function which treats None as the largest possible value"""
    if a is None: return False
    if b is None: return True
    return a < b

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


class _listitem_wx_widget(wx.PyPanel):

    def __init__(self,parent,item,index):
        super(_listitem_wx_widget,self).__init__(parent,-1)
        self.item = item
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        self.index_label = wx.StaticText(self,ID_LABEL)
        self.index_label.SetLabel(str(index))
        self.stable_idx  = wx.StaticText(self,ID_LABEL)
        self.stable_idx.SetLabel(item.name)
        self.data        = GetWidgetFor(item, parent = self)

        sizer.Add(self.index_label)
        sizer.Add(self.stable_idx)
        sizer.Add(self.data,3,wx.EXPAND)
        sizer.Add(wx.Button(self,wx.ID_ANY,label="Insert After"))
        sizer.Add(wx.Button(self,wx.ID_ANY,label="Delete"))
        
    def get_index(self):
        return int(self.index_label.GetLabel())
 
    def get_stableindex(self):
        return self.stable_idx.GetLabel()
 
    def set_index(self,idx):
        self.index_label.SetLabel(str(idx)) 

class _list_wx_widget(wx.PyPanel):
    ID_APPENDBUTTON = NewUI_ID()
    def __init__(self,parent,attribute):
        super(_list_wx_widget,self).__init__(parent,-1)
        self.attribute = attribute
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.newbutton = wx.Button(self,self.__class__.ID_APPENDBUTTON,label="Append")
        sizer.Add(self.newbutton)
        wx.EVT_BUTTON(self,self.__class__.ID_APPENDBUTTON,self.onAppend)
        self.notifyclosure = NotifyClosure(self,self.node_changed)
        self.notifyclosure.register(self.attribute)

        i = 0
        for element in attribute:
            sizer.Add(_listitem_wx_widget(self,element,i))
            i += 1

    def node_changed(self,obj):
        print "list noded changed"
        i =0 
        sizer = self.GetSizer()
        #Use list comprehension to copy elements into a list
        # - ignore the first (append button) element of the list display objects
        display_items = [ x.GetWindow() for x in sizer.GetChildren()][1:]
        index_elements = [x for x in self.attribute]

        print "sn %s"%index_elements
        print "di %s"%display_items

        element = _pop(index_elements)
        child   = _pop(display_items)
        while (element is not None) or (child is not None):
       
            cname = child and child.get_stableindex()
            #Can't use the boolean eval trick to protect elements
            # against None, because they may test as false for their own
            # reasonns . Or may have no boolean conversion
            nname = element
            if element is not None: nname = nname.name

            print "%r <->%r = (%s,%s)"%(nname,cname,nname==cname,_compare_names_lt(nname,cname))
            if nname == cname:
                #Node in place in tree already, move on to next
                # but we may need to update it's index positions.
                child.set_index(i)
                element = _pop(index_elements)
                child   = _pop(display_items)
                i += 1
            elif _compare_names_lt(nname,cname):
               #Insert item
                newpanel=_listitem_wx_widget(self,element,i)
                sizer.Insert(i+1,newpanel)
                newpanel.TransferDataToWindow()
                i+=1
                element = _pop(index_elements)
            else:
                # Remove item.
                sizer.Remove(i)
        self.GetTopLevelParent().Layout()

 
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
