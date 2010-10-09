#!/usr/bin/env python
#   			MMDLinkValue.py - Copyright Roger Gammans
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
This module provide a mechanism for creating a pair of attributes which operate as a BiDirectional
link between two objects.

Link Semantics
==============

Links comprise of two parts which should point to to each other. The
get_object method will return a MMReference further up the 
System Hierarchy. It is a requirement that a link points to 
an element in it's own ownership chain.

Links can exist in a disconnected state , in this state they are known 
as anchor points. An anchor point only knows the object to which it
will be a link to when it is connected. Anchor points can be created 
with the CreateAnchorPoint() function available in this module.

::
    player["character"] = CreateAnchorPoint(player)

The ConnectTo() functions allows to anchor points to be conneted, like so
::

    player1["character"] = CreateAnchorPoint(player1)
    character2["player"] = CreateAnchorPoint(character2)
    player1["chararacter"] = ConnectTo(character2["player"])

This will join the two anchor points created together to form a completed link,
now the links is completed player["character"].get_object() returns character2 
(it is the what character2["player"] was an anchor point for character2. )

These links are now considered to be in the connected state, and get_object()
and get_partner() should be able to return useful values. In the disconnected
state these methods should return None.

The Anchor point semantics allow arrays of anchor points to be created and still
refer to the main object.

