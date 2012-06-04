#!/usr/bin/python

###Grammar stuff
from pyparsing import Forward, OneOrMore, QuotedString , Literal, Word, alphas , nums , stringEnd

import logging
import sys
from MysteryMachine.Exceptions import NullReference,NoAttribute

modlogger = logging.getLogger("MysteryMachine.parsetools.grammar")

#Tokens
seperator  =   Literal(":")
queryOp    =   Literal("?")
equalsOp   =   Literal("=")
notequalsOp=   Literal("!=")

#Characters to avoid ?,:,/,!,= (eg other literals)
identifier =   Word("-" + "_" + alphas + nums)
LiteralVal =   QuotedString('"') 


def Grammar(home):
    # Productions
    cfoperator  =   equalsOp ^ notequalsOp
  
    pathElement=    seperator + identifier
    RelSpec    =    OneOrMore(pathElement)
    AbsSpec    =    identifier + RelSpec

    ExprField  =    AbsSpec ^ RelSpec

    ExprText   =    Forward()   
    BoolExpr   =    ExprField + cfoperator + ExprText 
    QueryExpr  =    BoolExpr + queryOp + ExprText + "/" +ExprText

    ExprText   <<  (  ExprField ^ \
    		          QueryExpr ^ \
                      LiteralVal  )

    ## Functions for parsing.
    def doBool(s,loc,toks):
    	modlogger.debug( "getbol\n")
        sense=(toks[1]=="!=")
    	return sense ^ ( str(toks[0]) == toks[2])


    def doQuery(s,loc,toks):
    	modlogger.debug( "doing query\n")
        if toks[0]:
    		return toks[2]
    	else:
    		return toks[4]

    def ExprFieldAction(s,loc,toks):
        #In this case our walk will fail so
        # just return None as an invalid thang.
        if home is None: return None

        #Determine whether abs or rel and
        # find our origin.
        # We use the home  objct - or
        # derefernce the object if it is an absolute reference.
        # - we can't just get the category because there is (currently)
        #   no object which represents those , but we can get an object
        #   and the grammar is specified such that an object must be spcified
        #   not just a category`
        if toks[0] == ":":
            origin  = home
            path    = toks[1:]
        else:
            origin  = home.get_root().get_object(toks[0],toks[2])
            path    = toks[4:]
        
        #Walk along the attributes
        field = origin
        canonpath = origin.get_nodeid()
        for ele in path:
            if ele != ":": #Skip ':' as grammar noise.
                if field is None:
                    raise NullReference(canonpath)
                canonpath ="%s:%s"%(field.get_nodeid(),ele)
                try:
                    field = field[ele]
                except KeyError:
                    raise NoAttribute("%s has no attribute `%s'"%(field.get_nodeid(),ele))

                if hasattr(field,"getSelf"):
                    field = field.getSelf()
        return field
    
    ## Bind functions to parse actions
    ExprField.setParseAction(ExprFieldAction)
    BoolExpr.setParseAction(doBool)
    QueryExpr.setParseAction(doQuery)

    ExprText.enablePackrat()
    ExprText.validate()
    return ExprText + stringEnd
