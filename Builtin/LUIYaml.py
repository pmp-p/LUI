"""
this file implements loading a user interface from a yaml file
Author : tosh007  revisited by: PmpP
2016-05-05
"""

import yaml as yamlParser
from copy import *

import panda3d.lui


__all__ = ['LUI',
    'LUIButton', 'LUICheckbox', 'LUIFormattedLabel', 'LUIFrame',
    'LUIInitialState', 'LUIInputField', 'LUIInputHandler', 'LUILabel', 'LUIObject',
    'LUIProgressbar', 'LUIRadiobox', 'LUIRadioboxGroup', 'LUIRegion', 'LUIRoot',
    'LUIScrollableRegion', 'LUISelectbox', 'LUISkin', 'LUISlider', 'LUISprite',
    'LUISpriteButton', 'LUITabbedFrame',
    "LUIHorizontalLayout", "LUIVerticalLayout", "LUICornerLayout", "LUIHorizontalStretchedLayout"
]

LUIBaseLayout = panda3d.lui.LUIBaseLayout


#FIXME:in every case of failure replace by eg a LUILabel with text=errormsg

# LUISprite should have a .get_children() that return an list ( empty for now )

# LUICornerLayout and LUIHorizontalStretchedLayout should live in seperate imports like others layouts

# create a 2D LUIMatrix object that can clone a widget sample in its cells with rules of some parametric(x,y) function



for luie in __all__[1:]:

    LUIElem = None
    try:
        exec("from plugbase.ui.lui.%(w)s import %(w)s as %(w)s;LUIElem = %(w)s" % dict(w=luie) )
    except:
        try:
            exec("from %(w)s import %(w)s as %(w)s;LUIElem = %(w)s" % dict(w=luie) )
        except:
            print("ressource panda3d.lui.%s will not be available" % luie[3:] )

    finally:
        setattr( panda3d.lui , luie[3:] , LUIElem )



class YamlUI:
    def __init__(self,parent=None, name=None, filename=None, yaml=None,**kw):
        self.parent = parent

        #hold hashes of luiobjects constructs
        self.gui = []
        self.msg = {}

        self.kw = kw

        self.name = name or ( filename or (yaml and 'inline') )

        if filename or yaml:
            self.loadGui(filename=filename,yaml=yaml)


    def extract_kw(self, kw, argname, try_ = True, format=None):
        try:
            value = kw[argname]
            del kw[argname]
        except KeyError:
            if not try_:
                raise KeyError(argname + " is required for constructing an ui element")
            value = None
        if (type(value) is str) and format:
            value=value.format(*format)
        return value

    def format_kw(self, kw, format):
        for key in kw.keys():
            if type(kw[key]) is str:
                kw[key]=kw[key].format(*format)


    def get_by_name(self,param,parent=None,lvl=0):
        for child in (parent or self.parent).get_children():
            if child and child.name == param:
                return child
            elif hasattr(child,'get_children'):
                recurse = self.get_by_name( param, parent = child , lvl = lvl+1)
                if recurse :
                    return recurse
        if not lvl:
            err("%s %s : %s not found" ,' ' * lvl, self.parent,param )
        return None

    def event(self,e):
        msg  = self.msg.get( hash(e.get_sender()) , '')
        print("\nYamlUI.event\ndef on_%s_( self, %s ): pass" %( e.get_sender().name, e ) )
        print("\nYamlUI.event\ndef on_%s_%s( self, msg='%s' ): pass" %( e.get_sender().name, e.name,msg ) )
        return msg

    def get_by_hash(self,param,parent=None,lvl=0):
        for child in (parent or self.parent).get_children():
            if child and hash(child) == param:
                return child

            elif hasattr(child,'get_children'):
                recurse = self.get_by_hash( param, parent = child , lvl = lvl+1)
                if recurse :
                    return recurse
