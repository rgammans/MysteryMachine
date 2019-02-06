#!/usr/bin/env python
#   			MMBase.py - Copyright Roger Gammans
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
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMBase.py
#


from __future__ import with_statement


#We import identifier to allow to ensure consisentcy 
from MysteryMachine.parsetools.grammar import identifier
from MysteryMachine.schema.Locker import Reader,Writer
import pyparsing
import logging

#For the container base class
import weakref



class SchemaCommon(object):
    """This is class which handles the utility bits and piesces which are used by schema
    related claess such as MMAttribueValue which aren't actaully nodes
    """

    def canonicalise(self,name):
        ##This keeps it synchronized with the definition
        # of identifier in parsetools/grammar.py
        try:
           #Supress leading dot from the test.
           tstname = name
           if tstname[0] == '.': tstname = tstname[1:]
           #Check that the identifier is good enough to match it.
           identifier.parseString(tstname,parseAll=True)    
        except pyparsing.ParseException:
           raise ValueError("`%s` is not valid in the MysteryMachine Namespace" % name)

        return name.lower()




class MMBase(SchemaCommon):

  """
   This is base class which handles all the stuff which is common to all the nodes
   in a MMSYstem, such as validation , and Store versioning. It interfaces with the
   ExtensionLib to get any required classes for alternate backend stores.

  :version:
  :author:
  """

  def __init__(self,*args,**kwargs):
    """
     Creates the object and /commifinds any require mixins

    @return  :
    @author
    """
    self.logger = logging.getLogger("MysteryMachine.schema")
    self.notify = []
    self._lock = None
    self.is_deleted = False
    self.is_modified = kwargs.get('create',False)

  def getRequiredVersions(self):
    """

    @return string :
    @author
    """
    pass

  def Validate(self):
    """
    The caller interface tthe validation code .

    @return bool :
    @author
    """
    ok = true
    for element in self:
        ok = element.Validate()
        if not ok: break

    if ok: ok=self.DoValidate()
    return ok

  def DoValidate(self):
    """
    Does the actual work of validating this object. Override this
    method to provide your rules.

    @return bool :
    @author
    """
    pass
  
  def get_root(self):
    """
    Returns the root (eg. MMSystem) node for the system which this object is
    a member of.
    """
    root = self.owner
    # Walk up the owner links
    while hasattr(root,"owner") and root.owner != None:
        root = root.owner
    return root

  def get_ancestor(self):
    """Return the ancestor node in the schema heirachy.

    This is usually the owner.
    """
    return self.owner

  def get_nodeid(self,):
     """Return a string representing the nodes path in the MMSystem"""
     owner = self.get_ancestor()
     if owner is not None: owner = owner.get_nodeid()
     if  owner:
         owner += ":"
     else: owner = ""

     return owner + self.name
     

  def getSelf(self):
    """
    returns self. 

    Used to strengthen a weakref and find the prefered object.
    """
    ## This exists so that MMObject can dereferences the weak proxy
    #  object that the store subsystem will normally pass it.
    return self

  def getRef(self):
    """
    This function is sort of the opposite of getSelf().

    Use on an schema object when creating a schema reference
    this ensures a reference is taken rather than a copy. There is
    only a few places this matters but this method is available
    everywhere.

    @returns: value which references self
    """
    ##Actually a NULL op in the general case. Overriden where it matters. 
    return self

  def register_notify(self,a_callable):
    """Register a callable to be invoke when the node changes.

    This is intended for use by users of the schema, rather than in-tree
    users. Added a registration DOES NOT add a refcount to the schema
    node's object and registrations are not (guaranteed to be) persistent
    across object rebuilds.

    As a result you _must_ maintain a seperate reference to any node that
    you register notifies on.

    An example application is include timely Ui update."""
    if a_callable not in self.notify:
        self.notify.append(a_callable)

  def unregister_notify(self,a_callable):
    """Unregister a callable to be invoke when the node changes."""
    self.notify.remove(a_callable)

  def _do_notify(self):
        nones = 0
        to_remove = []
        for fn in self.notify:
            #Pass as back to the notify function so it can be shared.
            if fn is not None:
                try:
                    fn(self)
                #A reference error will occur in fn no longer exists.
                except ReferenceError as e:
                    to_remove += [ fn ]
                #warn about any exceptions from notify.
                except Exception as e: 
                    self.logger.warn(e,exc_info = 1)
        for entry in to_remove:
            self.notify.remove(entry)
                

  def __del__(self):
      #Provide a warning if there are still remaining registrations
      #when this object is destroyed.
      #
      #This occurs when a client has follow the instructions in
      # register_notify.__doc__  and kept their own reference.
      if hasattr(self,"notify") and self.notify: self.logger.warning("Notify still active at del:%s"%self.notify)

  def end_write(self,xaction):
    self.get_root().tm.end_write(self,xaction)

  def abort_write(self,xaction):
    self.get_root().tm.abort_write(self,xaction)

  def abort_read(self,xaction):
    self.get_root().tm.abort_read(self,xaction)

  def start_write(self):
    return self.get_root().tm.start_write(self)

  def end_read(self,xaction):
    self.get_root().tm.end_read(self,xaction)

  def start_read(self):
    return self.get_root().tm.start_read(self)


  def _get_lock(self,):
    if self._lock is None:
        self._lock = self.get_root().lm.get_lock_object()
    return self._lock
    
  lock = property(_get_lock,None,None)
  
  @Writer
  def _new(self): pass

  @Writer 
  def _delete(self,):
    self.is_deleted = True
    
  def discard(self,):
    self.is_modified = False
    self.is_deleted = False
    
  def writeback(self,):
    self.is_modified = False



