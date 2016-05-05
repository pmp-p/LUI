# Author: PmpP
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import

dependencies = ['core','panda3d.core','panda3d.lui']

implements = "ui"

flags= '+persist +mem +time +events'


def init(*self):
    print("<%s>" % __all__[0] )
    LUIBase.build()


def destroy(*self):
    print("</%s>" % __all__[0] )


"""
TODO:

 - name button-%i events in mousedown
 - cleanup 'Elements' : is dead code
 - tile placement , cascade replace , auto arrange

"""

__all__ = ['LUI',
    'LUIButton', 'LUICheckbox', 'LUIFormattedLabel', 'LUIFrame',
    'LUIInitialState', 'LUIInputField', 'LUIInputHandler', 'LUILabel', 'LUIObject',
    'LUIProgressbar', 'LUIRadiobox', 'LUIRadioboxGroup', 'LUIRegion', 'LUIRoot',
    'LUIScrollableRegion', 'LUISelectbox', 'LUISkin', 'LUISlider', 'LUISprite',
    'LUISpriteButton', 'LUITabbedFrame',
    "LUIHorizontalLayout", "LUIVerticalLayout", "LUICornerLayout", "LUIHorizontalStretchedLayout"
]



import sys
import os

import panda3d.core
import panda3d.lui

for luie in __all__[1:]:
    #FIXME in case of failure replace by eg a LUIErrorLabel
    LUIElem = None
    try:
        exec("from plugbase.ui.lui.%(w)s import %(w)s as %(w)s;LUIElem = %(w)s" % dict(w=luie) )
    except:
        try:
            exec("from %(w)s import %(w)s as %(w)s;LUIElem = %(w)s" % dict(w=luie) )
        except:
            print("ressource panda3d.lui.%s will not be available" % luie[3:] )

    finally:
        setattr( __import__(__name__) , luie , LUIElem )
        setattr( panda3d.lui , luie[3:] , LUIElem )

LUIBaseLayout = panda3d.lui.LUIBaseLayout

try:
    pluginGlobalManager.initPlugin( sys.modules[__name__] , '%s.%s' % ( implements,__all__[0]) )
except:
    print("running out-of-the-box")

    def log(s,*args):
        print( s % args)

    class RunTime:
        native = True
        em = False
        OOTB = True

    try:
        import __builtin__
        PY2=True
        PY3=False
        RunTime.builtins = __builtin__
    except:
        PY3=True
        PY2=False
        import builtins
        RunTime.__builtin__ = builtins

    on_prefix = 'on_'

    RunTime.PY2 = PY2
    RunTime.PY3 = PY3
    RunTime.builtins.RunTime = RunTime
    RunTime.builtins.fix = log
    RunTime.builtins.warn = log
    RunTime.builtins.dev = log
    RunTime.builtins.err = log
    RunTime.builtins._info = __builtin__.info = log

panda3d.lui.__all__ = []

class LUIBase:

    _region = []
    current = 0

    @classmethod
    def region(cls):
        return cls._region[cls.current]

    @classmethod
    def root(cls):
        return cls.region().root

    @classmethod
    def build(cls):
        if LUIBase._region:
            cls.current = 0
            return LUIBase._region[0]

        try:
            base
        except:
            from direct.showbase.ShowBase import ShowBase
            panda3d.core.getModelPath().appendDirectory('./rsr')
            ShowBase()


        if RunTime.OOTB:
            from Skins.Default import Skin as LUISkin
        else:
            from plugbase.ui.lui.Skins.Default import Skin as LUISkin
        skin = LUISkin()
        cls.__handler = LUIInputHandler()
        base.mouseWatcher.attach_new_node(cls.__handler)


        return cls.new(0)


    @classmethod
    def new(cls,idx):

        if idx< len(LUIBase._region):
            cls.current = idx
            return False

        if idx> len(LUIBase._region):
            err("index yet not reached")
            idx=len(LUIBase._region)

        # Initialize LUI
        rname= "LUI-%s"%idx
        region =  LUIRegion.make(rname, base.win)
        region.root.name = rname
        cls._region.append( region )
        cls.current = idx


        cls._region[idx].set_input_handler(cls.__handler)
        return True

    @classmethod
    def wipe(cls):
        for region in cls._region:
            region.root.remove_all_children()




