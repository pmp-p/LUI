
import os

from panda3d.core import Filename
from panda3d.lui import LUIFontPool, LUIAtlasPool

class LUISkin:

    """ Abstract class, each skin derives from this class """

    skin_location = ""

    Loaded=False


    def __init__(self):
        if not self.__class__.Loaded:
            self.load()

        self.__class__.Loaded = True

    def load(self):
        """ Skins should override this. Each skin should at least provide the fonts
        'default' and 'label', and at least one atlas named 'skin' """
        raise NotImplementedError()

    def get_resource(self, pth):
        """ Turns a relative path into an absolute one, using the skin_location """
        fpth=Filename.from_os_specific(os.path.join(self.skin_location, pth)).get_fullpath()
        #print("LUISkin logger",fpth)
        return fpth