#        if not lvl:
#            err("%s %s : %s not found" ,' ' * lvl, self.parent,param )
        return None

    def loadGui(self,filename=None, yaml=None):
        if self.gui:
            self.deleteGui()
        #self.script_module.__dict__.clear()
        #self.script_module.gui=self

        if yaml is not None:
            ui_data=yamlParser.load(yaml)
        elif filename is not None:
            with open(filename,'rb') as stream:
                ui_data=yamlParser.load(stream)
        else:
            ui_data={}


        self.ui_data={}
        code=None
        self.all_binds= []   # {element:{event:func}}
        # first, iterate over the parsed datastructure
        # UI elements will be created immediately

        for pair in ui_data:
            assert len(pair) == 1
            name = pair.keys()[0]
            element_data = pair[name]


            if name=="python":
                code = element_data
                #exec code in self.script_module.__dict__
            else:
                self._loadElement(name, element_data, self.parent)
                self.ui_data[name]=element_data


        # finally, execute the bind statements, as they might use custom code from yaml
        while self.all_binds:
            binds = self.all_binds.pop()
            hofobj = binds.pop('hash')
            nofobj = binds.pop('name')
            if hofobj=='*':
                for luiobj in map( self.get_by_hash, self.gui ):
                    if luiobj.name == nofobj:
                        for event in binds:
                            print("%s.%s event has been set %s" % (luiobj.name, event, binds.get(event) ) )
                            luiobj.bind(event,self.event)
            else:
                luiobj = self.get_by_hash( hofobj )
                for event in binds:
                    self.msg[ hofobj ] = binds.get(event)
                    print("%s.%s event has been set %s" % (luiobj.name, event, binds.get(event) ) )
                    luiobj.bind(event,self.event)




    def instanceElement(self, name, parent, format):    # allows to instance branches
        self._loadElement(name, deepcopy(self.ui_data[name]), parent, format,True)


    def _loadElement(self, name, element_data, parent, formatlist=None, force_load=False):
        if formatlist:
            name=name.format(*formatlist)

        block_load = self.extract_kw(element_data, "block_load")    # only do not automatically load this branch

        if (not block_load) or force_load:
            typeofobj = self.extract_kw(element_data, "type", False)
            if not typeofobj.startswith('LUI'):
                err("this loader is for LUI objects only",typeofobj)
                return

            typedef = getattr( panda3d.lui, typeofobj[3:] )
            binds  = self.extract_kw(element_data, "bind", format=formatlist)
            children  = self.extract_kw(element_data, "children")


            kw = element_data
            if formatlist:
                self.format_kw(kw, formatlist)

            # PROBLEM: LUIHorizontalLayout needs a parent, but shouldn't the parent be specified using parentLayout.add(obj) ????
            parentToLayout = isinstance(parent, LUIBaseLayout)
            layoutChild    = issubclass(typedef, LUIBaseLayout)

            if not parentToLayout:
                kw["parent"] = parent
            else:
                parent_dummy = LUIObject()
                if layoutChild: # LUILayouts need a parent object passed
                    kw.setdefault("parent", parent_dummy )



            # finally construct lui element

            # fixme handle %+%
            if not self.gui:
                for kn in self.kw.keys():
                    override = self.kw[kn]
                    maybe  =  kw.get(kn,0)
                    kw.setdefault( kn , maybe+override )
                kw.update( self.kw )

            obj = typedef(**kw)

            obj.name = name


            self.get_family_members( obj )

            if binds:
                binds['hash'] = hash(obj)
                binds['name'] = name
                self.all_binds.append( binds )


            if parentToLayout:
                if layoutChild:
                    parent.add(parent_dummy)
                else:
                    parent.add(obj)

            if children:
                for pair in children:
                    #print len(pair)
                    assert len(pair)==1

                    name = pair.keys()[0]
                    data=pair.values()[0]
                    self._loadElement(name, data, obj, formatlist)

    def get_family_members(self,obj):
        self.gui.append( hash(obj) )
        if hasattr(obj,'get_children'):
            for child in obj.get_children():
                hc=hash(child)
                if not hc in self.gui:
                    self.gui.append( hc )
                else:
                    print("circular reference on LUI object !",child,child.name)
                self.get_family_members( child )



    def delete_leaves(self,luiobj):
        myid = hash(luiobj)
        if hasattr(luiobj,'get_children'):
            for child in luiobj.get_children():
                if child and hash(child) in self.gui:
                    self.delete_leaves( luiobj )
                else:
                    return False

        if luiobj.has_parent():
            #print('deleted (%s)%s ' % (luiobj.__class__.__name__,luiobj.name) )
            luiobj.unbind_all()
            luiobj.clear_parent()
        return True


    def deleteGui(self):
        if not self.gui:
            return

        print(":lui:yaml: Deleting %s LUIObjects from [%s]" % (len(self.gui),self.name) )
        while self.gui:
            luiobj = self.get_by_hash( self.gui.pop() )
            if luiobj:
                #print("about to delete:",luiobj,luiobj.name)
                if not self.delete_leaves( luiobj ):
                    #print('  deletion aborted')
                    pass

        if self.gui:
            warn('%s still have adopted children',self.gui)
        self.parent = None


    def __del__(self):
        self.deleteGui()