class Layouter:

    # absolute layout cannot work on width/height defaults because LUI can't know them till a rendering cycle

    def pad(self,wdg=None,w=0,h=0):
        if wdg:
            if wdg.width:
                w = wdg.width
            else:
                err("can't place widget [%s] who has no width !",wdg.name or wdg )

            if wdg.height:
                h = wdg.height
            else:
                err("can't place widget [%s] who has no height !",wdg.name or wdg )

        elif (w+h)==0:
            return (self.px,self.py,)

        self.px += self.padx + w
        self.py += self.pady + h

    def place( self, wname, klass, *argv, **kw):
        set=kw.setdefault
        set('parent',self.anchor or self)
        kw['name']=wname
        set( 'left', self.px )
        set( 'top', self.py )
        wdg=self.new(klass, *argv, **kw)
        self.pad(wdg)
        return wdg


    # H/V layouts

    def begin( self, wname, klass, *argv, **kw):
        if self.anchor:
            layout = self.__getCurrentLayout()
            if layout:
                warn('begin with no reset adding to current layout')
                self.anchor = self._ladd(self.__layoutCtx, wname, klass, *argv, **kw)

            else:
                err('reset and no previous layout please use .add/.hadd/.vadd(%s ,%s )!',wname, klass)
                return None
            return self.anchor

        for layctx in ['LUIHorizontalLayout','LUIVerticalLayout']:
            setattr(self, layctx , None )

        kw.setdefault('parent',self.anchor or self)
        kw.setdefault('name',wname)
        self.anchor = self.new(klass, *argv, **kw)
        return self.anchor


    def setCurrentLayout(self,layctx,layout):
        if not layctx in ['LUIHorizontalLayout','LUIVerticalLayout']:
            layctx = 'LUIVerticalLayout'
        setattr(self,layctx,layout)


    def __getCurrentLayout(self,layctx=None):
        auto = layctx is not None

        if not auto:
            layctx = self.__layoutCtx

        stackparent = self.anchor or self

        layout = None

        if layctx in ['LUIHorizontalLayout','LUIVerticalLayout']:
            if hasattr(self,layctx):
                layout = getattr(self, layctx )
        else:
            err('unsupported layout %s defaulting to vertical',layctx )
            layctx = 'LUIVerticalLayout'

        if auto and layout is None:
            warn('no default "%s" defined adding one to %s !',layctx, stackparent.name )
            layout = getattr( panda3d.lui , layctx )( parent= stackparent )

            if layctx=='LUIVerticalLayout':
                layout.width = '100%'
            elif layctx=='LUIHorizontalLayout':
                layout.height = '100%'
            #BUG!
#            if layctx=='LUIVerticalLayout':
#                layout.height = '100%'
#            else:
#                layout.width = '100%'
#

            setattr( self , layctx , layout )
            self.__layoutCtx = layctx

        return layout

    def layout(self):
        return self.__getCurrentLayout('LUIVerticalLayout')


    def _ladd(self,layctx, wname, klass, *argv, **kw):
        kw['parent']='layout'
        kw['name'] = wname

        # hlayout vlayout
        layout= self.__getCurrentLayout(layctx)

        kw['layer'] = layout
        child =  self.new(klass,*argv,**kw)
        layout.add(child)
        return child


    def hadd(self, wname, klass, *argv, **kw):
        return self._ladd( 'LUIHorizontalLayout', wname , klass , *argv, **kw )

    def vadd(self, wname, klass, *argv, **kw):
        return self._ladd( 'LUIVerticalLayout', wname , klass , *argv, **kw )


    def reset(self):
        for layctx in ['LUIHorizontalLayout','LUIVerticalLayout']:
            setattr(self, layctx , None )


class pdict(dict):

    def __init__(self,*argv,**kw):
        dict.__init__(self,kw)
        if argv:
            self['argv']=argv

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self,attr):
        return dict.get(self,attr,'')

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self,key)
        except:
            return ''

    def __getattr__(self,attr):
        if attr=='argv':
            return dict.get(self,'argv',())
        return dict.get(self,attr,None)

    def mpop(self,*keys):
        for k in keys:
            yield self.pop(k,'')

