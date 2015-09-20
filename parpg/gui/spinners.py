from fife.extensions.pychan.widgets import (ImageButton, TextField, HBox,
    Spacer)
from fife.extensions.pychan.attrs import Attr, IntAttr, BoolAttr

class ListAttr(Attr):
    def parse(self, value):
        list_ = value.split(',')
        return list_


class Spinner(HBox):
    ATTRIBUTES = HBox.ATTRIBUTES + [
        ListAttr('items'),
        IntAttr('default_item_n'),
        BoolAttr('circular'),
    ]
    
    def default_item_n():
        def fget(self):
            return self._default_item_n
        
        def fset(self, index):
            if len(self.items) -1 >= index:
                self._default_item_n = index
                self.text_field.text = self.items[index]
            else:
                error_message = \
                    'default_item_n exceeds number of items in spinner'
                raise ValueError(error_message)
        
        return locals()
    default_item_n = property(**default_item_n())
    
    def items():
        def fget(self):
            return self._items
        
        def fset(self, items):
            self._items = map(unicode, items)
            if self.default_item_n > len(items) - 1:
                self.default_item_n = 0
            self.text_field.text = self.items[self.default_item_n] if \
                                   len(self.items) > 0 else u''
        
        return locals()
    items = property(**items())
    
    def background_color():
        def fget(self):
            return self.text_field.background_color
        
        def fset(self, background_color):
            self.text_field.background_color = background_color
        
        return locals()
    background_color = property(**background_color())
    
    def font():
        def fget(self):
            return self.text_field.font
        
        def fset(self, font):
            self.text_field.font = font
        
        return locals()
    font = property(**font())
    
    def background_color():
        def fget(self):
            return self.text_field.background_color
        
        def fset(self, background_color):
            self.text_field.background_color = background_color
        
        return locals()
    background_color = property(**background_color())
    
    def min_size():
        def fget(self):
            return self._min_size
        
        def fset(self, min_size):
            self._min_size = min_size
            self.decrease_button.capture(self.previousItem)
            increase_button_width, increase_button_height = \
                self.increase_button.size
            decrease_button_width, decrease_button_height = \
                self.decrease_button.size
            text_field_width = min_size[0] - (2 * self.padding) - \
                               (increase_button_width + decrease_button_width)
            self.text_field.min_width = text_field_width
            self.text_field.max_width = text_field_width
            self.text_field.min_height = min_size[1]
        
        return locals()
    min_size = property(**min_size())
    
    
    def max_size():
        def fget(self):
            return self._max_size
        
        def fset(self, max_size):
            self._max_size = max_size
            self.decrease_button.capture(self.previousItem)
            increase_button_width, increase_button_height = \
                self.increase_button.size
            decrease_button_width, decrease_button_height = \
                self.decrease_button.size
            text_field_width = max_size[0] - (2 * self.padding) - \
                               (increase_button_width + decrease_button_width)
            self.text_field.max_width = text_field_width
            self.text_field.max_height = max_size[1]
        
        return locals()
    max_size = property(**max_size())
    
    def __init__(self, items=None, default_item_n=0, circular=True,
                 min_size=(50, 14), max_size=(50, 14), font=None, background_color=None, **kwargs):
        self._current_index = 0
        self._items = map(unicode, items) if items is not None else []
        self._default_item_n = default_item_n
        self._min_size = min_size
        self.circular = circular
        padding = 1
        self.text_field = TextField(background_color=background_color)
        self.decrease_button = ImageButton(
            up_image='gui/buttons/left_arrow_up.png',
            down_image='gui/buttons/left_arrow_down.png',
            hover_image='gui/buttons/left_arrow_hover.png',
        )
        # FIXME Technomage 2011-03-05: This is a hack to prevent the button
        #     from expanding width-wise and skewing the TextField orientation.
        #     Max size shouldn't be hard-coded like this though...
        self.decrease_button.max_size = (12, 12)
        self.decrease_button.capture(self.previousItem)
        self.increase_button = ImageButton(
            up_image='gui/buttons/right_arrow_up.png',
            down_image='gui/buttons/right_arrow_down.png',
            hover_image='gui/buttons/right_arrow_hover.png',
        )
        self.increase_button.capture(self.nextItem)
        increase_button_width, increase_button_height = \
            self.increase_button.size
        decrease_button_width, decrease_button_height = \
            self.decrease_button.size
        self.text_field = TextField(font=font)
        text_field_width = min_size[0] - (2 * padding) - \
                           (increase_button_width + decrease_button_width)
        self.text_field.min_width = text_field_width
        self.text_field.max_width = text_field_width
        self.text_field.min_height = min_size[1]
        self.text_field.text = self.items[default_item_n] if \
                               len(self.items) > 0 else u''
        HBox.__init__(self, **kwargs)
        self.opaque = 0
        self.padding = padding
        self.margins = (0, 0)
        self.addChildren(self.decrease_button, self.text_field,
                         self.increase_button)
    
    def nextItem(self, event, widget):
        if self.circular:
            if self._current_index < len(self.items) - 1:
                self._current_index += 1
            else:
                self._current_index = 0
            self.text_field.text = self.items[self._current_index]
        elif self._current_index < len(self.items) - 1:
            self._current_index += 1
            self.text_field.text = self.items[self._current_index]
    
    def previousItem(self, event, widget):
        if self.circular:
            if self._current_index > 0:
                self._current_index -= 1
            else:
                self._current_index = len(self.items) - 1
            self.text_field.text = self.items[self._current_index]
        elif self._current_index > 0:
            self._current_index -= 1
            self.text_field.text = self.items[self._current_index]


class IntSpinner(Spinner):
    ATTRIBUTES = Spinner.ATTRIBUTES + [
        IntAttr('lower_limit'),
        IntAttr('upper_limit'),
        IntAttr('step_size'),
    ]
    
    def lower_limit():
        def fget(self):
            return self._lower_limit
        
        def fset(self, lower_limit):
            self._lower_limit = lower_limit
            integers = range(lower_limit, self.upper_limit + 1, self.step_size)
            self.items = integers
        
        return locals()
    lower_limit = property(**lower_limit())
    
    def upper_limit():
        def fget(self):
            return self._upper_limit
        
        def fset(self, upper_limit):
            self._upper_limit = upper_limit
            integers = range(self.lower_limit, upper_limit + 1, self.step_size)
            self.items = integers
        
        return locals()
    upper_limit = property(**upper_limit())
    
    def step_size():
        def fget(self):
            return self._step_size
        
        def fset(self, step_size):
            self._step_size = step_size
            integers = range(self.lower_limit, self.upper_limit + 1, step_size)
            self.items = integers
        
        return locals()
    step_size = property(**step_size())
    
    def __init__(self, lower_limit=0, upper_limit=100, step_size=1, **kwargs):
        self._lower_limit = lower_limit
        self._upper_limit = upper_limit
        self._step_size = step_size
        integers = range(lower_limit, upper_limit + 1, step_size)
        Spinner.__init__(self, items=integers, **kwargs)

