Feature:  There should be a tree control view of the system available 


Scenario: The root node name should be named after the system
    Given the application is started
    I can Open a Packfile named '../examples/format1.mmpack'
    then the root node is named ""


Scenario: Under the root node should exapnd to show the categories

Scenario: The root should node should have a menu.
    Given the application is started
    I can Open a Packfile named '../examples/format1.mmpack'
    when i right-click on the root node
    I should see the follow menu entries:-
        | entry        |
        | Rename       |
        | New Category |


Scenario: Each category should node should have a menu.
    Given the application is started
    I can Open a Packfile named '../examples/format1.mmpack'
    when i exapnd the root-node
    and click on category nodel
    I should see the follow menu entries:-
        | entry        |
        | Rename       |
        | change default inheiratnance parent | 
        | New Category |

Scenario: Each object node should have a menu

Scenario: The category menu rename menu should change the name of the root node
Scenario: The root menu new category option should create a new category

Scenario: The category rename menu option should add a friendly name to the category
Scenario: The category add object  option should add an object to the category



Scenario: The object rename menu option should change the objects ".defname" attirbute