class Factory(Layouter):



    def __init__(self,*argv,**kw):

        #implicit name and .begin() on self
        self.set_name( self.__class__.__name__ )
        self.anchor = self

        self.__handler = None


        # for absolute layout
        self.padx = kw.get('padding-left',2)
        self.pady = kw.get('padding-top',2)

        self.px = 0
        self.py = 0

        self.anchor = self
        self.built = False
        self.__builder()

        #remove all refs ?
        self.anchor = None

    def __builder(self):
        if self.built:
            exc("ALREADY BUILT")
            return
        self.build()
        self.built =True


    def set_handler(self,h):
        self.__handler = h

    def __ihandler(self,e):
        if self.__handler:
            nevt= e.sender.name
            params = pdict(e,**{'name' :nevt} )
            fqnevt = '%s%s_' % ( self.__handler.on_prefix , nevt )
            if hasattr( self.__handler , self.__handler.on_prefix ):
                if type(self.__handler) is object:
                    getattr(self.__handler , self.__handler.on_prefix )( params)
                else:
                    getattr(self.__handler , self.__handler.on_prefix )(self.__handler , params)
            else:
                fix("no %s.%s(e) handler for %s", self.__handler.__name__,self.__handler.on_prefix , fqnevt )

            if hasattr( self.__handler , fqnevt ):
                print( type(self.__handler))
                if repr(self.__handler.__class__)=="<type 'module'>":
                    getattr(self.__handler , fqnevt )(self.__handler, params )
                else:
                    getattr(self.__handler , fqnevt )( params )

            return

        dev('no handler defined for %s',e.sender.name)


    def getDefault(self,kw):
        set=kw.setdefault

        if kw.get('parent',None) is None:
            set('parent',LUI.root())
            set('width','100%')
            set('height','100%')
        else:
            set('width','95%')
            set('height','95%')

        set('style',LUIFrame.FS_raised)
        set('margin',2)
        set('top',1)
        return kw

    def set_named_widget(self,wname,wdg):
        fix("assign auto numbered names on defaults")
        if hasattr(self, wname ):
            warn("widget with same name '%s' found in '%s' converting to named list",wname,self.name or self)
            nl = []
            nl.append( getattr( self, wname ) )
            nl.append(wdg)
            setattr( self, wname , nl )
            return wdg
        wdg.name = wname
        setattr( self, wname , wdg )
        return wdg


    def new(self,klass,*argv,**kw):
        set=kw.setdefault

        p = kw.setdefault('parent',self)

        if p=='layout':
            kw.pop('parent')
        elif p is None:
            warn('creating an instance of class LUI%s with no parent', klass )

        if 'orphan' in kw:
            kw.pop('orphan')
            if 'parent' in kw:
                kw.pop('parent')

        pn = kw.get('parent',None)
        pn = (pn and pn.name ) or 'None'
        cn = kw.get('name','NoName')

        if p=='layout':
            layer= kw.pop('layer')
            dev("Widget.new (parent)%s ->%s[ (%s)%s ]", layer.parent.name ,layer.__class__.__name__, klass, cn )
        else:
            dev("Widget.new (parent)%s -> (%s)%s", pn , klass, cn )


        if klass=='Sprite':
            wdg = getattr(panda3d.lui,klass)(p,*argv)
        else:
            wdg= getattr(panda3d.lui,klass)(*argv,**kw)
        if self.__handler:
            self.set_named_widget(cn, wdg )
            if klass=='Button':
                if cn!='drag':
                    wdg.bind('click',self.__ihandler)

            return wdg
        return self.set_named_widget(cn, wdg )


    #override this one to extend the widget
    def build(self):
        pass



