#!/usr/bin/env python
#   			MMListAttribute.py - Copyright Roger Gammans
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

from MysteryMachine.schema.MMAttributeValue import MMAttributeValue ,MakeAttributeValue , CreateAttributeValue 


#If we deprecated py2.5 this mess can be replaced
#with from 'itertools import izip_longest'
import itertools
import functools
import six

# izip_longest only exists from2.6 onwards 
# but  map(None,.) 
try:
    zip_longest = itertools.izip_longest
except Exception:
    zip_longest = itertools.zip_longest

try:
    dummy = xrange
except NameError:
    #Xrange not defined; define it to match range
    # which is a py3 equivalent
    xrange = range


class MMListAttribute(MMAttributeValue):
    """
    An attribute value type which provides an ordered list of strings.
    """
    typename = "list"
    contain_prefs = { list: 100 }

    def __init__(self,*args,**kwargs):
        ##Set a default value to be overwritten 
        parts = kwargs.get("parts")
        if not parts:
            kwargs["parts"] = {'0element': b''}

        super(MMListAttribute,self).__init__(self,*args,**kwargs)
        self.special = ["0element"]
        self.uncomposed = {}
        if self.value is not None:
            #Value overrides parts, but create a dummy part for emptylists
            self.parts = { "0element" : b'' }
            for item in self.value:

                self.logger.debug( "ila  %r",item)
                self.append(item)

        self.exports+= ["GetStableIndex", "__iter__" , "__contains__", 
                        "__len__", "__getitem__","__setitem__","__delitem__",
                        "count","extend","insert","append" ]

    def _elementkeys(self):
        ##Returns the elements of the array - remove any special parts
        for k,v in self.parts.items():
            if k not in self.special:
                    yield k

        for k in self.uncomposed.keys():
            yield k


    def _elementvalues(self):
        ##Returns the elements of the array - remove any special parts
        for k,v in self.parts.items():
            if k not in self.special:
                    yield v

        for v in self.uncomposed.values():
            yield self._convert_to_str(None,v,None)


    def __copy__(self,):
        cpy = super(MMListAttribute ,self).__copy__()
        cpy.uncomposed = dict(self.uncomposed)
        return cpy

    def __contains__(self,val , obj = None ):
        val = self._convert_to_str(None,val,obj)
        self.logger.debug("list CF: %s | %s ",val, list(self._elementvalues()))
        return val in self._elementvalues()

    def __len__(self, obj = None ):
        return len(list(self._elementkeys()))

    count = __len__
    def GetStableIndex(self,index,obj = None):
        try:
            index=int(index)
        except ValueError:
            return index
        return sorted(self._elementkeys())[index]

    def __delitem__(self,index ,obj = None):
        key = self.GetStableIndex(index,obj)
        if key in self.uncomposed:
            del self.uncomposed[key]
 
        if key in self.parts:
            del self.parts[key]
        if obj is not None: obj._do_notify()

    def __getitem__(self,index , obj = None):
        key = self.GetStableIndex(index,obj)
        if key in self.uncomposed:
            return self.uncomposed[key]
        return self._convert_to_val(key,self.parts[key],obj)        

    def __iter__(self, obj = None):
        for key in xrange(len(self)):
            yield key 

    def __setitem__(self,index,value , obj = None):
        key = self.GetStableIndex(index,obj)
        self._write(key,value,obj)

    def extend(self, iter , obj = None):
        for i in iter:
           self.append(i,obj)

    def insert(self,index,item , obj = None):
        key_b = self.GetStableIndex(index)
        klist = sorted(self._elementkeys())
        index = klist.index(key_b)
        if index >0:
            key_a = klist[index-1]
        else:
            key_a = None 
    
        key   = str(_Key(key_a).between(key_b))

        if obj is not None:
            obj[key] = item
            obj._do_notify()
        else:
            self.uncomposed[key] = CreateAttributeValue(item)



    def append(self,item, obj = None):

        lastkey = None
        try:
            lastkey = sorted(self._elementkeys(),reverse=True)[0]
        except Exception:
            pass
 
        lastkey = _Key(lastkey)
        lastkey = lastkey.next()
        lastkey = str(lastkey)

        if obj is not None:
             obj[lastkey] = item
             obj._do_notify()
        else: 
            self.uncomposed[lastkey] =  CreateAttributeValue(item)


    #
    #
    # Parts are not defined to be set until _compose has completed
    #   which applies to subojbects as well
    #
    # This means append(x, obj=None) - must stash repose in another
    #    array then bring them out into parts after call _compose on them!
    #
    #  which means having a suppliemnetal dict for not fully included items!

    def _compose(self, obj ):
        done = []
        for k,i in self.uncomposed.items():
            if obj:
                tobj = obj[k]
            else:
                self.logger.debug("compose without an obj for %s"%k)
                tobj = None
            self.logger.debug( "L compose %s %r %r",i,obj,tobj)
            i._compose(tobj)
            self._write(k,i,obj)
            done += [ k ]
        for k in done:
            del self.uncomposed[k]

    def _write(self,key,value,obj = None):
        self.parts[key] = self._convert_to_str(key,value,obj)


    def _convert_to_str(self,key , v, obj = None):
        #Force value Into an MMAttributeValue Object
        v = CreateAttributeValue(v,copy = False)
        l =len(v.get_parts())
        if l > 1:
            raise TypeError("MMListAttribute only supports single part values %s",v.get_parts().keys())
        elif l == 0:
            return v.get_type()
        else: #l == 1
            value = next(iter(v.get_parts().items()))
            #We can safely use ':' as a seperator as it isn't
            # allowed in  type or part names.
            return ( v.get_type().encode('ascii')+
                     b":"+value[0].encode('ascii')+
                     b":"+value[1] # Should already be bytes
                    )

    def _convert_to_val(self, key ,v, obj = None):
        #Limit split so that we don't lose data after ':' in the 
        #value.
        data = v.split(b":",2)
        if len(data) == 3:
            parts =  { six.text_type(data[1],'ascii'): data[2]}
        else:
            parts = {}
        return MakeAttributeValue(six.text_type(data[0],'ascii'),parts = parts )



