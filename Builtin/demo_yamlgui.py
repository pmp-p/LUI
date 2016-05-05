"""
This example shows how to load an UI from an .yaml file
the system supports all lui types, keyword args, event binding, and custom python code inside the yaml file.

"""

# Add lui modules to the path. This will not be required when LUI is included
# in panda.
import sys,os,gc


import LUIYaml
import panda3d.core

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
panda3d.core.getModelPath().appendDirectory('./rsr')

#from LUIEverything import *
from panda3d.lui import LUIRegion, LUIInputHandler

from Skins.Default import Skin as LUISkin


base=ShowBase()
base.region = LUIRegion.make("LUI", base.win)
base.handler = LUIInputHandler()
base.mouseWatcher.attach_new_node(base.handler)
base.region.set_input_handler(base.handler)
base.skin = LUISkin()
base.skin.load()




y1 = """
# example yaml file for loading LUI menus
#
#general structure:
#object_name:
#  type: LUIClassName
#  keyword: value   (passed to constructor)
#  bind:
#      event: function


- vertical:
    type: LUIVerticalLayout
    spacing: 30
    children:
        - b_enter:
            type: LUIButton
            template: ButtonGreen
            text: instancing example
            bind:
                click: change_to_example


# custom python module for e.g. event handling
# acces all gui elements as attributes of global variable "gui"
- python: |
    def handle(event):
        print "button2 pressed!"

    def change_to_example(event):
        print "button <enter another menu> pressed!"
        gui.loadGui("menus/structure_test.yaml")

    #print "python inside yaml script executed"
"""


y2 = """
# yamlgui test file
# creates 2 rows of 3 columns each
- vertical1:
    type: LUIVerticalLayout     # type = lui class name
    spacing: 30
    children:
        - main_button:
            type: LUIButton
            text: back to the other menu!
            bind:
                click: toMain


# prefab for instancing
- horizontal{0}:   # referenced name
    type: LUIHorizontalLayout
    spacing: 30
    block_load: True    # do not load until explicitly wanted, by calling loadElement(name, parent, formatlist)
    children:
        - mybutton{0}_1:
            type: LUIButton
            text: line{0} row1
        - mybutton{0}_2:
            type: LUIButton
            text: line{0} row2
        - mybutton{0}_3:
            type: LUIButton
            text: line{0} row3
"""




class Menu1(LUIYaml.YamlUI):

    def event(self,e):
        print("YamlUI.event\ndef on_%s_( self, %s )" %( e.get_sender().name, e ) )
        print("YamlUI.event\ndef on_%s_%s( self )" %( e.get_sender().name, e.name ) )

        self.deleteGui()
        Menu2( parent = base.region.root, name='menu2', yaml = y2 , top=100,left=100 )

class Menu2(LUIYaml.YamlUI):

    def event(self,e):
        print("YamlUI.event\ndef on_%s_( self, %s )" %( e.get_sender().name, e ) )
        print("YamlUI.event\ndef on_%s_%s( self )" %( e.get_sender().name, e.name ) )

        self.deleteGui()
        Menu1( parent = base.region.root, name='menu1', yaml = y1  )

Menu1( parent = base.region.root, name='menu1', yaml = y1  )




# example to remove the interface again
# gui.deleteGui()
base.run()