class DragTool:

    refs = []

    Begin = 0
    Drag  =  1
    End  = 2

    def __init__(self, host , callback, drag ):

        self.host =  host
        self.deny()


        if callback is None:
            if hasattr(host,'on_drag'):
                callback = getattr(host,'on_drag')
            else:
                callback = self.on_drag

        self.cb = callback

        self.mode = 0

        host.bind('mousedown',self.begin_drag)
        host.bind('mousemove',self.does_drag)
        host.bind('mouseup',self.end_drag)


    @classmethod
    def set(cls, host , callback= None, drag=None ):


        cls.refs.append( cls( host, callback, drag ) )


    def begin_drag(self,e,*argv):
        print('Begin: drag',e.message,argv)
        self.current = e.get_sender()


        self.accept(e)

        if self.cb:
            self.cb(self.host, self.Begin, e)

        if self.is_dragging:
            e.get_sender().request_focus()


    def accept(self,e):

        if e.message:
            btn = int(e.message)
            if btn in (0,2):
                self.mode = btn
                self.is_dragging = True
                return self.is_dragging
            print("fix no drag mode for button %s",e.message)
        self.is_dragging = False
        return self.is_dragging


    def deny(self):
        self.is_dragging = False

    def does_drag(self,e):
        if self.is_dragging:
            if self.cb:
                self.cb( self.host, self.Drag, e)

    def end_drag(self,e,*argv):
        if self.is_dragging:
            print('End : drag',e,argv)
            self.is_dragging = False
            self.current = None
            self.host.request_focus()



    def on_drag(dragtool,self,stat,e):
        if stat==dragtool.Drag:
            dfrom = dragtool.current.name
            x,y= e.get_coordinates()
            mode = '+'

            if dragtool.mode==2:
                corr=  ( (x- self.left) , (y - self.top) , )
                w,h= corr
                if not self._autoResize( w=w ,h=h ):
                    pass

            if dragtool.mode==0:
                self.left, self.top =  e.get_coordinates() - self.corr

        elif stat==dragtool.Begin:
            #default is accept
            x,y= e.get_coordinates()
            self.corr = ( (x- self.left) , (y-self.top ) )
            #drag.deny()
            WM_WIN_HANDLER.ZO +=1
            self.z_offset = WM_WIN_HANDLER.ZO

        elif stat==dragtool.End:
            pass

        else:
            err('unknow drag mode %s',stat)



class WM_WIN_HANDLER:
    ZO = 0
    win = []
    mdi = []

    @classmethod
    def wm_register(cls,self):
        if (not isinstance(self,WM_WINDOW)):
            err("%s not a WM_WINDOW",self)
            WM_WIN_HANDLER.mdi.append(self)
            self.name = "Mdi_%s"% str( len( WM_WIN_HANDLER.mdi ) ).zfill(2)
            return False


        WM_WIN_HANDLER.win.append( self )
        name = self.name
        cn = 0

        for win in WM_WIN_HANDLER.win:
            if win.name.startswith(name):
                cn+=1

        self.name = "%s_%s"%( self.name or 'Win' , str(cn).zfill(2) )
        DragTool.set(self)
        return True

    @classmethod
    def wm_ctrl(cls,e=None,win=None,wm_event=None):
        if (e or win or wm_event) is None:
            err("wm_ctrl( event=%s) OR (None,win=%s wm_event=%s)",e,win,wm_event)
            return None

        if e and not (win and wm_event):
            win , wm_event = e.sender.name.rsplit('::',1)
            for w in cls.win :
                if w.name == win:
                    win = w
                    break
            else:
                err("wm_ctrl: can't find window named [%s]",w.name)
                return

            if hasattr(win,'el_contextmenu'):
                if getattr(win,'el_contextmenu')( pdict( wm_event=wm_event ) ):
                    return None

        if wm_event == 'WM_SHADE':
            win.hide()
            return

        if wm_event == 'WM_NEW':
            try:
                #proto testing
                return TEST_OBJ(parent=win,top=30,left=40)
            except NameError:
                warn("no new tab handler")
            return

        dev("win %s wm_event %s",win,wm_event)



