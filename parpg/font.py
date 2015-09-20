import os

from fife.extensions import pychan
from fife.extensions.pychan.fonts import Font


class PARPGFont(Font):
    """ Font class for PARPG
        This class behaves identical to PyChan's Font class except in
        initialization. Ratherthan take a name and a get object, this class
        takes a fontdef and settings object as explained below. This class is
        necessary because the original Font class was too restrictive on how it
        accepted objects

        @param fontdef: defines the font's name, size, type, and optionally 
                        row spacing as well as glyph spacing.
        @type fontdef: dictionary
        
        @param settings: settings object used to dynamically determine the
                         font's source location
        @type settings: parpg.settings.Settings object
    """
    def __init__(self, fontdef, settings):
        self.font = None
        self.name = fontdef['name']
        self.typename = fontdef['typename']

        if self.typename == 'truetype':
            self.filename = '{0}.ttf'.format(self.name.lower().split('_')[0])

        self.source = '/'.join(['fonts', self.filename])
        self.row_spacing = fontdef.get('row_spacing', 0)
        self.glyph_spacing = fontdef.get('glyph_spacing', 0)

        if self.typename == 'truetype':
            self.size = fontdef['size']
            self.antialias = fontdef['antialias']
            self.color = fontdef.get('color', [255, 255, 255])
            manager = pychan.manager.hook.guimanager
            self.font = manager.createFont(self.source, self.size, '')

            if not self.font:
                raise InitializationError('Could not load font '
                                          '{0}'.format(self.name))
        
            self.font.setAntiAlias(self.antialias)
            self.font.setColor(*self.color)
        else:
            raise InitializationError('Unsupported font type '
                                      '{0}'.format(self.typename))

        self.font.setRowSpacing(self.row_spacing)
        self.font.setGlyphSpacing(self.glyph_spacing)
