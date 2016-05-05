import panda3d.core
#panda3d.core.getModelPath().appendDirectory('/')
import panda3d.lui
import os


__all__ = ['Skin']

try:
    if not RunTime.OOTB:
        from plugbase.ui.lui.LUISkin import LUISkin
        from plugbase.ui.lui.LUILabel import LUILabel

        import direct.stdpy.file

        def webglget(self,fn):
            fn = self.get_resource(fn)
            try:direct.stdpy.file.open(fn).close()
            except:print("LUI/Skins/Default: ressource not found %s" % fn)
            return fn
except:
    from LUISkin import LUISkin
    def webglget(self,fn):
        return self.get_resource(fn)


class Skin(LUISkin):

    """ The default skin which comes with LUI """


    Loaded = None

    skin_location = os.path.dirname(os.path.abspath(__file__))

    try:
        if RunTime.native:
            skin_location = "rsr/LUI/Skins/Default/"
        else:
            skin_location = "/rsr/LUI/Skins/Default/"
    except:
        skin_location = '../Skins/Default/'

    def load(self):


        fnt1 = webglget( self, "font/SourceSansPro-Semibold.ttf" )
        panda3d.lui.LUIFontPool.get_global_ptr().register_font( "default", loader.loadFont(fnt1))

        fnt2  = webglget( self, "font/SourceSansPro-Semibold.ttf" )
        labelFont = loader.loadFont(fnt2)
        labelFont.setPixelsPerUnit(32)

        panda3d.lui.LUIFontPool.get_global_ptr().register_font("label", labelFont)

        fnt3 = webglget( self, "font/SourceSansPro-Light.ttf" )
        headerFont = loader.loadFont(fnt3)
        headerFont.setPixelsPerUnit(80)

        panda3d.lui.LUIFontPool.get_global_ptr().register_font("header", headerFont)
        panda3d.lui.LUIAtlasPool.get_global_ptr().load_atlas("skin",
                webglget(self,"res/atlas.txt"),
                webglget(self,"res/atlas.png")
            )
