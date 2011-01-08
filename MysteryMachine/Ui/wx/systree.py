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
from MysteryMachine.schema.MMSystem import MMSystem


Ui_Id = 2000
def NewUI_ID():
  global Ui_Id
  Ui_Id += 1
  return Ui_Id 


ID_TREECTRL    = NewUI_ID()
ID_MENU_RENAME = NewUI_ID()
ID_MENU_NEW_CAT= NewUI_ID()
ID_MENU_NEW_OBJ= NewUI_ID()


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
_CategoryPopupMenu.Append(NewUI_ID(),"Change default Inheritance parent")
_CategoryPopupMenu.AppendSeparator()
_CategoryPopupMenu.Append(ID_MENU_NEW_OBJ,"New Object")

_ObjectPopupMenu = wx.Menu()
_ObjectPopupMenu.Append(ID_MENU_RENAME,"Rename","Change this object's default name")
_ObjectPopupMenu.Append(NewUI_ID(),"Change Inheritance parent")
_ObjectPopupMenu.AppendSeparator()
_ObjectPopupMenu.Append(NewUI_ID(),"New Attribute")

_popupmenus = { 'MMSystem': _SystemPopupMenu,
                'MMCategory': _CategoryPopupMenu,
                'MMObject': _ObjectPopupMenu
            }

class TreePanel(wx.Panel):
    def __init__(self,parent,system):
        super(TreePanel,self).__init__(parent,-1,wx.DefaultPosition,wx.Size(200,400))
        self.system = system
        self.buildUi()
        parent.FitInside()
        self.Layout()


    def buildUi(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.tree = wx.TreeCtrl(self,ID_TREECTRL)
        self.sizer.Add(self.tree, 1 , wx.EXPAND)
        self.rootItem = self.tree.AddRoot(str(self.system),-1,-1,wx.TreeItemData(obj=self.system))
        #Dummy item to allow expansion..
        self.tree.AppendItem(self.rootItem,"Dummy Item")

        wx.EVT_TREE_ITEM_EXPANDING(self.tree, ID_TREECTRL,  self.onExpanding )
        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, ID_TREECTRL,  self.onRightClick )

        wx.EVT_MENU(self,ID_MENU_RENAME, self.onRenameItem)
        wx.EVT_MENU(self,ID_MENU_NEW_CAT,self.onNewCategory)
        wx.EVT_MENU(self,ID_MENU_NEW_OBJ,self.onNewObject)
        self.sizer.Layout()

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
        self.updateNode(self.menu_on_itemid,self.menu_on_item)
        
    def onNewObject(self,evt):
        self.system.NewObject(repr(self.menu_on_item))
        self.updateNode(self.menu_on_itemid,self.menu_on_item)

    def onRightClick(self,evt):
        itemid = evt.GetItem()
        localroot = self.tree.GetItemData(itemid).GetData()
        self.menu_on_itemid = itemid
        self.menu_on_item = localroot
        print "onRightClick on %r " % localroot
        self.PopupMenu(_popupmenus[localroot.__class__.__name__])

    def onExpanding(self,evt):
        itemid = evt.GetItem()
        localroot = self.tree.GetItemData(itemid).GetData()
        self.updateNode(itemid,localroot)

    def updateNode(self,itemid,localroot):
        self.tree.DeleteChildren(itemid)

        if itemid == self.rootItem:
            iterator = object_iter(localroot,localroot.EnumCategories())
        else:
            iterator = localroot.__iter__()

        try:
            for element in sorted(iterator,key=_node_name):
                tmpid = self.tree.AppendItem(itemid,_node_name(element),-1,-1,wx.TreeItemData(obj =element))
                #Dummy item to allow expansion..
                self.tree.AppendItem(tmpid,"Temp Item")
        except TypeError:  pass