Additionally there is a convinence function CreateBiDiLink() for the case above
where you are immediately creaing a connected pair. You can use it simply like
this:
::
    CreateBiDiLink(player1,"character",character2,"player)

to achieve the same effect as the previous example.

Copying a link moves the end of the link which is the source for the copy, turning
this attribute into an anchor point. And changes the partner link attribute
to reflect this move. 

Note though the copy need to be to an existing anchor point, so that the partner
link can find it correct referent object.

::
       #Reassign player4 the character that player1 had
        player4["character"] = CreateAnchorPoint(player4)
        player4["character"] = player1["character"]
        print player1["character"].get_object()
None
    
        print repr(player1["character"].get_anchor())
player:1
        print repr(player4["character"].get_object())
character:2
        print repr(character2["player"].get_object())
player:4

These semantic ensure consistency while disallowing
and ensure there is always a single obvious referent for each link attribute.

When copying anchor points the distance back up the hierachy tree the anchor
points refers to is presevered. This allows the creation of anchor points in 
parent objects. Attempts to bind to these should create a new link in the actual
target object.

The bidilinks have been carefully implemented to ensure they can be contained
in list attributes if more complex structures are required.

"""

from __future__ import with_statement
from MMAttributeValue import MMAttributeValue
from MMAttribute import MMAttribute

from MysteryMachine.parsetools.grammar import Grammar

import copy
import weakref
import thread

import logging

_value_typename = "bidilink"

class _member_guard:
    def __init__(self,obj,attribute):
        self.obj=obj
        self.attribute = attribute


    def __enter__(self):
        setattr(self.obj,self.attribute,thread.get_ident())
        return self
    def __exit__(self,*args):
        setattr(self.obj,self.attribute,False)
        return False 

    def test(self,obj):
        if hasattr(obj,self.attribute):
            return getattr(obj,self.attribute) == getattr(self.obj,self.attribute)
        return False


class  BiDiLinkTargetMismatch(RuntimeError):
    pass

class BiDiCantCreate(ValueError):
    pass

def _process_obj_and_attr(obj,attr):
    #Check attributes are valid..
    if ":" in attr:
        basepath_elements =  attr.split(":")
        baseref = obj
        for ele in  basepath_elements[:-1]:
            baseref = baseref[ele]
        try:
            baseref.__getitem__(basepath_elements[-1])
        except KeyError:
            pass
    else:
        basepath_elements =  [ obj.canonicalise(attr) ]
        baseref = obj
    return baseref , basepath_elements


def _container_walk(root,path):
    node = root
    for element in path:
        if element != "":
            node = node[element]
        if node is None: break
    return node


def _walk_back(obj,dist):
    objname = repr(obj)
    objpath = objname.split(":")
    if dist >= len(objpath): return None
    return _container_walk(obj.get_root(),objpath[:-dist])

def CreateBiDiLink(obj1,attrname1,obj2,attrname2):
    """
    Create a bidilink between objects obj1 & obj2.

    Specifically obj1[attrname1] contains a link to obj2, and
    Specifically obj2[attrname2] contains a link to obj1.

    This links try to maintain consisency if they are moved etc.
    """
    baseref1,basepath1_elements = _process_obj_and_attr(obj1,attrname1)
    baseref2,basepath2_elements = _process_obj_and_attr(obj2,attrname2)

    baseref2[basepath2_elements[-1]] = MMDLinkValue(target = obj1 , foreign = attrname1)
    baseref1[basepath1_elements[-1]] = MMDLinkValue(target = obj2 , foreign = attrname2, compose = True)
    #baseref2[basepath2_elements[-1]].get_value().compose() 


def ConnectTo(attribute):
    """
    This functions returns a half-link so that it can be used to 
    connect two anchor point. That half link will be a partner for
    the passed attribute.

    You use this by assigning an existing anchop point to the result
    from this function.
    """
    if not isinstance(attribute,MMAttribute):
        raise TypeError("Can only ConnectTo an MMAttribute")
    if attribute.get_value().get_type() !=  _value_typename:
        raise TypeError("Can only ConnectTo bidilinks")

    anchorname = repr(attribute.get_anchor())
    attrname   = repr(attribute)
    return MMDLinkValue(target = attribute.get_anchor() , 
                        foreign=attrname[len(anchorname)+1:]) 

def CreateAnchorPoint(obj):
    """
    Creates an anchor point for object obj which can be turned into a
    complete link later. (ie. with ConnectTo() )
    """
    return MMDLinkValue(anchor = obj)


class MMDLinkValue(MMAttributeValue):
    typename =  _value_typename
    contain_prefs = {}
    def __init__(self,*args,**kwargs):
        super(MMDLinkValue,self).__init__(*args,**kwargs)
        self.logger    = logging.getLogger("MysteryMachine.schema.MMDLinkValue")
        self.obj            = kwargs.get("target",None)
        self.partner_name   = kwargs.get("foreign",None)
        self.anchorp        = kwargs.get("anchor",None)
        self.obj_name       = None
        self.anchordist   = None
        if len(self.parts) == 0:
            #Validate we have enough data..
            # Handle anchopoint init first...
            if self.anchorp is not None:
                self.parts["anchor"] = repr(self.anchorp)
            else:
                if self.obj is None:
                    raise ValueError("BiDilink needs an object")
                else: self.obj_name = repr(self.obj).split(":")
                if self.partner_name is None:
                    raise ValueError("BiDiLink needs a foreign target")
                #Create member variables we can use..
                self.partner_name =  self.partner_name.split(":")
                self.parts["target"] =  repr(self.obj)+":" + ":".join(self.partner_name) +"," +str(len(self.partner_name))
        else:
             self._process_parts()
   
        self.exports += [ "get_object", "get_partner" , "get_anchor"]
        self.valid = False 
        self.in_assignment = False

    def assign(self,other):
      """Called by MMAttribute when an value assignment occurs - not exported"""
      self.logger.debug( "in assign")
      if self.__class__ is other.__class__:
          self.valid = False
          with _member_guard(self,"in_assignment") as assign_guard:
            self.logger.debug( "got inassign lock")
            oldpartner =  self.get_partner()
            #Keep hold of old partner data, so we can delink it later.
            if oldpartner:
                oldpanchor = oldpartner.get_anchor()
            self.logger.debug( "oldp>%r"%oldpartner )
            
            self.parts =  copy.copy(other.parts)
            oldattr    =  other.get_partner()
            self.logger.debug( "othp>%r"%oldattr )
            self.logger.debug( "myap>%r"%self.anchorp )

            self._process_parts()
            

            #Update partner if exists to break the link, iff it isn't inside 
            # assign further up the stack. 
            not_opassign = True
            if oldpartner: not_opassign = not assign_guard.test(oldpartner.get_value())
            if oldpartner and  not_opassign:
               oldpartner.set_value(MMDLinkValue(anchor = oldpanchor))

            if hasattr(oldattr,"get_partner"): 
                oldattr=oldattr.get_partner()
                self.logger.debug( "my-p>%r"%oldattr)
                #Turn other into an anchorpoint.
                if other.anchordist is not None:
                    other.parts = { 'anchordist' : other.anchordist }
                    other._process_parts()

                #Write the changes to the new anchorpoint back, now our state is sane.
                if oldattr and oldattr.get_value() is other:
                    oldattr._writeback()
                else:
                    self.logger.debug( "writeback skipped")

      else:
            raise ValueError("Assign of mismathched classes , %s" %repr(other.__class__))
    

    def _process_parts(self):
       self.logger.debug( "_pp>%s"%self.parts)
       if "target" in self.parts:
            attributename,sniplen = self.parts["target"].rsplit(",",1)
            attributename = attributename.split(":")
            sniplen=int(sniplen)
            self.obj_name= attributename[:-sniplen]
            self.partner_name=attributename[-sniplen:]
       else:
            self.obj_name     = None 
            self.partner_name = None
            if "anchordist" in self.parts:
                self.anchordist   = int(self.parts["anchordist"])

    def _compose(self,obj = None ):
        if obj is None: raise BidiCantCreate("Cannot compose as owned by None") 
        self.logger.debug( "%s _compose (%r,%s)" % (object.__repr__(self) ,obj, self.parts))
        #Now we have a handle on the system find our objects etc,
        if self.obj_name is None:
            if self.anchordist is None:
                ##Legacy code handles if we were inited from an anchor part 
                #This should just be an anchor_point - find and write back canonical name.
                self.logger.debug( "walking for anchor %s , %r"%(self.parts["anchor"],obj))
                oldanchor    =  self.anchorp
                anchorpath   = self.parts["anchor"].split(":")
                self.anchorp = _container_walk(obj.get_root(), anchorpath )
                self.logger.debug( "Moved anchor %r -> %r" %(oldanchor, self.anchorp ))
                #Verify anchor is an direct owner fo obj - we can do this via it MMpath.
                if repr(obj)[:len(self.parts["anchor"])] != self.parts["anchor"]:
                    raise BiDiLinkTargetMismatch("Anchor not in line owner %s,%s"%(repr(obj),repr(self.anchorp)))
                objpath = repr(obj).split(":")
                self.anchordist = len(objpath) - len(anchorpath) 
                self.parts["anchordist"]=str(self.anchordist)
                if "anchor" in self.parts: del self.parts["anchor"]
            self.anchorp  = self.get_anchor(obj)
            self.logger.debug("Completing ap with anchordist %i", self.anchordist)
            return
        
        #Ok this is a full link do the real work here..
        self.obj = _container_walk(obj.get_root(),self.obj_name)
        try:
            partner = self.get_partner()
        except KeyError:
            #Our partner is not instantiated yet, it's compose will invoke
            #us again so lets just wait.
            self.logger.debug("Early escape - no partner")
            return 
        
        if partner.get_value().get_type() == self.get_type():
            pv = partner.get_value()
            self.logger.debug( "A> %r %r %r" % ( self.anchorp , self.obj , pv.obj))
            if pv.obj is None:
                #The other object hasn't composed properly itself,
                #(probably because we hadn't been created at that point)
                #we should do that then to the do we need moved check.
                pv._compose(partner)
            
            if pv.obj is not obj.get_owner():
                #This is where we handle a moved link from an existing destination,
                # we need to  move the link back to use and back the old destination
                # dangle.
                self.logger.debug( "objs> %r %s "% (partner.get_owner() , self.obj_name))
                self.logger.debug( "partner-> %s %r %r"% (pv.obj ,partner.get_owner() , obj.get_owner()))
                self.logger.debug( "anchor-> %r" % self.anchorp)
                self.logger.debug( "parts-> %r" % self.parts)
                self.logger.debug( "p_parts-> %r" % pv.get_parts())
                self.logger.debug( "anchordist-> %r" % self.anchordist)
                if (self.anchorp is None) and (self.anchordist is None):
                    #Out anchor point does not exist - this is a raw move which has problems.
                    raise BiDiLinkTargetMismatch("No anchor point defined")

                #Do Fixup
                ptarget_str = repr(obj)
                pobj_str    = repr(self.anchorp)
                if self.anchordist is None:
                    self.anchordist  = len(ptarget_str.split(":")) - len(pobj_str.split(":")) 

                pval = MMDLinkValue( parts = {'target': ptarget_str +","+str(self.anchordist)} )  
                self.logger.debug( "pval> %r "%pval.obj_name)
                partner.set_value( pval )             
            else:
                self.logger.debug( "B> %r %r"%(pv.obj , self.obj))
            #Keep a record of our anchor object we need this
            # if our partner moves..
            self.anchorp = pv.obj
            objpath    = repr(obj).split(":")
            anchorpath = repr(pv.obj).split(":")
            self.anchordist = len(objpath) - len(anchorpath) 
        else:
            self.logger.debug("Error detected: %s %s" % ( partner.get_value().get_type() ,self.get_type()))
            raise BiDiCantCreate("type mismatch with partner %s != %s" % ( partner.get_value().get_type() ,self.get_type()))
       
        self.logger.debug("Completing lk with anchordist %i", self.anchordist)
        self.valid = True


    def __copy__(self):
        self.logger.debug("MMDL:__copy__")
        cpy = super(MMDLinkValue,self).__copy__()
        if hasattr(self,"anchordist"):
            self.logger.debug("MMDL:dist->%r",self.anchordist)
            cpy.anchordist = self.anchordist
        return cpy

    def get_object(self, obj = None ):
        """Returns the anchor point of our partner , eg. the object
        to which we point.

        Returns None if disconnected.
        """
        return self.obj

    def get_raw(self,obj = None):
        """Get a simple text represantion of the link"""
        if self.obj is None: return "*AnchorPoint "+repr(self.anchorp)+"*" 
        else:                return repr(self.obj)

    def get_raw_rst(self,obj = None):
        """ Get a ReST represenation of the link for use in documents"""
        objstr = repr(self.obj)
        if self.obj is None: return objstr
        else:                return ":mm:`"+ objstr + "`"

    def get_partner(self, obj = None):
        """Get the attribute which forms the other half of this link"""
        if self.obj is None: return None
        if self.partner_name is None: return None
        return _container_walk(self.obj,self.partner_name)


    def get_anchor(self, obj = None):
        """Get the item further up the ownership heirachy to which our partner
        (if we have one) should point. If not the item to which we refer out partner
        to when we connect."""
        if obj is None: raise ValueError("Anchor is now relative - must pass home object")
        if self.anchordist is None: return self.anchorp
        return _walk_back(obj,self.anchordist)

    def _validate(self, attr = None):
        try:
            return self.partner.get_partner() is attr 
        except AssertionError: return False

