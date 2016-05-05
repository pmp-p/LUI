
import panda3d.lui
from panda3d.core import Filename
import os
from os.path import join


__all__ = ['Skin']

if not RunTime.OOTB:
    from plugbase.ui.lui.LUISkin import LUISkin
    #from plugbase.ui.lui.LUILabel import LUILabel

    import direct.stdpy.file

    def webglget(self,fn):
        fn = self.get_resource(fn)
        try:direct.stdpy.file.open(fn).close()
        except:print("LUIMetroSkin: ressource not found %s" % fn)
        return fn
else:
    from LUISkin import LUISkin
    #from LUILabel import LUILabel

    def webglget(self,fn):return self.get_resource(fn)


class Skin(LUISkin):

    """ Simple Metro / Flat UI skin """

    Loaded = None

    skin_location = os.path.dirname(os.path.abspath(__file__))

    try:
        if not RunTime.native:
            skin_location = "/rsr/LUI/Skins/Metro/"
        else:
            skin_location = "rsr/LUI/Skins/Metro/"
    except: pass


    def load(self):
        fnt1 = webglget(self, "font/Roboto-Medium.ttf" )
        panda3d.lui.LUIFontPool.get_global_ptr().register_font( "default", loader.loadFont(fnt1) )

        fnt2=webglget(self, "font/Roboto-Medium.ttf" )
        label_font = loader.loadFont(fnt2)
        label_font.set_pixels_per_unit(32)
        panda3d.lui.LUIFontPool.get_global_ptr().register_font("label", label_font )

        fnt3 = webglget(self, "font/Roboto-Light.ttf" )

        headerFont = loader.loadFont(fnt3)
        headerFont.set_pixels_per_unit(80)

        panda3d.lui.LUIFontPool.get_global_ptr().register_font("header", headerFont)

        panda3d.lui.LUIAtlasPool.get_global_ptr().load_atlas("skin",
                webglget(self,"res/atlas.txt"),
                webglget(self,"res/atlas.bmp")
            )

        # Label color
        # LUILabel.DEFAULT_COLOR = (0.0, 0.0, 0.0, 0.6)
        # LUILabel.DEFAULT_USE_SHADOW = False
