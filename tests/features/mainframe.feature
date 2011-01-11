Feature: Basic window
  In order to use MysteryMachine
  I need a main frame with some standard menu items

Scenario:Application Startup
    When the application is started
    Then I see a new window


Scenario: There is a file menu 
   Given the application is started
   Then I look at the menubar
   I should find a "File" menu
 
Scenario: there is a help menu 
   Given the application is started
   Then I look at the menubar
   I should find a "Help" menu  

Scenario: There is an about item
    Given the application is started
    Then I look at the menubar
    I should find a "Help" menu  
    When I look at the menu I should find a "About Mystery Machine" entry

Scenario: the about item opens a dialog box
    Given the application is started
    Then I look at the menubar
    I should find a "Help" menu  
    When I look at the menu I should find a "About Mystery Machine" entry
    And click on it
    Then I should see a about dialog box.
    

Scenario: The is an open file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open PackFile" entry

Scenario: the open file shows a file picker
    Given the application is started
    I should find a "File" menu
    When I look at the menu I should find a "Open PackFile" entry
    And click on it
    Then I should get a file select dbox.
    I can see a "Cancel" button
    And click on it
    Then the dialog is closed

Scenario: The is an open file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open From a URI" entry

Scenario: The is an open file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open From a URI" entry
    And click on it
    Then I see a window entitled "Open from a URI"


Scenario: The is an open URI window has sensible controls.
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open From a URI" entry
    And click on it
    Then I see a window entitled "Open from a URI"
    This window has a combobox
    This combo has the following selections options:
        | option  |
        | dict    |
        | hgafile |
    



Scenario: The is an close file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Close" entry


Scenario: The is an revert file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Revert" entry


Scenario: The is an revert file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Commit" entry

Scenario: The is an quit file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Quit" entry

Scenario: The close, save and Revert menu options are grey out 
   Given the application is started
   Then I look at the menubar
   I should find a "File" menu  
   When I look at the menu I should find a "Close" entry
   This entry is greyed-out
   When I look at the menu I should find a "Save" entry
   This entry is greyed-out
   When I look at the menu I should find a "Revert" entry
   This entry is greyed-out
    When I look at the menu I should find a "Commit" entry
   This entry is greyed-out
   
Scenario: Can open two packfiles and Can close the first open on first then the second becomes a blank frame.
    Given the application is started is
    I can Open a Packfile named '../examples/format1.mmpack'
    Then there is a window named "MysteryMachine - A simple example"
    I can Open a Packfile named '../examples/format1.mmpack'
    Then there are "2" windows named "MysteryMachine - A simple example"
    When I close window '1'
    Then window '1' is closed
    When I close window '2'
    Then window '2' becomes blank.
  
Scenario: The close,save and revert menu options are not grey out after a system is loaded 
   Given the application is started
   I can Open a Packfile named '../examples/format1.mmpack'
   Then I look at the menubar
   I should find a "File" menu  
   When I look at the menu I should find a "Save" entry
   This entry is not greyed-out
   When I look at the menu I should find a "Revert" entry
   This entry is not greyed-out
   When I look at the menu I should find a "Commit" entry
   This entry is not greyed-out
   When I look at the menu I should find a "Close" entry
   This entry is not greyed-out

