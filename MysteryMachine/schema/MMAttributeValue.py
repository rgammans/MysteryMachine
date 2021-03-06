#!/usr/bin/env python
#   			MMAttributeValue.py - Copyright roger
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
#    with this program; if not, wrobjectite to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# 
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMAttributeValue.py
#
#

import sys

from .MMBase import *
from MysteryMachine.parsetools.grammar import Grammar

import logging
import sys
import types
import operator
import copy as _copy
import codecs
import six

AttrTypes = dict()
TypeLookup = dict()

modlogger = logging.getLogger("MysteryMachine.schema.MMAttributeValue")

ATTRIBUTE_MMTYPE_EXPOINTNAME= "AttributeValueMMType"
ATTRIBUTE_PYTYPE_EXPOINTNAME= "AttributeValuePyType"

#FIXME make a __new__ method.
def CreateAttributeValue(val, copy = True):
    """
    Create an appropriate MMAttributeValue to store val.


    This searches through the registered types to find the most preferred
    MMAttributeValue class to store and value of type(val).

    If a MMAttributeClass is pass as val a copy is created and returned,
    unless copy=False , in which case val is returned.
    """
    if not isinstance(val,MMAttributeValue):
        #Decide on type to use and create object.
        vtype = FindBestValueType(type(val))
        val = vtype(value =val)
    else:
        modlogger.debug( "CAV2:type:%s" % val.__class__.typename)
        modlogger.debug( "CAV2:parts:%s" % val.parts)
        if copy: val= _copy.copy(val)
        modlogger.debug( "CAV2:newparts:%s" % val.parts)

    return val


def GetClassForType(typename):
    if not  typename in AttrTypes:
        from MysteryMachine import StartApp
        with StartApp() as ctx:
            possible_plugins = ctx.GetExtLib().findPluginByFeature(ATTRIBUTE_MMTYPE_EXPOINTNAME,typename)
            ##TODO Sort plugins by preference
            for plugin in possible_plugins:
                ctx.GetExtLib().loadPlugin(plugin)
                #Just load one module to handle the type.
                if typename in AttrTypes: break

    return AttrTypes[typename]


def GetAttributeTypeList():
    rv = [] 
    for name in AttrTypes.keys():
        #Hide private internal types
        if name[0] != '.': rv +=  [ name ]

    typelist = AttrTypes.keys()
    from MysteryMachine import StartApp
    with StartApp() as ctx:
        for plugin_type in ctx.GetExtLib().findFeaturesOnPoint(ATTRIBUTE_MMTYPE_EXPOINTNAME):
            if plugin_type[0] == "." : continue 
            if plugin_type in rv     : continue 
            rv += [ plugin_type ]
    
    return rv

def MakeAttributeValue(type,parts):
   cls = GetClassForType(type)
   return cls(parts = parts)
                              
 
def register_value_type(name,acls,nativelist):
    """
    """
    global AttrTypes    
    AttrTypes[name]=acls
    modlogger.debug("native types %s -> %s",str( nativelist ),acls)
    for typenm in nativelist.keys():
        priority=nativelist[typenm]
        if typenm not in TypeLookup:
            TypeLookup[typenm] = list()
        TypeLookup[typenm].append( (acls, priority) )


def FindBestValueType(atype):
    """
    """
    #Handle base class and more sets in the key get a list 
    # of classes to use for candidate handlers. 
    candidates = list()
    try:
        typelist = atype.__mro__
    except Exception:
        typelist = list(atype)


    #Collect the handlers for the functions.
    for t in typelist:
        if t in TypeLookup:
            candidates += TypeLookup[t]
   

    if len(candidates) == 0:
        from MysteryMachine import StartApp
        with StartApp() as ctx:
            possible_plugins = ctx.GetExtLib().findPluginByFeature(ATTRIBUTE_PYTYPE_EXPOINTNAME,atype.__name__)
            for plugin in possible_plugins:
                ctx.GetExtLib().loadPlugin(plugin)

                #Just load one module to handle the type.
 
        #Collect the handlers for the functions (again).
        for t in typelist:
            if t in TypeLookup:
                candidates += TypeLookup[t]

    modlogger.debug("candiate attrval's %s" % candidates)
    rlist = sorted(candidates,key=operator.itemgetter(1),
                    reverse= True )
    
    if len(rlist) == 0: raise TypeError("No schema type for %s" % atype)
    return rlist[0][0]


