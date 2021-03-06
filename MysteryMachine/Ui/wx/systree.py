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
Provides a tree view of a MM system.
""" 

import wx


from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMSystem import MMSystem

from dialogs.objectpicker import ObjectPicker, EVT_OBJECTPICKED_EVENT
from dialogs.newattribute import NewAttributeDialog

from MysteryMachine.Ui.wx import event_handler
import six
import logging

import widgets
import functools

ID_TREECTRL    = wx.NewId()
ID_MENU_RENAME = wx.NewId()
ID_MENU_NEW_CAT= wx.NewId()
ID_MENU_NEW_OBJ= wx.NewId()
ID_MENU_NEW_ATTR=wx.NewId()
ID_MENU_CHANGE_PARENT= wx.NewId()


def object_iter(root,iterator):
    for i in iterator:
        yield root[i]

def _node_name(node):
    #It makes sense to use Str for cateories and objects, as they names of the
    #elements, but or attributes str returns a value. So since object can only
    #contain attirbutes..
    if isinstance(node,MMAttribute):
        return node.name
    else:return six.text_type(node) 



_SystemPopupMenu = wx.Menu()
_SystemPopupMenu.Append(ID_MENU_RENAME,"Rename","Change the name of the System")
_SystemPopupMenu.AppendSeparator()
_SystemPopupMenu.Append(ID_MENU_NEW_CAT,"New Category")

_CategoryPopupMenu = wx.Menu()
_CategoryPopupMenu.Append(ID_MENU_RENAME,"Change display name","Change this categories descriptive name")
_CategoryPopupMenu.Append(ID_MENU_CHANGE_PARENT,"Change default Inheritance parent")
_CategoryPopupMenu.AppendSeparator()
_CategoryPopupMenu.Append(ID_MENU_NEW_OBJ,"New Object")

_ObjectPopupMenu = wx.Menu()
_ObjectPopupMenu.Append(ID_MENU_RENAME,"Rename","Change this object's default name")
_ObjectPopupMenu.Append(ID_MENU_CHANGE_PARENT,"Change Inheritance parent")
_ObjectPopupMenu.AppendSeparator()
_ObjectPopupMenu.Append(ID_MENU_NEW_ATTR,"New Attribute")

_popupmenus = { 'MMSystem': _SystemPopupMenu,
                'MMCategory': _CategoryPopupMenu,
                'MMObject': _ObjectPopupMenu
            }

class TreePanel(wx.Panel):
    def __init__(self,parent,system):
        super(TreePanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(0,0))
        self.parent   = parent
        self.system   = system
        self.buildUi()
        self.Layout()


    def buildUi(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.tree = widgets.MMTreeView(self,ID_TREECTRL, system = self.system)
        self.sizer.Add(self.tree, 1 , wx.EXPAND)
        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, ID_TREECTRL,  self.onRightClick )
        wx.EVT_TREE_ITEM_ACTIVATED(self.tree, ID_TREECTRL,  self.onItemActivated )


        wx.EVT_MENU(self,ID_MENU_RENAME, self.onRenameItem)
        wx.EVT_MENU(self,ID_MENU_NEW_CAT,self.onNewCategory)
        wx.EVT_MENU(self,ID_MENU_NEW_OBJ,self.onNewObject)
        wx.EVT_MENU(self,ID_MENU_NEW_ATTR,self.onNewAttribute)
        wx.EVT_MENU(self,ID_MENU_CHANGE_PARENT,self.onChangeParent)
        self.sizer.Layout()

    def getPanelName(self):
        return u"System Explorer"

    @event_handler()
    def onRenameItem(self,evt):
        caption = "Change name of "+repr(self.menu_on_item)
        title   = ""
        try:
            defvalue = self.menu_on_item[".defname"].get_raw_rst()
            title  = "Existing value:" +repr(self.menu_on_item)
        except KeyError: defvalue = repr(self.menu_on_item)
        newstr = wx.GetTextFromUser(title,caption = caption, default_value = defvalue)
        if newstr:
            if isinstance(self.menu_on_item,MMSystem):
                self.menu_on_item.set_name(newstr)
            else:
                self.menu_on_item[".defname"] = newstr
                    
        self.tree.SetItemText(self.menu_on_itemid,_node_name(self.menu_on_item))

    @event_handler()
    def onNewCategory(self,evt):
        newstr = wx.GetTextFromUser("Category names are limited to numbers and lower case letters",caption = "Reference name for category")
        if newstr:
            try:
                self.menu_on_item.NewCategory(newstr)
            except Exception as e:
                wx.MessageBox(str(e))
        
    @event_handler()
    def onNewObject(self,evt):
        self.system.NewObject(repr(self.menu_on_item))
        
    @event_handler()
    def onNewAttribute(self,evt):
        dlg = NewAttributeDialog(self,-1,owner = self.menu_on_item ,title ="Enter initial value")
        dlg.Show()

    @event_handler()
    def onItemActivated(self,evt):
        node = self.tree.GetItemData(evt.GetItem()).GetData()
        self.GetTopLevelParent().NewSchemaView(node) 

    @event_handler()
    def onRightClick(self,evt):
        itemid = evt.GetItem()
        localroot = self.tree.GetItemData(itemid).GetData()
        self.menu_on_itemid = itemid
        self.menu_on_item = localroot
        self.PopupMenu(_popupmenus[localroot.__class__.__name__])

    @event_handler()
    def onChangeParent(self,evt):
        dlg = ObjectPicker(self,-1,title ="Choose new parent",system = self.system,
                            action = functools.partial(self.onNewParentChosen,self.menu_on_item))
        dlg.Show()

    @event_handler()
    def onNewParentChosen(self,parent,item):
        parent.set_parent(item)
