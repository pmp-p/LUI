
from __future__ import print_function, division

from LUIObject import LUIObject
from LUISprite import LUISprite
from LUIHorizontalLayout import LUIHorizontalLayout
from direct.directnotify.DirectNotify import DirectNotify

from LUIInitialState import LUIInitialState

__all__ = ["LUIHorizontalStretchedLayout"]

class LUIHorizontalStretchedLayout(LUIObject):

    """ A layout which takes 3 sprites, a left sprite, a right sprite, and a
    middle sprite. While the left and right sprites remain untouched, the middle
    one will be stretched to fit the layout """

    def __init__(self, parent=None, prefix="ButtonDefault", **kwargs):
        LUIObject.__init__(self)
        self._layout = LUIHorizontalLayout(self, spacing=0)
        self._layout.width = "100%"
        self._sprite_left = LUISprite(self._layout.cell(), "blank", "skin")
        self._sprite_mid = LUISprite(self._layout.cell('*'), "blank", "skin")
        self._sprite_right = LUISprite(self._layout.cell(), "blank", "skin")
        if parent is not None:
            self.parent = parent
        self.prefix = prefix
        LUIInitialState.init(self, kwargs)

    def set_prefix(self, prefix):
        """ Sets the layout prefix, this controls which sprites will be used """
        self._sprite_left.set_texture(prefix + "_Left", "skin")
        self._sprite_mid.set_texture(prefix, "skin")
        self._sprite_right.set_texture(prefix + "_Right", "skin")
        self._sprite_mid.width = "100%"
        self._prefix = prefix

    def get_prefix(self):
        """ Returns the layout prefix """
        return self._prefix

    prefix = property(get_prefix, set_prefix)
