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
from MysteryMachine.Exceptions import *

from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMSystem import MMSystem


import tempfile

import wx
import wx.aui
import  wx.lib.scrolledpanel as scrolled

#Change to read this out of the generated file , created from mercurial data.
DEVELOPERS = [ "Roger Gammans" ]
COPYRIGHT = "(C) Roger Gammans"
LICENSE =   """
Copyright (C) 2008-2010 Roger Gammans <roger@gammascience.co.uk>.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

You can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation; either version
2 of the License, or (at your option) any later version.
"""

NAME   =    "MysteryMachine"
VERSION   = "0.14"
WEBSITE   = "http://trac.backslashat.org/mysterymachine"

ID_NEW=wx.ID_NEW
ID_OPENPKFILE=wx.ID_OPEN
ID_CLOSE=wx.ID_CLOSE
ID_REVERT=wx.ID_REVERT
ID_QUIT=wx.ID_EXIT
ID_ABOUT=wx.ID_ABOUT
ID_ABOUTWX=107
ID_OPENURI=108
ID_COMMIT=109
ID_SAVE=wx.ID_SAVE
ID_SAVEAS=wx.ID_SAVEAS

ID_VIEW_BASE=1000
#

ID_URI_DIR_BROWSE=200

def _noop(uri):
    return None

class OpenUriDialog(wx.Dialog):
    def __init__(self,parent,id, title = "Open from a URI", caption =u"Chose URI to open", action = _noop ):
        super(OpenUriDialog,self).__init__(parent,id,title)
        self.action = action
        outersizer=wx.StaticBoxSizer(wx.StaticBox(self,1,caption),  wx.VERTICAL)
        sizer=wx.BoxSizer(  wx.HORIZONTAL)
        self.SetSizer(outersizer)
        outersizer.Add(sizer ,1 , wx.EXPAND, 20)
        schemes = MysteryMachine.store.GetStoreNames()
        self.combobox = wx.ComboBox(self,-1,choices = list(schemes) )
        self.textctrl = wx.TextCtrl(self,-1)
        self.button   = wx.Button(self,ID_URI_DIR_BROWSE,label="Browse")
        wx.EVT_BUTTON(self,ID_URI_DIR_BROWSE,self.onDirBrowse)
        sizer.Add(self.combobox,1)
        sizer.Add(wx.StaticText(self,-1,label = ":" ) ,0)
        sizer.Add(self.textctrl,2)
        sizer.Add(self.button,1)

        sizer2=wx.StdDialogButtonSizer()
        sizer2.Add(wx.Button(self,wx.ID_OK,"OK"))
        sizer2.Add(wx.Button(self,wx.ID_CANCEL,"Cancel"))
        outersizer.Add(sizer2)
        outersizer.Fit(self) 

        wx.EVT_BUTTON(self,wx.ID_OK,self.onDoLoad)
        wx.EVT_BUTTON(self,wx.ID_CANCEL,self.onCancel)
        self.Show()

    def onDoLoad(self,evt):
        print "inDoload"
        uri = self.combobox.GetValue() + ":" + self.textctrl.GetValue()
        sys = self.action(uri)
        wx.GetApp().OpenFrame(sys)
        self.Close()
        self.Destroy()


    def onCancel(self,evt):
        print "o-uri cancelled"
        self.Close()
        self.Destroy()

    def GetUri(self):
        return self.combobox.GetValue() + ":" + self.textctrl.GetValue()

    def onDirBrowse(self,event):
        chosendir = wx.DirSelector("Select system directory")
        self.textctrl.SetValue(chosendir)


class ScrolledTab(scrolled.ScrolledPanel):
    pass
    def __init__(self,parent,*args,**kwargs):
        
        super(scrolled.ScrolledPanel,self).__init__(parent,*args,**kwargs)
        self.sizer = wx.GridSizer()
        self.SetSizer(self.sizer)
        self.innerpanel = None

    def Add(self,panel):
        self.innerpanel =panel
        self.GetSizer().Add(panel,1,wx.EXPAND)
        self.innerpanel.FitInside()
        self.innerpanel.Show(True)
        self.Layout()
        self.SetAutoLayout(True)
        self.SetupScrolling()

    def getPanelName(self):    
        return self.innerpanel.getPanelName()