class WM_WINDOW(Factory):

    def __init__(self):
        Factory.__init__(self)

    # FIXME: make a real title bar
    def build(self):
        if isinstance( self, WM_WINDOW):
            WM_WIN_HANDLER.wm_register(self)

        self.setCurrentLayout('LUIHorizontalLayout',self.header_bar)
        for ctrl in [
                    self.hadd( '%s::WM_CLOSE' % self.name  , 'Label' ,text='X ', top=-10),
                    self.hadd( '%s::WM_SHADE' % self.name  , 'Label' ,text=' __ ', top=-10 ),
                    self.hadd( '%s::WM_EXPAND' % self.name , 'Label' ,text=' [_]', top=-10),
                    self.hadd( '%s::WM_NEW' % self.name , 'Label' ,text=' +Tab', top=-10),
                ]:
            ctrl.bind('click',WM_WIN_HANDLER.wm_ctrl)
            ctrl.solid = True

        self.caption = self.hadd( self.name ,  'Label' ,text='             %s          '% self.name , top=-10 )


    def _autoResize(self,x=0,y=0,w=0,h=0,minw=300,minh=300):
        if not self.width:
            return False
        if (w>0) and (h>0):
            pass
        elif x+y>0:
            w =  x - self.left
            if w< minw:
                return False
            h = y - self.top
            if h< minh:
                return False

        if self.width and self.width>0:
            if w>0:
                self.width = w
            if h>0:
                self.height = h

        if hasattr(self,'onresize'):
            return self.onresize(w,h)
        return True



class Widget(LUIFrame,Factory):
    # Container
    def __init__(self,**kw):
        super(Widget,self).__init__(self, **self.getDefault(kw) )
        Factory.__init__(self)



class VT100FB(LUISprite):

    #default_bg = "rsr/tty/bg.pgm"

    if RunTime.em:
        fb_width=1024
        fb_height=512
    else:
        fb_width=640
        fb_height=480

    fb_width=1024
    fb_height=512

    def __init__(self,title='terminal',vt=None):
        LUISprite.__init__(self,LUI.root(),panda3d.core.Texture( ),0,0,self.fb_width,self.fb_height)
        self.last_key = ''
        self.name =  title

        self.solid = True

        self.width = '100%'
        fix("LUISprite heigth=100% have not effect")

        self.fb = self.clone()

        self.line_buf = ''

    # advanced mode LUISprite number is limited , so to display more PTY , let ptmx switch framebuffer and render selected
    def hijack(self,vfb):
        fb = self.fb
        self.fb = None
        self.vfb = vfb
        self.bind("mousedown", vfb.rt_mousedown)
        self.bind("mouseup", vfb.rt_mouseup)
        return fb

    def clone(self):
        fb= panda3d.core.PNMImage(self.fb_width,self.fb_height)
        fb.makeRgb()
        return fb

    def blit(self):
        # ptmx hijack ?
        if self.fb is None:
            pnm = self.vfb.render()
            if pnm:
                self.texture.load( pnm )
            return True

        self.vt.VT_renderTo_PNM(self.fb,stdout=1,stderr=0)
        self.texture.load(self.fb)
        return True


    def onresize(self,w,h,host=None):
        self.height=h - 45
        return True

    #default:  one term one fb one luisprite, eg game console

    def attach(self,vt,blit=False):
        self.vt = vt
        self.vt.Resize(self.fb)
        self.bind("mousedown", self.rt_mousedown)
        self.bind("mouseup", self.rt_mouseup)

        if blit:
            return self.blit()
        return False

    def rt_mousedown(self,e):
        self.request_focus()
        print('rt_mousedown',e)

    def rt_mouseup(self,e):
        print('rt_mouseup',e)
        #self.parent.request_focus()

    def on_keydown(self,e):
        #print('on_keydown')
        self.last_key = e.message
        self.onkeypress( self.last_key )

    def on_keyrepeat(self,e):
        self.onkeypress( self.last_key )

    def onkeydown(self,e):
        self.last_key = e.message
        self.onkeypress( self.last_key )


    def onkeypress(self,key_name):
        dev("onkeypress key_name: [%s]",key_name)


class TAB_Utils:
    TAB_COLOR_SELECTED = (0,1,1)

    def mark_selected_tab(self,header,defcolor):
        for h in self.header_to_frame.keys():
            h.color = defcolor
        header.color = self.TAB_COLOR_SELECTED