class _AttrMeta(type):
   def __init__( self, name , bases, ns):
        super( _AttrMeta , self).__init__(name,bases,ns)
        if name != "MMAttributeValue":
            register_value_type(self.typename,self,self.contain_prefs)
    
#FIXME Remove and replace reference to appropriate exception class
class Error():
    pass


#__metaclass__ = _AttrMeta
@six.python_2_unicode_compatible
class MMAttributeValue (six.with_metaclass(_AttrMeta,SchemaCommon) ):
  """
   This is the base class of MMAtributes actual value. Each 'type' of Attribure
   should have it's own speciallisation of this class. It is through this object
   that values are directly manipulated.

   An attribute value must consist of one or more string parts, each part should
   have a unique name in the MysteryMachine namespace.

  :version:
  :author:
  """

  """ ATTRIBUTES
  base  (private)
  attr  (private)
  """
    

  def __init__(self,*args, **kwargs):
    self.parts = {} 
    self.value = None
    if 'parts' in kwargs:
        self.parts=kwargs['parts']
        partsmap = { }
        for k in self.parts.keys():
            #Check k is valid - will throw if not.
            newk = self.canonicalise(k)
            if k != newk:
                partsmap[k] = self.canonicalise(k)
                if newk in self.parts: raise ValueError("%s and %s conflict" % (k ,newk))
            
        for oldkey , newkey in partsmap.items():
            self.parts[newkey] = self.parts[oldkey]
            del self.parts[oldkey]
  
    if 'value' in kwargs:
        self.value=kwargs['value']

    self.exports=[ "get_raw", "get_raw_rst" ]
    self.logger = logging.getLogger("MysteryMachine.schema.MMAttributeValue")

  def __repr__(self):
    """

    @return string :
    @author
    """
    return str(self.__class__)+"(\""+self._decode_content()+"\")"

  def __str__(self):
    return self._decode_content()


  def _decode_content(self, obj = None):
    """ Internal function 
    returns an intermediate str/unicode representation.
    
    This is so __str__ and get_raw_rst can share an implementaion
    at the base class; but is not intended to be overrridden or used
    elsewhere.
    """
    if obj is not None:
        encoding = obj.get_root().get_encoding()
        raw = self.get_raw(obj = obj)
    else:
        # Round trip through the unicode escape codec to map any 
        #non-ascii characters
        raw = six.text_type(self.get_raw(), "unicode_escape")
        rawlist = raw.split("\n")
        raw = b""
        for ele in rawlist:
            raw += ele.encode("unicode_escape")
            raw += b'\n';
        raw = raw[:-1]
        encoding = 'ascii'

    return six.text_type(raw,encoding)

  def get_raw(self, obj = None):
    """
    Gets unprocessed rst contents of attribute.       

    @return bytes :
    @author
    """
    self.logger.debug( str(self.__class__))
    self.logger.debug( self.parts)
    result = b"\n".join([x[1] for x in  sorted(self.parts.items())])
    self.logger.debug( "raw-->%s<--" % result)
    return result

  def get_raw_rst(self, obj = None):
    """Get raw contents suitable for parsing by the markup parser.

    :returns str/unicode:
    """
    return self._decode_content(obj)

  def get_parts(self):
    return self.parts

  def get_type(self):
    return self.__class__.typename 
 
  def _validate(self,attr = None):
    """

    @return bool :
    @authorMysteryMachine/schema/MMAttribute.py:
    """
    ok = True
    #Test we can parse succesfully, and valid part naems but no more.
    try:
        for k in self.parts.keys():
            if k != self.canonicalise(k):
                ok = False
                #exit early
                return ok

        if attr is None:
            grammar.parse(self.get_raw_rst())
        else:
            attr.get_ancestor().parser.ProcessRawRst(self.get_raw_rst())
    except Exception:
        ok = False
    return ok

  def assign(self,other):
     """
     Handle self=other calls.

     The aim of this is to allow custom cleverness as the
     value are updated. The aim is to be able to find the
     appropriate way of store the change. 
     This is important in the more advanced value types.
     
     Pre: self and other are of the same type. 
     Post:str(self) == str(other) 
     """
     if isinstance(other,MMAttributeValue):
         if self.__class__ is other.__class__:
             self.parts =  _copy.copy(other.parts)
         else:
             raise TypeError(type(other))
     else:
         #TODO Clever code here to handle appropriate value
         # setting. Raise error while unimplemented. 
         raise TypeError()

  def can_assign_to(self,other):
    """
    Provides an opporitunity to  raise and prevent the 
        other = self
    assignment from working"""
    return True

  def __copy__(self):
     self.logger.debug( "AV_c:Entered")
     return self.__class__(parts = _copy.copy(self.parts))


  def __eq__(self,other):
     if not isinstance(other,MMAttributeValue): return False 
     return self.get_type() == other.get_type() and self.get_parts() == other.get_parts()

  def __hash__(self):
     #FIXME: Identical valued but distict obj return the same hash
     return hash(("MMAttributeVal" , self.get_type() , tuple(sorted(self.get_parts().items())),{}),)


