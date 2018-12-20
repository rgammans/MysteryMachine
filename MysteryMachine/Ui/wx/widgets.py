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
from MysteryMachine.Ui.wx import event_handler
import six
import logging

import functools



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
    else:return six.text_type(node) 


def _pop(seq):
    try:
        return seq.pop()
    except IndexError: pass
    return None

def _none_guard(value,fn):
    if value is None: return None
    return fn(value)


class NotifyClosure(object):
    """Check the target of the notify is non-zero at notify time.

    This object can hold be registered on multiple nodes as
    a notify target, but it forwards the notify request to a callable
    passed to __init__.

    The callable should also have a sentinel object (usually self) which
    evalutes to false in a boolean context if the notify is no logner valid.

    In this case the Closure automatically unregisters itself from all
    it's nodes.

    The primary use of this is to wrap calls into wx widgets which will
    become false when the are tidied (deleted) away by the C++ code.
    """
    def __init__(self,sentinel,a_callable):
        self.sentinel = sentinel
        self.target   = a_callable
        self.registrations = []

    def __del__(self):
        assert self.registrations == [] ,"Registration exists at del in %s"%self

    def register(self,node):
        node.register_notify(self)
        if node not in self.registrations:
            self.registrations += [ node ]

    def unregister(self,node):
        node.unregister_notify(self)
        self.registrations.remove(node)

    def unregister_all(self):
        for node in self.registrations:
            node.unregister_notify(self)
        self.registrations = []

    def __call__(self,obj):
        if self.sentinel:
            self.target(obj)
        else: self.unregister_all()


class MMTreeView(wx.TreeCtrl):
    """Treectrl widget show a complete MMSystem"""
    def __init__(self,parent,id,*args,**kwargs):
        self.system = _get_argument('system',kwargs)
        self.logger = logging.getLogger("MysteryMachine.Ui.wx.widgets.TreeView")


        super(MMTreeView,self).__init__(parent,id,**kwargs)
        self.id = id

        self.notifyclosure = NotifyClosure(self,self.node_notifier)

        self.rootItem = self.AddRoot(six.text_type(self.system),-1,-1,wx.TreeItemData(obj=self.system))
        self.notifyclosure.register(self.system)
        #Use the empty string as the db path for the root node.
        self.nodes = { '' : self.rootItem }
        self.SetItemHasChildren(self.rootItem,True)

        wx.EVT_TREE_ITEM_EXPANDING(self ,self.id,  self.onExpanding )
        wx.EVT_WINDOW_DESTROY(self,self.onDestroy)

    @event_handler()
    def onDestroy(self,event):
        self.notifyclosure.unregister_all()
 
    @event_handler()
    def onExpanding(self,evt):
        itemid = evt.GetItem()
        localroot = self.GetItemData(itemid).GetData()
        self.updateNode(itemid,localroot)
    
    def node_notifier(self,node):
        if node is self.system:
            return self.updateNode(self.rootItem,self.system)

        node_addr = repr(node)
        try:
            itemid = self.nodes[node_addr]
        except KeyError as e:
            self.logger.warn("ignoring notify on unknown node %s"%node_addr)
        else:
            self.updateNode(itemid,node) 
    

    def updateNode(self,itemid,localroot):
        self.SetItemHasChildren(itemid,False)
        
        #self.DeleteChildren(itemid)
        display_items = sorted(self.child_iter(itemid),key = self.GetItemText )

        if itemid == self.rootItem:
            iterator = object_iter(localroot,localroot.EnumCategories())
        else:
            iterator = localroot.__iter__()

        try:
            schema_nodes = sorted(iterator,key=_node_name)
        except TypeError as e:
            ##Most likely casue of a type erros is a non-iterable node.
            # log this at the debug lvel but return.
            self.logger.debug(e,exc_info =1)
            return

 
        ##Walk both lists backward until they are empty,
        # each list pass should remove an elemnt from one or both lists
        # which guarantee we terminate.
        #
        # Because the lists are sorted we should meet the matching nodes
        # in matching order, not doing so means we find insertions and deletions.
        element = _pop(schema_nodes)
        child   = _pop(display_items)
        while (element is not None) or (child is not None):
       
            #We now know there is at least one child entry.
            if element is not None: self.SetItemHasChildren(itemid,True)

            nname = _none_guard(element, _node_name ) 
            cname = _none_guard(child, self.GetItemText )

            if nname == cname:
                #Node in place in tree already, move on to next
                element = _pop(schema_nodes)
                child   = _pop(display_items)

            elif nname < cname:
               #Remove item.
                oldname = repr(self.GetItemData(child).GetData())
                self.Delete(child)
                del self.nodes[oldname] 
                #move on to next display item
                child   = _pop(display_items)
 
            else: # nname > cname 
                #Insert node 
                if child: 
                    tmpid = self.InsertItem(itemid,child,nname,-1,-1,wx.TreeItemData(obj =element))
                else:
                    tmpid = self.InsertItemBefore(itemid,0,nname,-1,-1,wx.TreeItemData(obj =element))
                self.nodes[repr(element)] = tmpid
                self.notifyclosure.register(element)
                self.SetItemHasChildren(tmpid,True)
                element = _pop(schema_nodes)

      
    def child_iter(self,itemid):
        child, cookie = self.GetFirstChild(itemid)
        while child.IsOk():
            yield child
            child,cookie = self.GetNextChild(itemid,cookie)