class MDIChild(LUITabbedFrame, WM_WINDOW, TAB_Utils ):
    # Container


    def __init__(self,*argv,**kw):
        set = kw.setdefault
        caption= set('caption',None)
        caption = kw.pop('caption')


        super(MDIChild,self).__init__(self, **self.getDefault(kw) )
        if caption:
            self.name = caption
        WM_WINDOW.__init__(self)

        self.bind("keydown", self.rton_keydown)
        self.bind("keyrepeat", self.rton_keyrepeat)

    def rton_mousedown(self,e):
        if int(e.message):return
        x,y= e.get_coordinates()-(5,5)
        #x,y= e.get_coordinates()
        print("%s::%s->on_mousedown( %s , %s ) [ %s ]" % (self.parent.name,self.name,x,y,e.message) )
        LUIButton(text='%s %s' % (x,y), left=x,top=y,parent = self) #.parent ) #LUI.root() )



    def rton_keyrepeat(self,e):
        if hasattr(self.current_frame,'rt_keyrepeat'):
            if not self.current_frame.on_keyrepeat(e):
                #_info('deny %s.on_keyrepeat(%s)',self.current_frame.name , e.message)
                pass
        else:
            _info('Un-bound %s.on_keyrepeat(%s)',self.current_frame and self.current_frame.name , e.message)

    def rton_keydown(self,e):
        if hasattr(self.current_frame,'onkeydown'):
            if not self.current_frame.onkeydown(e):
                #_info('deny %s.on_keydown(%s)',self.current_frame.name , e.message)
                pass
        else:
            _info('Un-bound %s.onkeydown(%s)',self.current_frame and self.current_frame.name , e.message)

    def onresize(self,*argv):
        if self.current_frame:
            if hasattr(self.current_frame,'onresize'):
                return self.current_frame.onresize(*argv,host=self)
        return False

    def on_click(self, event):
        """ Internal on click handler """
        self.request_focus()


    def make_tab_header(self,header,frame):
        if header is None:
            header = frame.name or repr( frame )
            if len(header)>15:
                header = header[:5]+'...'+header[-5:]

        if isinstance(header, str):
            header = LUI.Button(text = header)

        self.header_bar.add(header, "?")
        self.header_to_frame[header] = frame

        header.solid = True
        header.bind("click", self._change_to_tab)
        return header

    def set_new_tab_active(self,frame):
        if self.current_frame:
            self.current_frame.hide()
        self.current_frame = frame
        self.current_frame.show()
        self.current_frame.request_focus()


    def add_tab(self,frame,header=None,**kw):
        # header
        header=self.make_tab_header(header,frame)

        # Frame
        frame.parent = self.main_frame
        #frame.width = "100%"
        #frame.height = "100%"

        # Put frame in front
        self.mark_selected_tab(header, (1,1,1) )
        self.set_new_tab_active(frame)




class TaskBar(LUITabbedFrame, Factory, TAB_Utils):
    on_prefix = 'on_'
    __name__ = 'WM'
    BOTTOM = -14
    DECAL = 35

    def __init__(self,**kw):
        super(TaskBar,self).__init__(self, **self.getDefault(kw) )
        Factory.__init__(self)
        self.last = None
        LUI.taskBar = self

    def build(self):
        self.set_handler( self )
        self.setCurrentLayout('LUIHorizontalLayout',self.header_bar)
        self.hadd('WM_NEW','Button',bottom=self.BOTTOM,left=self.BOTTOM,text='open')


    def on_WM_NEW_(self,e):
        global taskbar

        win = self.spawn( width='60%',height='60%', **self.__cascade()  )
        return self.add( win.name , win ) or win


    def add(self, header, frame):
        # header
        if header is None:
            header = frame.name or repr( frame )

        if isinstance(header, str):
            if len(header)>15:
                header = header[:5]+'...'+header[-5:]

            header = LUIButton(text = header,bottom=self.BOTTOM )
            header.name = '%s::WM_STATUS' % frame.name

        self.header_bar.add(header, "?")
        self.header_to_frame[header] = frame
        header.solid = True
        header.bind("click", self._change_to_tab)

        # Put frame in front
        #if self.current_frame is None:
        self._change_to_tab( None, header )




    def _change_to_tab(self, lui_event=None, header=None):
        if lui_event:
            header = lui_event.sender

            #clic again to hide
            if self.header_to_frame[header].visible:
                if header == self.last:
                    header.color = self.TAB_COLOR_SELECTED
                    self.header_to_frame[header].hide()
                    self.last = None
                    return
            self.mark_selected_tab(header,LUILabel.DEFAULT_COLOR)

        self.last = header

        #reset all win, then bring selected to front
        for all in self.header_to_frame.values():
            all.z_offset = 0

        self.mark_selected_tab(header, (1,1,1) )
        self.current_frame = self.header_to_frame[header]
        self.current_frame.show()
        self.current_frame.z_offset+=1

    def __cascade(self):
        c=self.DECAL * (1+ len(WM_WIN_HANDLER.mdi) + len(WM_WIN_HANDLER.win) )
        return {'left':c,'top':c}

    def spawn(self,*argv,**kw):
        set = kw.setdefault
        cascade = self.__cascade()
        set('left',cascade['left'])
        set('top',cascade['top'])
        set('caption','PTMX')
        set('width','60%')
        set('height','60')

        try:
            with use('ui') as gui:
                return gui.PTMX(*argv,**kw)
        except:
            kw.pop('caption')
            return LUI.MDIChild(*argv,**kw)