def _create_new(uri):
    return wx.GetApp().ctx.CreateNew(uri = uri)

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
        self.fileMenu.Append( ID_NEW , "&New","Create a new freeform")
        wx.EVT_MENU(self, ID_NEW, self.OnNew)        
    
        self.fileMenu.Append(ID_OPENPKFILE,"&Open PackFile")
        wx.EVT_MENU(self, ID_OPENPKFILE , self.OnOpenFile)        
        
        self.fileMenu.Append(ID_OPENURI ,"Open From a &URI")
        wx.EVT_MENU(self, ID_OPENURI , self.OnOpenUri)        
 
        self.revertMenuItem = self.fileMenu.Append(ID_REVERT,"&Revert")
        self.revertMenuItem.Enable(False)
        wx.EVT_MENU(self, ID_REVERT, self.OnRevert)        
  
        self.commitMenuItem = self.fileMenu.Append(ID_COMMIT,"&Commit")
        self.commitMenuItem.Enable(False)
        wx.EVT_MENU(self, ID_COMMIT, self.OnCommit)
 
        self.saveMenuItem = self.fileMenu.Append(ID_SAVE,"&Save")
        self.saveMenuItem.Enable(False) 
        wx.EVT_MENU(self, ID_SAVE, self.OnSave)
  
        self.saveasMenuItem = self.fileMenu.Append(ID_SAVEAS,"Save As..")
        self.saveasMenuItem.Enable(False) 
        wx.EVT_MENU(self, ID_SAVEAS, self.OnSaveAs)
        
        self.closeMenuItem = self.fileMenu.Append(ID_CLOSE,"&Close")
        self.closeMenuItem.Enable(False) 
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
        self.SetStatusBar(self.status)       
 
        #Variable to store references to view objects
        self.nextViewId=ID_VIEW_BASE

        self.panel = None
        self.Layout()



    def OnNew(self,event):
        print "onnew"
        dialog = OpenUriDialog(None , -1 , title = "Chose Uri to store new sytem" , caption = "Enter scheme and Uri" , action = _create_new)
        #Set some default values here so users don't need to worry.
        dialog.combobox.SetValue("hgafile")
        workdir = tempfile.mkdtemp("mm-newsystem")
        dialog.textctrl.SetValue(workdir)
        pass

    def OnAboutMM(self,event):
        print self.__class__.AboutInfo
        wx.AboutBox(self.__class__.AboutInfo)

    def OnOpenFile(self,event):
        packfile = wx.FileSelector("Open a MysteryMachine Packfile",wildcard="*.mmpack")
        print packfile
        sys = self.app.ctx.OpenPackFile(packfile)
        self.app.OpenFrame(sys)

    def OnSave(self,event):
        try:
            self.sys.SaveAsPackFile()
        except NoPackFileName , e:
            self.OnSaveAs(event)

    def OnSaveAs(self,event):
        name = str(self.sys) + ".mmpack"
        packfile = wx.FileSelector("Save a MysteryMachine Packfile",wildcard="*.mmpack",
                                   default_filename = name,
                                   default_extension = ".mmpack",flags = wx.FD_SAVE + wx.FD_OVERWRITE_PROMPT)
        self.sys.SaveAsPackFile(packfile)

    def AssignSystem(self,sys):
        import systree
        if sys:
            self.nb = wx.aui.AuiNotebook(self)
            panel = systree.TreePanel(self,sys) 
            self.SetTitle("MysteryMachine - %s" % (sys  or ""))
        
            self.AddPanel(panel)

            self.sizer =  wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.nb,1,wx.EXPAND)    
            self.SetSizer(self.sizer)
            self.Layout()
        else:
            self.sizer.Remove(self.nb)
            for page_nr in range(self.nb.GetPageCount()):
                self.nb.DeletePage(page_nr)
            self.nb.Close()
            self.nb = None
            self.SetTitle("MysteryMachine")
            self.SetSizer(None)
            self.sizer = None
         
        self.sys = sys    
        self.app.frames[sys] = self
        self.app.systems[self] = sys
        self.closeMenuItem.Enable(sys is not None)
        self.saveMenuItem.Enable(sys is not None)
        self.saveasMenuItem.Enable(sys is not None)
        self.revertMenuItem.Enable(sys is not None)
        self.commitMenuItem.Enable(sys is not None)

    def AddPanel(self,panel):
        self.nb.AddPage(panel,panel.getPanelName())


    def GetNewNodePanel(self,parent,schema_node):
        """Returns a panel for the passed in schema node

        schema_node must be a node in a MysteryMachine.schema.
        """
        ##FIXME: consult userprefs to find what panel to open
        #        for each object type.
        panel = None
 
        if isinstance(schema_node,MMAttribute):
            import attributepanel
            panel = attributepanel.AttributePanel(parent, schema_node )
        
        if isinstance(schema_node,MMObject):
            import objectpanel
            panel = objectpanel.ObjectPanel(parent, schema_node )

        if isinstance(schema_node,MMSystem):
            import systree
            panel = systree.TreePanel(parent,schema_node)
        return panel
 
    def NewSchemaView(self,schema_node):
        """Creates a new tab showing schema_node.

        schema_node must be a node in a MysteryMachine.schema.
        """
        
        panel = ScrolledTab(self,-1)
        innerpanel = self.GetNewNodePanel(panel,schema_node)
        if innerpanel is None:
             panel.Destroy()
             return
        panel.Add(innerpanel)
        
        if panel: self.AddPanel(panel)
 

    def OnOpenUri(self,event):
        dialog = OpenUriDialog(None , -1  , action = self.app.ctx.OpenUri)
    
    def OnRevert(self,event):
        print "onrevertr"
        pass
    
    def OnCommit(self,event):
        caption = "Enter log message for this changeset"
        title   = ""
        newstr = wx.GetTextFromUser(title,caption = caption)
        self.sys.Commit(newstr)
 

    def OnClose(self,event):
        print "onclose"
        #TODO: Check if system is saved.
        self.app.CloseFrame(self)

    def OnExit(self,event):
        wx.GetApp().ExitMainLoop()

    def AddView(self,viewname,desc,evtHndlr):
        id=++self.nextViewId
        self.ViewMenu.Append(id,viewname,desc);
        wx.EVT_MENU(self,id,evtHndlr)
        return id

    def SetApp(self,app):
        self.app = app