class MMAttributeValue_Raw(MMAttributeValue):
    """
    A minimalistic attribtue value class used for
    certain special purposes within the schema
    """
    typename = "_raw"
    contain_prefs = {}

    def _compose(self,obj):
        """Called by some containers for any final inplace optimisations neeeded"""
        pass

class MMAttributeValue_BasicText(MMAttributeValue):
    """
    A single Macro part value type.

    This type is appropriate for String values.
    """
    typename      = "simple"
    contain_prefs = { six.binary_type: 100 }


    def __init__(self,*args,**kwargs):
        ##Set a default value to be overwritten 
        parts = kwargs.get("parts")
        if not parts:
            kwargs["parts"] = {'txt':''}
        MMAttributeValue.__init__(self,*args,**kwargs)
        #Get passed in value.
        if self.value is not None:
            self.parts["txt"] = six.binary_type(self.value)

    def _compose(self,obj):
        if obj is not None:
            encoding = obj.get_root().get_encoding()
            decode = codecs.getdecoder(encoding)
            #Ensure text values can be transcribed in the system encoding
            # will rasise an exception we will propagate if not decodeable.
            decode(self.parts["txt"])

@six.python_2_unicode_compatible
class MMAttributeValue_UnicodeText(MMAttributeValue):
    """
    A single Macro part value type.

    This type is appropriate for String values . This type
    returns unicode as an appropriate type and stores in values in utf8
    """
    typename      = "simple_utf8"
    contain_prefs = { six.text_type: 120 }


    def __init__(self,*args,**kwargs):
        MMAttributeValue.__init__(self,*args,**kwargs)
        #Get passed in value.
        if self.value is not None:
            self.parts["txt"] = self.value.encode("utf8")

    def get_raw(self, obj = None):
        """
        Gets unprocessed rst contents of attribute.       

        @return bytes :
        @author
        """
        return self.parts["txt"]

    def __str__(self):
        return self.get_raw_rst()

    def get_raw_rst(self, obj = None):
        """Get raw contents suitable for parsing by the markup parser.

        :returns str/unicode:
        """
        return six.text_type(self.get_raw(obj),"utf8")

    def _compose(self,obj):
        pass

class MMAttributeValue_MMRef(MMAttributeValue):
    """
    This Value typeobjct store reference to other
    attributes or objects insidea MMObject system.
    """
    typename = "ref"
    contain_prefs = { MMBase: 50 }

    def __init__(self,*args,**kwargs):
         ##Set a default value to be overwritten 
        parts = kwargs.get("parts")
        if not parts:
            kwargs["parts"] = {'obj':b''}
        super(MMAttributeValue_MMRef, self).__init__(*args,**kwargs)
        if isinstance(self.value,MMBase):
            #Get string represenation of the object.
            #TODO Store object here so it cached.
            self.parts['obj'] = repr(self.value).encode('ascii')
            
            self.logger.debug( "MMA-O:init->%s<--" % self.parts['obj'])
        #All ok.
        self.exports += [ "get_object" ]

    def _compose(self,obj = None):
        if not self._validate(obj): pass# raise Error()    
        #pass

    def _validate(self, obj = None):
        objref = None
        #try:
        objref = self.get_object( obj )
        #except exceptions.Exception , e:
        #    logging.warn(e.msg())
        #    objref = None
        return not objref is None

    def get_object(self, obj = None ):
        """
        This method may raise and exception if the
        own_obj is not valid or the value will not validate.
        """
        ##TODO Consider caching the return result.

        self.logger.debug( "refobj->%r<--" %obj )

        # Get the reference as a unicode string
        # as we use the standard parser to decode
        # we need it to no longer be a bytes object ( in py3)
        # Utf8 is in py3 our standard encoding althogu
        # thi should ahve now non-ascii codes.
        pstr = six.text_type(self.get_raw(obj),'utf8')

        #Special case answer.
        if pstr == "": return obj.get_root() 

        objref = None
        self.logger.debug( "MMA-O:go:pstr  ->%r<--" % pstr)
        g = Grammar(obj)
        objref = g.parseString(pstr)[0]
        self.logger.debug( "ret = %r, class = %r" % (objref , objref.__class__ ))
        return objref

    def get_raw_rst(self,obj = None):
        pstr = six.text_type(self.get_raw(obj),'utf8')
        return ":mm:`"+  pstr + "`"