class MMDeletedNode(MMBase):
    """A node to occupy to cache location.

    The sole purpose of this item is to sit in the cache an
    prevent the real object being loaded from the store.

    This allows faster deletes.
    """
    def __init__(self,owner,name,callback,*args,**kwargs):
        super(MMDeletedNode,self).__init__(self,*args,**kwargs)
        self.owner = owner
        self.name = name
        self.is_deleted = True
        self.callback = callback
    

    @Writer
    def _delete(self): pass

    def discard(self,):
        if hasattr(self.owner,"_invalidate_item_"):
            self.owner._invalidate_item_(self.name)
        else:
            logger.warn("cant incalidate %s",self.get_nodeid())

    def writeback(self,):
        self.callback()

class MMContainer(MMBase):
    """
    This is the base class for object which manage container of
    other MMBase objects to inherit from.

    This is important as the a MMSystem is supposed to provide a guarantee
    a guaranteee about that an Attribute or instance has a single in-core
    instance. 

    The accessor and mutator helper functions provided here are unlocked
    to redice the amount of lock recurse. Do not call outside of
    a start/end_read/write pair.
    """
    def __init__(self,*args,**kwargs):
        super(MMContainer,self).__init__(self,*args,**kwargs)
        self.deleted_items= []
        self.new_items = [ ]
        self._invalidate_cache()

    def _invalidate_cache(self,):
        self.cache = weakref.WeakValueDictionary()

    @Writer
    def _invalidate_item(self,item):
        self._invalidate_item_(item)

    def _invalidate_item_(self,item):
        try:
            del self.cache[item]
        except KeyError: pass

    @Reader
    def _get_item(self,key,func,*args):
        try:
            item = self.cache[key]
        except KeyError:
            item = func(*args)
            self.cache[key] = item
            self._do_compose(item)

        return item

    def _do_compose(self,item): pass

    @Reader
    def _has(self,name,func,*args):
        try:
            item =self.cache[key]
        except KeyError:
            return func(*args)
        else: 
            #TODO: Does reading is_deleted require a reader lock on v?
            return not item.is_deleted
        #Catch any thing which drops through
        return False


    @Reader
    def _is_item_deleted(self,k):
        """Returns true, if the item  has a deleted ghos in the cache"""
        v = self.cache.get(k,None)
        #TODO: Does reading is_deleted require a reader lock on v?
        return v is not None and v.is_deleted

    @Reader
    def _contains_helper(self,name,store_fn ):
       if name in self.cache:
            a = not self.cache[name].is_deleted
       else:
            a = store_fn(name) 
       self.logger.debug( "** %s does %s exist** ", name , ("" if a else "not"))
       return a


    @Reader
    def _EnumX(self, storefn , **kwargs ):
        """Helper function for Enumerator in node classes
        Takes a function to query the store for possible object names
        and checks against the cache, and (hence) current transcation state
        """
        inc_hidden = kwargs.get('inc_hidden', False)
        val_guard = kwargs.get('val_guard', lambda x:True)

        if inc_hidden:
            #guard returns false on hidden
            guard = lambda x:True
        else:
            guard = lambda x:x[0] != '.'

        seen = set()
        def cache_iter():
            """ Allow iteration around a possibly changing
            dictionary"""
            more = True
            #Using the outer seen var causing endless iteration
            my_seen = set()
            while more:
                # Items in keys but not in seen
                todo = set(self.cache.keys()).difference(my_seen)
                if todo:
                    k = todo.pop()
                    my_seen.add(k)
                    yield k,self.cache[k]
                else:
                    more = False


        for k,v in cache_iter():
            if not guard(k): continue
            if not val_guard(v): continue
            seen.add(k)
            #TODO: Does reading is_deleted require a reader lock on v?
            if not v.is_deleted: yield k

        ##Because we've added deleted items, to seen we don't
        # yield them when we find them in the store
        for k in storefn():
            if not guard(k): continue
            if k not in seen and not self._is_item_deleted(k):
                seen.add(k)
                yield k


    def items(self):
        for a in self.iterkeys():
            yield (a ,self[a])

    iteritems = items
    def __iter__(self):
        for a in self.iterkeys():
            yield self[a]

    itervalues = __iter__


    @Writer
    def _del_item(self,key,callback):
        item = self._get_item(key,MMDeletedNode,self,key,callback)
        item._delete()
        #Keep around to enusre the cache doesn't purge 
        #the item
        self.deleted_items.append(item)

    @Writer
    def _set_item(self,k,v):
        self.cache[k] = v
    
    @Writer
    def _new_item(self,k,v):
        self.new_items.append(v)
        self.cache[k] = v
        v._new()
       
    def writeback(self,):
        self.new_items = [ ]
        self.deleted_items = [ ]
        super(MMContainer,self).writeback()
    
    def discard(self,):
        self.deleted_items = [ ]
        self.new_items = [ ]
        super(MMContainer,self).discard()