class MMWxApp(wx.PySimpleApp):
    def __init__(self,options  = []):
        wx.PySimpleApp.__init__(self)

        self.args = options
        self.ctx  = None

        self.SetVendorName("Roger Gammans")
        self.SetAppName("MysteryMachine")

        win=MainWindow(None  ,-1,"MysteryMachine", size=(400,200))
        self.SetTopWindow(win)
        win.SetApp(self)
        win.Show()

        self.frames  =  { None: win }
        self.systems =  { win: None }
    
    def OpenFrame(self,system):
        """Assigns a system to a Frame.

        Opens a new top level frame for a system, or assigns
        to an existing unassigned frame if any.
        """
        if system in self.frames:
            #System already open so raise it's window to the top.
            self.frames[system].Raise()
            return

        if None in self.frames:
            win = self.frames[None]
            del self.frames[None]
            win.AssignSystem(system)
        else:
            newwin = MainWindow(None  ,-1, "", size=(400,400))
            newwin.SetApp(self)
            newwin.AssignSystem(system)
            newwin.Show()
 
    def CloseFrame(self,frame):
        """Close an existing frame and system
        """
       
        system = self.systems[frame]
        if len(self.frames) == 1:
            frame.AssignSystem(None)
        else:
            frame.Close()
            del self.frames[system]
            del self.systems[frame]

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
