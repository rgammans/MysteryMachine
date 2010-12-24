#!/usr/bin/env python
#               Ui/wx/__init__.py - Copyright R G Gammans 
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

from __future__ import with_statement

import MysteryMachine
import mercurial.ui as hgui

import wx

#Change to read this out of the generated file , created from mercurial data.
DEVELOPERS = [ "Roger Gammans" ]
COPYRIGHT = "(C) Roger Gammans"
LICENSE =   """
Copyright (C) 2008-2010 Roger Gammans <roger@gammascience.co.uk>.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""

NAME   =    "MysteryMachine"
VERSION   = "0.14pre"
WEBSITE   = "http://trac.backslashat.org/mysterymachine"

ID_NEW=101
ID_OPENPKFILE=102
ID_CLOSE=103
ID_REVERT=104
ID_QUIT=105
ID_ABOUT=106
ID_ABOUTWX=107
ID_OPENURI=108

ID_VIEW_BASE=1000
#
class MainWindow(wx.Frame):


    AboutInfo = wx.AboutDialogInfo()
    for dev in DEVELOPERS:
        AboutInfo.AddDeveloper(dev)
    AboutInfo.SetCopyright(COPYRIGHT)
    AboutInfo.SetLicense(LICENSE)
    AboutInfo.SetVersion(VERSION)
    AboutInfo.SetWebSite(WEBSITE)

    def __init__(self,parent,id,title,size):
        wx.Frame.__init__(self,parent,id,title)
        self.app = None
        #Create menu.
        self.menu=wx.MenuBar()
        self.fileMenu=wx.Menu()
        self.fileMenu.Append( -1 , "&New","Create a new freeform")
        wx.EVT_MENU(self, ID_NEW, self.OnNew)        
    
        self.fileMenu.Append(ID_OPENPKFILE,"&Open PackFile")
        wx.EVT_MENU(self, ID_OPENPKFILE , self.OnOpenFile)        
        
        self.fileMenu.Append(ID_OPENURI ,"&Open PackUri")
        wx.EVT_MENU(self, ID_OPENURI , self.OnOpenUri)        
 
        self.fileMenu.Append(ID_REVERT,"&Revert")
        wx.EVT_MENU(self, ID_REVERT, self.OnRevert)        
    
        self.fileMenu.Append(ID_CLOSE,"&Close")
        wx.EVT_MENU(self, ID_CLOSE, self.OnClose)        
        
        self.fileMenu.AppendSeparator()
        
        self.fileMenu.Append(ID_QUIT,"&Quit")
        wx.EVT_MENU(self, ID_QUIT, self.OnExit)        
        
        self.ViewMenu=wx.Menu()
        self.helpMenu=wx.Menu()

        self.menu.Append(self.fileMenu,"&File")
        self.menu.Append(self.ViewMenu,"&View")
        self.menu.Append(self.helpMenu,"&Help")
   
        self.helpMenu.Append(ID_ABOUT,"&About Mystery Machine")
        wx.EVT_MENU(self, ID_ABOUT, self.OnAboutMM)        
  
        self.SetMenuBar(self.menu)
        self.status=wx.StatusBar(self)
        self.status.Enable()
        self.status.Show()
        
        #Variable to store references to view objects
        self.nextViewId=ID_VIEW_BASE
        

    def OnNew(self,event):
        print "onnew"
        pass

    def OnAboutMM(self,event):
        print self.__class__.AboutInfo
        wx.AboutBox(self.__class__.AboutInfo)

    def OnOpenFile(self,event):
        packfile = wx.FileSelector("Open a MysteryMachine Packfile",wildcard="*.mmpack")
        print packfile
        sys = self.app.ctx.OpenPackFile(packfile)
        self.app.systems.append(sys)

    def OnOpenUri(self,event):
        dialog = wx.Dialog(None,-1,"Open from a URI")
        outersizer=wx.BoxSizer(  wx.VERTICAL)
        sizer=wx.BoxSizer(  wx.HORIZONTAL)
        dialog.SetSizer(outersizer)
        outersizer.Add(wx.StaticText(dialog,-1,label="Chose URI to open"))
        outersizer.Add(sizer)
        schemes = MysteryMachine.store.GetStoreNames()
        combobox = wx.ComboBox(dialog,-1,choices = list(schemes) )
        textctrl = wx.TextCtrl(dialog,-1)
        button   = wx.Button(dialog,-1,label="Browse")
        sizer.Add(combobox)
        sizer.Add(textctrl)
        sizer.Add(button)
        
        dialog.Show()

    def OnRevert(self,event):
        print "onrevertr"
        pass
    
    def OnClose(self,event):
        print "onclose"
        pass

    def OnExit(self,event):
        wx.GetApp().ExitMainLoop()

    def AddView(self,viewname,desc,evtHndlr):
        id=++self.nextViewId
        self.ViewMenu.Append(id,viewname,desc);
        wx.EVT_MENU(self,id,evtHndlr)
        return id

    def SetApp(self,app):
        self.app = app



class WxMercurialUi(hgui.ui):
    def plain(self):
        """Activates plain mode  so parsing of repsonses is easier"""
        return True

class MMWxApp(wx.PySimpleApp):
    def __init__(self,options  = []):
        wx.PySimpleApp.__init__(self)

        self.args = options
        self.ctx  = None

        self.SetVendorName("Roger Gammans")
        self.SetAppName("MysteryMachine")

        self.win=MainWindow(None  ,-1,"MysteryMachine", size=(400,400))
        self.SetTopWindow(self.win)
        self.win.SetApp(self)
        self.win.Show()

        self.ui = WxMercurialUi()
        self.systems = []
    

    def mercurial_ui(self):
        return self.ui 

    def Run(self):
       with MysteryMachine.StartApp(self.args) as ctx:
            self.ctx = ctx
            self.MainLoop()
       self.ctx = None

def main():
    from MysteryMachine.Main import process_args 

    options = process_args()
    ui = MMWxApp(options)

    ui.Run()


if __name__ == "__main__":
    main()