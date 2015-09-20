from fife.extensions.pychan.widgets import VBox, HBox, ScrollArea, Button
from fife.extensions.pychan.tools import callbackWithArguments

class TabWidget(VBox):
    def min_size():
        def fget(self):
            return self._min_size
        
        def fset(self, min_size):
            self._min_size = min_size
            self.view.min_size = min_size
            #HACK: This fixes a problem when the size is set before the Widget
            #is created proper
            if hasattr(self, '__parent'):   
                 self.adaptLayout()
        
        return locals()
    min_size = property(**min_size())
    
    def max_size():
        def fget(self):
            return self._max_size
        
        def fset(self, max_size):
            self._max_size = max_size
            self.view.max_size = max_size
            #HACK: This fixes a problem when the size is set before the Widget
            #is created proper
            if hasattr(self, '__parent'):   
                self.adaptLayout()
        
        return locals()
    max_size = property(**max_size())
    
    def opaque():
        def fget(self):
            return self._getOpaque()
        
        def fset(self, opaque):
            self._setOpaque(opaque)
            self.view.opaque = opaque
            base_color = self.view.base_color
            base_red = base_color.r
            base_green = base_color.g
            base_blue = base_color.b
            background_color = self.view.background_color
            background_red = background_color.r
            background_green = background_color.g
            background_blue = background_color.b
            alpha = 255 if opaque else 0
            self.view.base_color = (base_red, base_green, base_blue, alpha)
            self.view.background_color = (background_red, background_green,
                                          background_blue, alpha)
        
        return locals()
    opaque = property(**opaque())
    
    def border_size():
        def fget(self):
            frame = self.findChild(name='frame')
            return frame.border_size
        
        def fset(self, border_size):
            frame = self.findChild(name='frame')
            frame.border_size = border_size
        
        return locals()
    border_color = property(**border_size())
    
    def __init__(self, min_size=(0, 0), max_size=(9999, 9999), border_size=1,
                 **kwargs):
        self._min_size = min_size
        self._max_size = max_size
        self.views = {}
        tab_bar = HBox(name='tabBar')
        tab_bar.min_size = (0, 20)
        tab_bar.max_size = (9999, 20)
        self.view = ScrollArea(name='view')
        self.view.min_size = self._min_size
        self.view.max_size = self._max_size
        self.view.border_size = border_size
        frame = VBox(name='frame')
        frame.border_size = border_size
        frame.opaque = 0
        frame.addChild(self.view)
        VBox.__init__(self, **kwargs)
        self.padding = 0
        VBox.addChild(self, tab_bar)
        VBox.addChild(self, frame)
        self.adaptLayout()
    
    def addTab(self, text):
        text = unicode(text)
        tab = Button(text=text)
        tab_bar = self.findChild(name='tabBar')
        tab_bar.addChild(tab)
        tab.capture(callbackWithArguments(self.showView, text))
        self.adaptLayout()
    
    def addChild(self, child):
        name = child.name or unicode(str(child))
        self.addTab(name)
        self.views[name] = child
        if len(self.views) == 1:
            # Show the first view by default.
            self.showView(name)
    
    def showView(self, name):
        view = self.views[name]
        self.view.content = view
        self.adaptLayout()
