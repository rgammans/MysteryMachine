#!/usr/bin/python

###Grammar stuff
from pyparsing import  Regex,Optional,ZeroOrMore, QuotedString , Literal, Word, alphas , nums , printables  , CharsNotIn
from functools import partial

import sys


def Grammar(obj):
    home=obj
    #Tokens
    openExpr   =   Literal("${")
    closeExpr  =   Literal("}")
    seperator  =   Literal(":")
    queryOp    =   Literal("?")
    equalsOp   =   Literal("=")
    notequalsOp=   Literal("!=")

    identifier =   Word(alphas + nums)
    objectName =   identifier.copy()
    fieldName  =   identifier.copy()
    ObjectId   =   Word(nums)
    NonExpr    =   CharsNotIn("$")

    ExprLimit  =   Regex("[^ \n\t]*[ \n\t]")
    Value      =   QuotedString('"') 

    # Productions
    cfoperator  =   equalsOp ^ notequalsOp
    ObjectUID   =   Optional(objectName + seperator + ObjectId)

    NamedField  =   ObjectUID + seperator +fieldName
    ExprField   =   ObjectUID ^  \
    		NamedField

    BoolExpr   =    ExprField + cfoperator + Value.copy() 
    QueryExpr  =    BoolExpr + queryOp + Value.copy() + seperator +Value.copy()

    ExprText   =    ExprField ^ \
    		QueryExpr

    Expr       =   openExpr + ExprText + closeExpr
    #Error      =   openExpr + ExprLimit 

    textEle    =   NonExpr  ^ \
                   Expr 
       
    text       =   ZeroOrMore(textEle)


    ## Functions for parsing.

    def getField(s,loc,toks):
    	print "bar(%s)\n" % toks
    	field=toks[2]
    	obj=toks[0]
    	return obj[field]


    def doBool(s,loc,toks):
#    	print "baz\n"
        sense=(toks[1]=="!=")
    	return sense ^ ( str(toks[0]) == toks[2])


    def doQuery(s,loc,toks):
#    	print "foo\n"
        if toks[0]:
    		return toks[2]
    	else:
    		return toks[4]

    def initFromParse(s,loc,toks):
    	print "Creating form :%s (current=%s)\n"%(toks,repr(home))
        isSelf=len(toks)==0
       	if isSelf:         return home 
        elif home is None: return None
        else:              return home.get_root().get_object(toks[0],toks[2])

    #def gotError(s,loc,toks):
    #	sys.stderr.write("BARR")

    ## Bind functions to parse actions
    
    NamedField.setParseAction(getField)

    BoolExpr.setParseAction(doBool)
    QueryExpr.setParseAction(doQuery)
    Expr.setParseAction(lambda s,loc,tok:tok[1])
    #Error.setParseAction(gotError)

    ObjectUID.setParseAction(initFromParse)
    
    return ExprText
