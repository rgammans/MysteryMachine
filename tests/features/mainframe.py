# -*- coding: utf-8 -*-
from lettuce import step
from lettuce.terrain import after , before
from dogtail.utils import run
from dogtail import tree
from dogtail import predicate
from time import sleep
import sys

from lettuce import world
@step(u'When the application is started')
def when_the_application_is_started(step):
    run('../scripts/mysterymachine_wx')

@step(u'Then I see a new window')
def then_i_see_a_new_window(step):
     world.focus_obj = tree.root.application( "python")
     world.app  = world.focus_obj
     assert world.focus_obj , "No window opened"

@step(u'Given the application is started')
def given_the_application_is_started(step):
    if world.app is None:
        step.given(u'When the application is started')
        step.given(u'Then I see a new window')
    world.focus_obj = world.app


@step(u'Then I look at the menubar')
def when_i_examine_the_menus(step):
     x = world.focus_obj
     world.focus_obj = x.child(roleName = "menu bar")
     assert world.focus_obj , "No menu bar"


@step(u'I should find a "(.*)" menu')
def i_should_find_a_group1_menu(step, group1):
    world.focus_obj = world.focus_obj.menu(group1) 
    world.menu = world.focus_obj
    if group1 == u'File': 
        world.filemenu= world.focus_obj
    assert world.focus_obj, '%s menu entry not found' % group1


@step(u'When I look at the menu I should find a "(.*)" entry')
def when_i_look_at_the_menu_i_show_find_a_group1_entry(step, group1):
    world.focus_obj = world.menu.menuItem(group1) 
    assert world.focus_obj, '%s menu entry not found' % group1

@step(u'Then I should see a about dialog box.')
def then_i_should_see_a_about_dialog_box(step):
   win = world.app.child("About MysteryMachine")
   button = win.child("Close")
   button.click()


@step(u'And click on it')
def and_click_on_it(step):
    world.focus_obj.click()


@step(u'Then I should get a file select dbox.')
def then_i_should_get_a_file_select_dbox(step):
    opendialog = world.app.dialog("Open a MysteryMachine Packfile")
    #TODO Verify it is a file picker
    assert opendialog ,"No File picker dialog found"
    world.dialog = opendialog
    world.focus_obj = opendialog


@step(u'I can see a "(.*)" button')
def i_can_see_a_group1_button(step, group1):
    button =  world.focus_obj.button(group1)
    assert button , "Button %s not found" % group1
    world.focus_obj = button

@step(u'Then the dialog is closed')
def then_the_dialog_is_closed(step):
    pass

@step(u'Then I see a window entitled "(.*)"')
def then_i_see_a_dialog_box_entitled_group1(step, group1):
    opendialog = world.app.window(u"Open from a URI")
    world.window = opendialog
    world.focus_obj = opendialog
    assert opendialog ,"No dialog found"


@step(u'This window has a combobox')
def this_window_has_a_combobox(step):
    combobox = world.window.child(roleName="combo box")
    world.combobox = combobox
    assert combobox, "combobox note found"


@step(u'This combo has the following selections options')
def this_combo_has_the_following_selections_options(step):
    menu = world.combobox.child(roleName="menu")
    for options in step.hashes:
        option = options["option"]
        assert menu.menuItem(option) , "%s selection not found " % option


@step(u'I can Open a Packfile named \'(.*)\'')
def i_can_open_a_packfile_named_group1(step, group1):
    store = world.focus_obj
    step.given("Then I look at the menubar")
    step.given("I should find a \"File\" menu")
    step.given("When I look at the menu I should find a \"Open PackFile\" entry")
    step.given("And click on it")
    step.given("Then I should get a file select dbox.")
    world.dialog.child(roleName='text').text = group1
    world.dialog.button('Open').click()
    world.focus_obj = store

@step(u'This entry is greyed-out')
def this_entry_is_greyed_out(step):
    assert world.focus_obj.click() == 0L , '%s seems to be clickable' % world.focus_obj

@step(u'This entry is not greyed-out')
def this_entry_is_not_greyed_out(step):
    a = world.focus_obj.click()
    print "\n%i\n"%a
    assert a , '%s seems to not be clickable' % world.focus_obj

@step(u'Then there is a window named "(.*)"')
def then_there_is_a_window_named_group1(step, group1):
    find_n_windows_named(step,"1",group1)
    #step.given('Then there are "1" windows named "%s"'%group1)
    world.focus_obj = world.windows[0]
    world.windows   = world.windows[0]

@step(u'Then there are "(.*)" windows named "(.*)"')
def then_there_are_group1_windows_named_group2(step, group1, group2):
    find_n_windows_named(step,group1,group2)

def find_n_windows_named(step,group1,group2):
    pred = predicate.GenericPredicate( name=group2)
    nr = int(group1)
    #I'd rather not use a constant delay here but I'm not sure what alternative
    #I have I need to ensure the window is complete constructed..
    sleep(4)
    world.app.child(group2)
    world.windows = world.app.findChildren(pred)
    if world.windows is None: world.windows =[]
    assert len(world.windows)  >= nr , 'Can\'t find enough (%i<%i) windows named \'%s\'' % (len(world.windows),nr,group2)
    
@step(u'When I close window \'(.*)\'')
def when_i_close_window_group1(step, group1):
    nr = int(group1)
    world.window  =world.windows[nr-1]
    world.focus_obj = world.window
    step.given("Then I look at the menubar")
    step.given("I should find a \"File\" menu")
    step.given("When I look at the menu I should find a \"Close\" entry")
    step.given("And click on it")


@step(u'Then window \'(.*)\' is closed')
def then_window_n_is_closed(step,group1):
    nr = int(group1)
    world.window  =world.windows[nr-1]
    assert world.window.getUserVisibleStrings() == [] ,"Window doesn't seem to be closed"

@step(u'Then window \'(.*)\' becomes blank.')
def then_the_window_n_becomes_blank(step,group1):
    nr = int(group1)
    world.window  =world.windows[nr-1]
    assert "MysteryMachine" in world.window.getUserVisibleStrings() ,"Window doesn't seem to be closed"


@before.all
def setup_world():
    world.filemenu = None
    world.app = None
 
@after.all
def close_app(step):
    if world.filemenu is not None:
        world.filemenu.menuItem("Quit").click()
     #world.app.close() b
