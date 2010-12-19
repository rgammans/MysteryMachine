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

Scenario: The is an open file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open PackUri" entry

Scenario: The is an open file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Open PackUri" entry
    And click on it
    Then I see a window entitled "Open from a URI"

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

Scenario: The is an quit file menu item
    Given the application is started
    Then I look at the menubar
    I should find a "File" menu
    When I look at the menu I should find a "Quit" entry

