# -*- coding: utf-8 -*-
from lettuce import step
from lettuce.terrain import after , before
from dogtail.utils import run
from dogtail import tree
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
    if group1 == u'File': 
        world.filemenu= world.focus_obj
    assert world.focus_obj, '%s menu entry not found' % group1


@step(u'When I look at the menu I should find a "(.*)" entry')
def when_i_look_at_the_menu_i_show_find_a_group1_entry(step, group1):
    world.focus_obj = world.focus_obj.menuItem(group1) 
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
    opendialog.button("Cancel").click()



@step(u'Then I see a window entitled "(.*)"')
def then_i_see_a_dialog_box_entitled_group1(step, group1):
    opendialog = world.app.window(u"Open from a URI")
    assert opendialog ,"No dialog found"


@before.all
def setup_world():
    world.filemenu = None
    world.app = None
 
@after.all
def close_app(step):
    if world.filemenu is not None:
        world.filemenu.menuItem("Quit").click()
     #world.app.close()
