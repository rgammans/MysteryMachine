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

from dialogs import ObjectPicker, EVT_OBJECTPICKED_EVENT
import widgets
import functools

Ui_Id = 2000
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 


ID_TREECTRL    = NewUI_ID()
ID_MENU_RENAME = NewUI_ID()
ID_MENU_NEW_CAT= NewUI_ID()
ID_MENU_NEW_OBJ= NewUI_ID()
ID_MENU_CHANGE_PARENT= NewUI_ID()


def object_iter(root,iterator):
    for i in iterator:
        yield root[i]

def _node_name(node):
    #It makes sense to use Str for cateories and objects, as they names of the
    #elements, but or attributes str returns a value. So since object can only
    #contain attirbutes..
    if isinstance(node,MMAttribute):
        return node.name
    else:return str(node) 



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
_ObjectPopupMenu.Append(NewUI_ID(),"New Attribute")

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
        wx.EVT_MENU(self,ID_MENU_NEW_CAT,self.onNewCategory)
        wx.EVT_MENU(self,ID_MENU_CHANGE_PARENT,self.onChangeParent)
        self.sizer.Layout()

    def getPanelName(self):
        return u"System Explorer"

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

    def onNewCategory(self,evt):
        newstr = wx.GetTextFromUser("Category names are limited to numbers and lower case letters",caption = "Reference name for category")
        if newstr:
            try:
                self.menu_on_item.NewCategory(newstr)
            except BaseException , e:
                wx.MessageBox(str(e))
        self.tree.updateNode(self.menu_on_itemid,self.menu_on_item)
        
    def onNewObject(self,evt):
        self.system.NewObject(repr(self.menu_on_item))
        self.tree.updateNode(self.menu_on_itemid,self.menu_on_item)

    def onItemActivated(self,evt):
        node = self.tree.GetItemData(evt.GetItem()).GetData()
        panel = None
 
        if isinstance(node,MMAttribute):
            import attributepanel
            panel = attributepanel.AttributePanel(self.parent, node )
        
        if isinstance(node,MMObject):
            import objectpanel
            panel = objectpanel.ObjectPanel(self.parent, node )


        if panel: self.parent.AddPanel(panel)


    def onRightClick(self,evt):
        itemid = evt.GetItem()
        localroot = self.tree.GetItemData(itemid).GetData()
        self.menu_on_itemid = itemid
        self.menu_on_item = localroot
        print "onRightClick on %r " % localroot
        self.PopupMenu(_popupmenus[localroot.__class__.__name__])

    def onChangeParent(self,evt):
        print "change parent"
        dlg = ObjectPicker(self,-1,title ="Chose",system = self.system,
                            action = functools.partial(self.onNewParentChosen,self.menu_on_item))
        dlg.Show()

    def onNewParentChosen(self,parent,item):
        print "chosen " + str(item)
        parent.set_parent(item)