class _Key(object):
    """
    Encodes the actually logic used for generating dict keys for
    our ordered list.
    """
    """
    This class uses a tree analogy to create sortable strings for
    our dict elements.
    On each subtree self.order[0] and self.order[-1] are reserved to
    be immediately extended creating a new subtree
    Under normal circumstances we try to bisect the difference between the
    end (self.order[-1] in the case of append) and the start items.

    However if the two elements are 'adajenct' we create another subtree
    (append another character) and start from the center there.

    eg. (using a,b,c,d,e) as our symbols. 'a' and 'e' are reserved as
        our endpoints. and we start with 'c'
        
        append           -> c
                            c
        append           -> c , d
                            c--d
        insert(c)        -> c , cc ,d
                       c--d
                       |
                       cc
        insert(c)        -> c, cb , cc, d
                       c--+--d
                       |
                    cb-+-cc
        insert(c)        -> c , cac,cb,cc,d
                       c--+--d
                       |
                 (ca)-cb-+-cc
                  |
                 cac

    Note: We can't use the ca node as it is impossible to insert anything
          between the 'c' node and the 'ca' node.
    """
    #This _must_ be longer than three elements, otherwise the algorythm
    # cant always guarantee to find a between. Ideally it should be 3**n .
    #But I've compromised on 26 - one short of the ideal for n=3, becuase a-z
    # have a stable sort order across most (hopefully all) locales.
    order = [  ] 
    for i in range(26): 
        order.append(chr(ord('a') + i))

    #VV ---  Simple to trick to ensure algo requiremnt is true --- VV
    order = sorted(order)
    ##################################################################

    def __init__(self,value = None):
        self.abet =  self.__class__.order
        self.value = value
        if self.value is None:
            self.value = ''
 
    def __str__(self):
        return self.value

    def between(self,other):
        """
        Return a key half way between this and other - assuming no other 
        intermediate keys exist in the tree.
        """
        ans = []
        for lo,hi in zip_longest(self.value,other):

            if lo is None: lo = self.abet[0]
            if hi is None: hi = self.abet[-1]

            if lo == hi:
                #The nodes are on the same subtree - so the answer will be too.
                ans.append(lo)
            else:
                #At this point we have found a difference between the subtrees which
                #contain the nodes.
                #But consider:-
                #           -b---------d-
                #            |         |
                #        bb--bc--bd    dc-dd
                #
                # I think it is sensible to return 'c' for insert_after('bd')
                new = self.abet[ ( self.abet.index(hi) + 
                                   self.abet.index(lo) ) //2 ]
               
                #Check is unique and not reserved.
                if hi != new and lo != new and new !=0 and new != len(self.abet)-1:
                    ans.append(new)
                else:
                    #New subtree - ensure goes in a good place new == hi is the
                    #              only possible problem so lets trap it.
                    #      (It shouldn't occur due to integer division but..)
                    if new == hi: new=lo
                    ans += [ new , self.abet[len(self.abet) // 2] ]
                
                break

        return self.__class__("".join(ans))

    def next(self):
        """
        The implicit assumption is that this is the last key in the squenence.
        
        We need to return another key somewhere later in the sequence. We could
        use between() here but that wouldn't make the most use of the end element. 
   
        So we use a slightly customized algorithm to do between(self,self.abet[-1])
        """

        if self.value == '':
            #Special case to handle empty string
            return self.__class__(self.abet[len(self.abet) // 2])

        ans = [ ]
        got = False
        for digit in self.value:
            if digit != self.abet[-1]:
                # Find digit 1/2 to the end rounding up (allowing us to use the end node)
                new = self.abet[ ( self.abet.index(digit) +
                                   len(self.abet)-1 )  // 2 ]
                
                #Run out of space on this subtree/node
                if new == digit:
                    # Last node on tree: - 
                    #   use Create mid point in new subtree
                    ans += [self.abet[-1] , self.abet[len(self.abet) // 2] ]
                else:
                    ans += [ new ]
                #No need to add any more subtrees - so exit here.
                got = True
                break
            else:
                #On an end subtree move down and consider it alone...
                ans += [ digit ]
        
        #We must have finished succesfully as got can only be false if
        # if we have an unbroken sequenence of self.abet[-1]'s but we 
        # never generate such a sequence. 
        assert(got)
        return self.__class__("".join(ans))