class MMNullReferenceValue(MMAttributeValue):
    """
    This class can only hold a single value. None.
 
    It should act like MMRef but always return None
    from get_object(). It should only have a single part
    which is always empty.
    """
    typename = "null"
    contain_prefs = { None: 100 }

    def __init__(self,*args,**kwargs):
        super(MMNullReferenceValue, self).__init__(*args,**kwargs)
        self.parts = { 'value' : b'' } 
            
        self.exports += [ "get_object" ]

    def _validate(self, obj = None):
        return True

    def get_object(self, obj = None ):
        return None 

    def getSelf(self):
        #Function need especially for MMObject.set_parent.
        return None
 
    def get_raw_rst(self,obj = None):
        return ""

@six.python_2_unicode_compatible
class ShadowAttributeValue(MMAttributeValue):
    
    """
    This class is a place holder value for inherited attributes.

    We need to create an MMAttribute object for those object so that 
    they are always evaluated in the correct context , however they cannot
    share the value object as that has a hard to fix failure mode when
    the inherited value is updated. If the update creates a new value object
    any inherited attributes do not piclk up the new value as they are still
    pointing at the old value.

    This class is designed to fix that problem by handling the forwarding directly.

    Note that the class only hold a reference to it's owning object as that
    means it doens't impact on the GC at all.

    Attempts to de-reference Value where it's target has gone away,
    or no longer contain a matching attribute raise ReferenceError
    """

    typename = ".inhertitance_shadow"
    contain_prefs = { }

    def __init__(self,*args,**kwargs):
        super(ShadowAttributeValue, self).__init__(*args,**kwargs)
        self.obj       = kwargs.get("object",None)
        self.attrname  = kwargs.get("attrname","")
        self.exports   = self._get_target().exports
        self.logger    = logging.getLogger("MysteryMachine.schema.MMAttributeValue.ShadowAV")
        #self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Created forward for %s[%s] " % ( repr(self.obj), self.attrname) )


    def shadow_deref(self,):
        """Dereference shadow - useful in some rare instances where shadows
        work slighty differently"""
        p = self._get_parent()
        #If there is no parent raise ReferenceError
        #to indicate invalid attribute. - the same
        #as would happen if the parent lost
        #the atribute.
        if not p: raise ReferenceError(self.attrname)

        try:
            t = p[self.attrname]
        except KeyError  as e: raise ReferenceError(e.message)

        return t


    def _compose(self,obj = None):
        #Disable this as our target need to trigger compose not us!
        pass

    def __getattr__(self,attrname):
        self.logger.debug(attrname)
        fwd_to = getattr(self._get_target(),attrname)
        return fwd_to

    def _get_target(self):
        return self.shadow_deref().get_value()

    def _get_parent(self):
        p = self.obj.get_parent()
        return p 
        

    def __copy__(self):
        #return a copy of the object we are proxying - it want you really want 
        #anyway
        return _copy.copy(self._get_target())

    def __str__(self):
        return six.text_type(self._get_target())
        
    def get_raw_rst(self, obj = None):
        self.logger.debug("%s[%s].raw_rst ( obj = %s ) "% (  repr(self.obj), self.attrname , repr(obj) ))
        return self._get_target().get_raw_rst(obj)


    def get_raw(self, obj = None):
        return self._get_target().get_raw(obj)

    def get_parts(self):
        return self._get_target().get_parts()

    def get_type(self):
        return self._get_target().get_type()
