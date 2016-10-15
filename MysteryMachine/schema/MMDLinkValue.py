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
    CreateBiDiLink(player1,"character",character2,"player")

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


Shadowing bidilinks
-------------------

# Anchorpoints keep the same relative reference, so an attribute or list
  containing an anchor point to it home object, continues to point to it 
  ownin object after inheritance 9ie. move with the inheithance).

# Connecting links continue to point forwrd, but their anchor is based on the
  object which owns them.

"""

from __future__ import with_statement
from MMAttributeValue import MMAttributeValue
from MMAttribute import MMAttribute, MMUnstorableAttribute

from MysteryMachine.parsetools.grammar import Grammar
from MysteryMachine.schema.Locker import ValueReader,ValueWriter

import copy as _copy
import weakref
import thread

import logging
import weakref
import itertools

logger    = logging.getLogger("MysteryMachine.schema.MMDLinkValue")
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
#    logging.getLogger("MysteryMachine.schema.MMDLinkValue").debug("walking from %r to %s ",root,path)
    if path is None: return None
    node = root
    for element in path:
        if element != "":
            node = node[element]
        if node is None: break
    return node


def _walk_back(obj,dist):
    for i in range(dist): obj = obj.get_ancestor()
    return obj 


def _measure_path_diff(frm,to):
    """Meause the patch distnce from 'frm' to 'to' """
    frm_path = frm.get_nodeid().split(':')
    to_path =  to.get_nodeid().split(':')

    count = 0
    for f,t in itertools.izip_longest(frm_path,to_path):
        if count >0 and t is not None: RuntimeError("invalid path %r"%to_path)
        if f is not None and t is not None:
            if f != t: raise RuntimeError('%r is not a parent of %r'%(frm,to))
            #Don't count common elements
            else: continue

        if f is None: break
        if t is None: count += 1

    logger.debug(" %r -> %r = len %s",frm,to,count)
    return count


def _resolve_value(obj,):
    """When we look at our partners value we need to know the 
    value is associated directly with the partner and isn't a shadow
    obj. If it is we need to vivify a actuall valueon the object."""


    val = obj.get_value()
    if val.get_type() !=  _value_typename:
        raise TypeError("Can only ConnectTo bidilinks")

    if obj.is_shadow(): 
        obj.set_value(_copy.copy(val))
        val = obj.get_value()

    return val

def CreateBiDiLink(obj1,attrname1,obj2,attrname2):
    """
    Create a bidilink between objects obj1 & obj2.

    Specifically obj1[attrname1] contains a link to obj2, and
    Specifically obj2[attrname2] contains a link to obj1.

    This links try to maintain consisency if they are moved etc.
    """
    baseref1,basepath1_elements = _process_obj_and_attr(obj1,attrname1)
    baseref2,basepath2_elements = _process_obj_and_attr(obj2,attrname2)

    baseref2[basepath2_elements[-1]] = CreateAnchorPoint(obj2)
    baseref1[basepath1_elements[-1]] = CreateAnchorPoint(obj1)
    baseref1[basepath1_elements[-1]] = ConnectTo( baseref2[basepath2_elements[-1]] )

#@Writer
def ConnectTo(attribute):
    """
    This functions returns a half-link so that it can be used to 
    connect two anchor point. That half link will be a partner for
    the passed attribute.

    You use this by assigning an existing anchop point to the result
    from this function.
    """
    logger.debug( "Cti init>?")
    if not isinstance(attribute,MMAttribute):
        raise TypeError("Can only ConnectTo an MMAttribute")
    if attribute.get_value().get_type() !=  _value_typename:
        raise TypeError("Can only ConnectTo bidilinks")

    anchorname = repr(attribute.get_anchor())
    attrname   = repr(attribute)
    if  attrname[:len(anchorname)] != anchorname:
        raise ValueError("attribute not decesended from anchor %s /< %s"%(anchorname,attrname))

    foreign   =  attrname[len(anchorname)+1:]

    logger.debug( "CTi: %s , %s, %s",anchorname, attrname,foreign)

    return MMDLinkValue(target = attribute.get_anchor() , 
                        foreign=foreign,

    ## TODO Doesm't this change brak list container mode see __init__

#                        foreign=foreign,
                        mode = "connect_to_seed",
    ) 

def CreateAnchorPoint(obj):
    """
    Creates an anchor point for object obj which can be turned into a
    complete link later. (ie. with ConnectTo() )
    """
    return MMDLinkValue(anchor = obj ,mode = "anchor_point_seed")


class MMDLinkValue(MMAttributeValue):
    typename =  _value_typename
    contain_prefs = {}
    def __init__(self,*args,**kwargs):
        #FIXME
        """FIXME  Docuemnt this even if it is to say don;t use."""
        super(MMDLinkValue,self).__init__(*args,**kwargs)

        self.logger    = logging.getLogger("MysteryMachine.schema.MMDLinkValue")
        self.obj            = kwargs.get("target",None)
        partner_name        = kwargs.get("foreign",None)
        self.anchorp        = kwargs.get("anchor",None)
        self.mode           = kwargs.get("mode",'')
        self.anchordist     = None


        if len(self.parts) == 0:
            #Validate we have enough data..
            # Handle anchopoint init first...
            if self.anchorp is None:
                if self.mode == 'connect_to_seed':
                    #Create member variables we can use..
                    self.partner_path =  repr(self.obj).split(":") + partner_name.split(":")
                    self.parts["target"] =  repr(self.obj)+":" + partner_name +", 0"
                elif self.mode == 'anchor_point_seed':
                    self.parts["anchordist"]="0"
                    self.partner_path = None
                else:
        #            ###Fallback to stuff
                    #if self.anchordist:
                    self.parts["anchordist"]='1'#str(self.anchordist)
                    self._process_parts()
        else:
             self.mode = 'init_from_parts'
             self._process_parts()

        self.exports += [ "get_object", "get_partner" , "get_anchor" ,'disconnect']
        self.valid = False 
        self.in_assignment = False
        if ( (self.mode[:10] != 'connect_to' )  and
             ( self.anchorp is None and self.anchordist is None)):

            self.mode = "copied_initialised!"

    def can_assign_to(self,other):
        if other.get_type() != _value_typename:
            raise TypeError("Can only ConnectTo bidilinks")
    
    def assign(self,other):
      """Called by MMAttribute when an value assignment occurs - not exported

        valid cases.
            other is an newly initialised Anchor point.
            other is the result of connectTo from an anchorpoint
            other is the result of a connectTo  already connected Link object.
            other is a attribute being moved!
          #
           Invaldid cases wherw dircet assinemtn as been tried. 

      """
      self.logger.debug( "in assign")
      if self.__class__ is other.__class__:
          self.valid = False
          with _member_guard(self,"in_assignment") as assign_guard:
            self.logger.debug( "got inassign lock")
            
            if other.mode == 'anchor_point_seed':
                #Two sub cases here, we are anchorpoint, or we are connected
                self.old_partner_path = self.partner_path
                self.partner_path = None 
                self.anchordist = None
                self.anchorp = other.anchorp
                self.mode = 'anchor_point_gestate'
                self.logger.debug( "APG: %s | %s | %s",self.parts,other.parts,self.partner_path)
                self.parts= other.parts
            elif other.mode == 'connect_to_seed':
                self.parts =  { 'target' :other.parts['target'] }
                assert self.anchorp or self.anchordist
                self.logger.debug( "connect_to_seed: %r | %r | %s | %s", self.anchorp,  self.anchordist, self.partner_path,other.partner_path)
                self.mode = 'connect_to_gestate'
                self.old_partner_path = self.partner_path
                self.partner_path = other.partner_path
            else:
                if other.parts == self.parts: return
                #Native assiginment/or move.
                self.logger.debug("\tother %s %r %r",other.mode,self.parts,other.parts)
                self.old_partner_path = self.partner_path
                self.partner_path = other.partner_path
                self.parts = other.parts
                if 'target' in other.parts:
                    self.mode = 'connect_to_gestate'
                else:
                    #Some wort of Anchorpint move, do simple valid test
                    if other.anchorp is not None:
                        self.mode = 'anchor_point_gestate'
                        self.anchorp = other.anchorp

    def _process_parts(self):
       self.logger.debug( "_pp>%s"%self.parts)
       if "target" in self.parts:
            attributename,sniplen = self.parts["target"].rsplit(",",1)
            attributename = attributename.split(":")
            #if int(sniplen) > 0: we used to ensure anchordist was never 0
            self.anchordist = int(sniplen)
            self.partner_path=attributename
       else:
            self.obj= None
            self.partner_path = None
            if "anchor" in self.parts:
                self.anchordist = None
                if repr(self.anchorp) != self.parts["anchor"]: self.anchorp = None
            if "anchordist" in self.parts:
                self.anchordist = int(self.parts["anchordist"])
                #print "SD_>",self.anchordist


    @ValueWriter
    def disconnect(self, obj = None):
        obj.set_value(CreateAnchorPoint(self.get_anchor(obj=obj)),copy = False)
    
    @ValueWriter
    def _connect_to(self, target, **kwargs):
        """Internal function set partner apth, and clears exsitign partner"""
        obj = kwargs.get('obj',None)
        path = kwargs.get('path',self.partner_path)
        self.logger.debug( "connect_to mode: %r | %r | %r | %r | %r",path,obj,target,self.anchordist,self.parts)

        #Get partner if defined.
        existing_partner = None
        if path:
            existing_partner =  _container_walk(target.get_root(),path)

        if  existing_partner is not target:
            if existing_partner is not None:
                if not isinstance(obj,MMUnstorableAttribute):
                    existing_partner.disconnect()

            ##The int() wrapping is desgin to cause a fastfailure if anchordist is 
            # invalid
            self.parts['target'] = repr(target) +","+str(int(self.anchordist))
            try:
                del self.parts['anchordist']
            except KeyError:pass
            self._process_parts()
        else:
            #Self connect is a special case and we need to repair the target part broken by assign (lear the anchordist)

            ##The int() wrapping is desgin to cause a fastfailure if anchordist is 
            # invalid

            self.parts['target'] = ":".join(self.partner_path) +","+str(int(self.anchordist))


    def _compose(self,obj = None ):
        self.logger.debug("compose_moode: %r | %r | %r | %r | %r | %r",self.mode,obj,type(obj.get_value()),self.anchorp,self.anchordist,self.parts)
        if not self.mode:
            #Iniitialise from parts.
            return

        if obj is None: raise BidiCantCreate("Cannot compose as owned by None") 
        self.logger.debug( "%s _compose (%r,%s)" % (object.__repr__(self) ,obj, self.parts))
        #Now we have a handle on the system find our objects etc,

        #Verify anchordist, and correct parts if an anchorpoint
        # this is needed for some unstoreable cornercases
        if self.anchorp is not None:
            self.anchordist = _measure_path_diff(obj,self.anchorp)
            if 'anchordist' in self.parts:
                self.parts = {'anchordist' : str( self.anchordist) }


        if self.mode == 'connect_to_gestate':
            npartner =  _container_walk(obj.get_root(),self.partner_path)
            self.anchor = self.get_anchor(obj = obj)
            #We set us and out parnter to mutually point at each other.
            # it is importat to move ourselves first, to chortcut recursion.
            self._connect_to(npartner,path = self.old_partner_path, obj=obj)
            # buyt only do our end if we are 'unstorable'
            if not isinstance(obj,MMUnstorableAttribute):
                _resolve_value(npartner)._connect_to(obj,obj = npartner)

        ##Q? Can  connectd link by copied_initialised -because that's not handled?
        elif self.mode in ( 'anchor_point_gestate' , 'copied_initialised!'):
            #
            # This state is create when we are assign an anchorpoint, but must wait
            # for compose to find an anchordist for the parts.
            #
            # If we were connected before an assignment changed we must alway
            # reset our old partner back to anchor point state.
            #
            oldp =  _container_walk(obj.get_root(),self.old_partner_path)
            if not isinstance(obj,MMUnstorableAttribute):
                if oldp is not None:
                    oldp.disconnect()

            self.anchordist = _measure_path_diff(obj,self.anchorp)
            self.parts = {'anchordist' : str( self.anchordist) }
            self._process_parts()

        else:
            ###There is a awkward corner case here that our partner doesn't
            #  point back to us.
            npartner =  _container_walk(obj.get_root(),self.partner_path)
            if npartner is not None:
                npartner_partner =  _container_walk(obj.get_root(),_resolve_value(npartner).partner_path)
                if npartner_partner is not obj and  not isinstance(obj,MMUnstorableAttribute):
                    _resolve_value(npartner)._connect_to(obj,obj = npartner)



        #elif self.mode == 'copied_composed':
        #    assert False

        self.mode = 'composed'

    def __copy__(self):
        #print "cpy",self.mode
        mode = 'copied_'+self.mode#[:-4]+"gestate"
        self.logger.debug("copy",self.mode,self.parts)
        ##Uncomment this for different behaviour
        #FIXME WHY!
        #x=str(self.anchorp)
        cpy = self.__class__(parts=_copy.copy(self.parts),mode = self.mode)
        cpy.anchorp = self.anchorp
        cpy.anchordist = self.anchordist
        ## These next three lines seem to have no effect, so they are commented out!
        #if hasattr(self,'old_partner_path'):
        #    cpy.old_partner_path = self.old_partner_path
        #else:
        cpy.old_partner_path = None
        return cpy




    def get_object(self, obj = None ):
        """Returns the anchor point of our partner , eg. the object
        to which we point.

        Returns None if disconnected.
        """
        if self.obj is None:
            obj = self.get_partner(obj)
            if obj is not None: self.obj = obj.get_anchor()

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
        if obj is None: obj = self.obj
        if obj is None: return None
        if self.partner_path is None: return None
        return _container_walk(obj.get_root(),self.partner_path)


    def get_anchor(self, obj = None):
        """Get the item further up the ownership heirachy to which our partner
        (if we have one) should point. If not the item to which we refer out partner
        to when we connect."""
        if obj is None: raise ValueError("Anchor is now relative - must pass home object")
        if self.anchordist is None:
            if self.anchorp is not None: return self.anchorp
            ##NOTE If the line below is raising KeyError('anchor') the problem occured
            #      before we got here!
            #      For instance assigned ConnectTo(..)'s result to  a non Dlink object is 
            #      one way to cause this, although I intend to raise a custom error for this
            #      ealier in the control path!
            else: return _container_walk(obj.get_root(),self.parts["anchor"].split(":"))

        ##If we are connected (partner_path is not None) and  a shadow, deref the shadow.
        if obj.is_shadow() and self.partner_path is not None:
            obj = obj.get_value().shadow_deref()

        return _walk_back(obj,self.anchordist)

    def _validate(self, attr = None):
        try:
            return self.partner.get_partner() is attr 
        except AssertionError: return False