class LUI(LUIBase):
    VT100FB = VT100FB

    #Console = VT100Base
    Widget = Widget
    TaskBar  = TaskBar
    MDIChild = MDIChild
    WM_WINDOW = WM_WINDOW




for luie in __all__:
    wdgname = luie[3:]
    if wdgname:
        if not hasattr( panda3d.lui, wdgname  ):
            panda3d.lui.__all__.append( wdgname )
            setattr( panda3d.lui , wdgname , getattr( sys.modules[__name__] , luie ) )
        if not hasattr( LUI , wdgname  ):
            setattr( LUI , wdgname , getattr( sys.modules[__name__] , luie ) )

panda3d.lui.Widget = Widget


if __name__ == '__main__':
    if not RunTime.OOTB:
        import plugbase
        use= plugbase.PluginGlobalManager( { 'config': {'kbd':{}} } ).enter()
        use.setLogger(sys.modules[__name__])
        cam = use('camera.third')
        kbd = use('hid.linereader')
        mdl = use('models.loader')
        world = use('world.wp3d')
        scr = use('screen.sp3d')
        cam.setMode('third')

        lui = use('ui').lui

        lui.LUI.wipe()

        def update(task):
            global kbd
            if kbd.heardEnter():
                cmd=kbd.readline().strip().lower()
                if cmd=='e':
                    ecam = use('camera.edit')
                    ecam.setMode(scr,world)
                elif cmd=='x':
                    dr.setActive(0)
                elif cmd in  ('q','quit','exit'):
                    pluginGlobalManager.Quit = True
                    return task.exit
                else:
                    evt('map_rotate',ctx='gsc')
                #pluginGlobalManager.Quit = True
                #return direct.task.Task.Task.exit
            else:
                pluginGlobalManager.eventManager.process_one()
            return task.cont


    else:
        lui = LUI()
        lui.build()

    class autoidx:
        def __init__(self):
            self.i = -1


        def __call__(self):
            self.i += 1
            return str(self)

        def __str__(self):
            return '%s_%s'% ( hash(self) , self.i )


    class TEST_OBJ(Widget):
        pass

        def build(self):
            d = { 'section1' : [0,1,2,3] ,'section2' : [4,5,6,7] }
            keys = d.keys()
            keys.sort()
            Sect = autoidx()

            for k in keys:
                v=d[k]

                sect = Sect()
                self.vadd( sect ,'Label',text='[-] %s' % k)
                SubSect = autoidx()
                subf = self.vadd('zone_%s'% sect  ,'Widget',orphan=True,left=20,top=4)
                for elem in v:
                    #subf.vadd( SubSect() , 'Label', text = str(v) )

                    print (k,elem)








    taskbar = TaskBar(width='100%',height=24,left=0,top=0)

    win = taskbar.on_WM_NEW_(None)
    print(win)

    WM_WIN_HANDLER.wm_ctrl(win=win,wm_event="WM_NEW")






    if RunTime.OOTB:
        base.run()


