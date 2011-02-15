#!/usr/bin/env python
#   			widgets.py - Copyright %author%
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
Provides an implementation of common widgets.
""" 

import wx
import wx.lib.newevent

import MysteryMachine
from MysteryMachine.schema.MMSystem import MMSystem
from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMObject import MMObject




def _apply_default(name,default,kwargs):
    if name not in kwargs: kwargs[name] = default

def _get_argument(name,kwargs):
    rv = kwargs.get(name)
    if name in kwargs: del kwargs[name]
    return rv

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



class MMTreeView(wx.TreeCtrl):
    def __init__(self,parent,id,*args,**kwargs):
        self.system = _get_argument('system',kwargs)

        super(MMTreeView,self).__init__(parent,id,**kwargs)
        self.id = id

        self.rootItem = self.AddRoot(str(self.system),-1,-1,wx.TreeItemData(obj=self.system))
        self.SetItemHasChildren(self.rootItem,True)

        wx.EVT_TREE_ITEM_EXPANDING(self ,self.id,  self.onExpanding )


    def onExpanding(self,evt):
        itemid = evt.GetItem()
        localroot = self.GetItemData(itemid).GetData()
        self.updateNode(itemid,localroot)

    def updateNode(self,itemid,localroot):
        self.SetItemHasChildren(itemid,False)
        self.DeleteChildren(itemid)

        if itemid == self.rootItem:
            iterator = object_iter(localroot,localroot.EnumCategories())
        else:
            iterator = localroot.__iter__()

        try:
            for element in sorted(iterator,key=_node_name):
                tmpid = self.AppendItem(itemid,_node_name(element),-1,-1,wx.TreeItemData(obj =element))
                self.SetItemHasChildren(tmpid,True)
        except TypeError:  pass
