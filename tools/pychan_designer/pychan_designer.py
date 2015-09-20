#! /usr/bin/env python2

from __future__ import print_function
import sys
import os
import logging
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from fife import fife
from fife.extensions.basicapplication import ApplicationBase, Setting
from fife.extensions import pychan

from parpg.common.optionparser import OptionParser, OptionError
from parpg.common.utils import dedent_chomp
from parpg import gui

USAGE_MESSAGE = '''\
usage: pychan_designer.py [-h] xml_script_path
Load a pychan xml script and display the gui element it contains.

    -h                show this help message
    -v                increase the verbosity of console output; may be
                        specified multiple times
    -q                decrease the verbosity of console output; may be
                        specified multiple times
'''

def is_child(widget, parent):
    """
    Recursively search a widget hierarchy to determine if the
    widget is a decendent of parent.
    """
    
    if widget is None or parent is None:
        result = False
    elif hasattr(parent, 'children'):
        if widget in parent.children:
            result = True
        else:
            result = False
            for child in parent.children:
                if is_child(widget, child):
                    result = True
                    break
    else:
        result = False
    
    return result


class LabelLogHandler(logging.Handler):
    def __init__(self, text_box, level=logging.NOTSET):
        assert hasattr(text_box, 'text') and hasattr(text_box, 'adaptLayout')
        logging.Handler.__init__(self, level=level)
        self.text_box = text_box
    
    def emit(self, record):
        message= self.format(record)
        self.text_box.text = unicode(message, 'utf8')
        self.text_box.adaptLayout()

class TextBoxLogHandler(LabelLogHandler):
    def emit(self, record):
        message= self.format(record)
        self.text_box.text = '\n'.join([self.text_box.text, message])
        self.text_box.adaptLayout()


class GuichanDesignerApplication(ApplicationBase):
    def __init__(self, settings_file='settings-dist.xml'):
        setting = Setting(settings_file=settings_file)
        super(GuichanDesignerApplication, self).__init__(setting=setting)
        # PyChanDesigner fonts
        pychan.loadFonts('fonts/freefont.fontdef')
        pychan.setupModalExecution(self.mainLoop, self.breakFromMainLoop)
        # pychan default settings need an overwrite, because we don't like some aspects (like opaque widgets)
        screen_width, screen_height = \
            [int(dimension) for dimension in
             setting.get('FIFE', 'ScreenResolution').split('x')]
        self.xml_script_path = ''
        self.active_widget = None
        self.selected_widget = None
        self.widget_stack = []
        self.logger = logging.getLogger('PychanDesignerApplication')
        self.xml_editor = pychan.loadXML('gui/xml_editor.xml')
        self.console = pychan.loadXML('gui/console.xml')
        with file('gui/pychan_designer.xml') as xml_file:
            self.gui = pychan.loadXML(xml_file)
        self.gui.min_size = (screen_width, screen_height)
        self.gui.max_size = (screen_width, screen_height)
        editor = self.gui.findChild(name='editor')
        editor.content = self.xml_editor
        self.gui.mapEvents(
            {
                'exitButton': self.quit,
                'reloadButton': self.reloadXml,
                'applyButton': self.applyXml,
                'saveButton': self.saveXml,
                'xmlEditorTab': self.showXmlEditor,
                'consoleTab': self.showConsole,
            }
        )
        self.gui.adaptLayout()
        self.gui.show()

    def showXmlEditor(self):
        editor = self.gui.findChild(name='editor')
        editor.content = self.xml_editor

    def showConsole(self):
        editor = self.gui.findChild(name='editor')
        editor.content = self.console

    def setupLogging(self, level):
        console = self.console
        self.logger.setLevel(level)
        console_handler = TextBoxLogHandler(console, level)
        console_formatter = \
            logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        status_bar = self.gui.findChild(name='statusBar')
        status_bar_handler = LabelLogHandler(status_bar, logging.ERROR)
        self.logger.addHandler(status_bar_handler)

    def _applyActivateEventCapture(self, widget):
        widget.capture(self._activateCallback, 'mouseEntered')
        widget.capture(self._deactivateCallback, 'mouseExited')

    def selectWidget(self):
        widget = self.widget_stack[0]
        self.selected_widget = widget
        property_viewer = self.gui.findChild(name='propertyViewer')
        columns = property_viewer.content
        name_rows = columns.findChild(name='propertyNameColumnRows')
        value_rows = columns.findChild(name='propertyValueColumnRows')
        name_rows.removeAllChildren()
        value_rows.removeAllChildren()
        assert len(name_rows.children) == 0 and \
               len(value_rows.children) == 0, \
               'propertyViewer was not properly cleared!'
        for attribute in sorted(widget.ATTRIBUTES,
                                cmp=lambda a, b: cmp(a.name, b.name)):
            name = attribute.name
            name_label = pychan.Label(text=unicode(name, 'utf8'))
            name_label.font = 'FreeMono'
            name_label.background_color = (250, 250, 250)
            name_container = pychan.HBox()
            name_container.border_size = 1
            name_container.base_color = (250, 250, 250)
            name_container.addChild(name_label)
            alternate_name = '_'.join(['old', name])
            if hasattr(widget, alternate_name):
                value = getattr(widget, alternate_name)
            else:
                value = getattr(widget, name)
            if isinstance(value, fife.Color):
                value = (value.r, value.g, value.b, value.a)
            elif isinstance(value, fife.GuiFont):
                value = value.name
            elif isinstance(value, fife.GuiImage):
                # FIXME Technomage 2011-01-27: Unfortunately I haven't found a
                #     way to display the image path only, so for now it's being
                #     skipped.
                continue
            value_label = pychan.TextField(text=unicode(repr(value), 'utf8'))
            value_label.font = 'FreeMono'
            value_label.background_color = (220, 220, 220)
            value_label.min_size = (0, 20)
            value_container = pychan.HBox()
            value_container.border_size = 1
            value_container.min_size = (0, 24)
            value_container.base_color = (250, 250, 250)
            value_container.addChild(value_label)
            name_container.min_size = value_container.min_size
            
            value_label.capture(
                self._createChangeAttributeCallback(name, widget,
                                                    type(attribute)),
                'keyPressed'
            )
            name_rows.addChild(name_container)
            value_rows.addChild(value_container)
        columns.adaptLayout()
        
        if self.selected_widget is not None:
            self.unhighlightWidget(self.selected_widget)
        self.highlightWidget(widget)

    def _createChangeAttributeCallback(self, attribute_name, wrapped_widget,
                                       attribute_type):
        def _changeAttributeCallback(widget, event):
            if (event.getKey().getValue() == pychan.events.guichan.Key.ENTER):
                try:
                    value = eval(widget.text)
                    setattr(wrapped_widget, attribute_name, value)
                except (ValueError, TypeError, NameError) as exception:
                    self.logger.error(exception)
                    widget.text = unicode(getattr(wrapped_widget,
                                                  attribute_name))
        return _changeAttributeCallback

    def _activateCallback(self, widget):
        self.logger.debug(
            'mouse entered {0}(name={1!r})'.format(
                type(widget).__name__,
                widget.name
            )
        )
        if len(self.widget_stack) == 0:
            self.widget_stack.append(widget)
            self.activateWidget(widget)
        elif is_child(self.widget_stack[0], widget):
            self.widget_stack.append(widget)
        else:
            parent = self.widget_stack[0]
            self.widget_stack.insert(0, widget)
            self.deactivateWidget(parent)
            self.activateWidget(widget)

    def _deactivateCallback(self, widget):
        self.logger.debug(
            'mouse exited {0}(name={1!r})'.format(
                type(widget).__name__,
                widget.name
            )
        )
        widget_stack = self.widget_stack
        index = widget_stack.index(widget)
        self.deactivateWidget(widget)
        if index == 0 and len(widget_stack) > 1:
            parent = widget_stack[1]
            self.activateWidget(parent)
        widget_stack.remove(widget)

    def activateWidget(self, widget):
        self.highlightWidget(widget)
        self.logger.debug(
            'activated {0}(name={1!r})'.format(
                type(widget).__name__,
                widget.name
            )
        )

    def deactivateWidget(self, widget):
        self.unhighlightWidget(widget)
        self.logger.debug(
            'deactivated {0}(name={1!r})'.format(
                type(widget).__name__,
                widget.name
            )
        )

    def highlightWidget(self, widget):
        if not hasattr(widget, 'highlighted') or not widget.highlighted:
            widget.highlighted = True
            widget.old_base_color = widget.base_color
            widget.base_color = (255, 0, 0)
            widget.old_background_color = widget.background_color
            widget.background_color = (255, 0, 0)
            widget.old_border_size = widget.border_size
            widget.border_size = 1
            if hasattr(widget, 'opaque'):
                widget.old_opaque = widget.opaque
                widget.opaque = 1
            widget.adaptLayout()
    
    def unhighlightWidget(self, widget):
        if hasattr(widget, 'highlighted') and widget.highlighted:
            widget.highlighted = False
            widget.base_color = widget.old_base_color
            widget.background_color = widget.old_background_color
            widget.border_size = widget.old_border_size
            if hasattr(widget, 'opaque'):
                widget.opaque = widget.old_opaque
            widget.adaptLayout()

    def saveXml(self):
        with file(self.xml_script_path, 'w') as xml_file:
            xml_content = self.xml_editor.text
            xml_file.write(xml_content)
        self.logger.info('saved file {0}'.format(self.xml_script_path))

    def applyXml(self):
        xml_content = self.xml_editor.text
        xml_stream = StringIO(str(xml_content))
        xml_stream.seek(0)
        self.loadXml(xml_stream)

    def reloadXml(self):
        with file(self.xml_script_path, 'r') as xml_file:
            self.loadXml(xml_file)

    def loadXml(self, xml_file):
        self.logger.debug(
            'loading file {0}'.format(getattr(xml_file, 'name', ''))
        )
        top_widget = pychan.loadXML(xml_file)
        top_widget.deepApply(self._applyActivateEventCapture)
        top_widget.deepApply(lambda widget: widget.capture(self.selectWidget,
                                                           'mousePressed'))
        widget_preview = self.gui.findChild(name='widgetPreview')
        widget_preview.content = top_widget
        top_widget.adaptLayout()
        # FIXME Technomage 2011-01-23: Containers are not displayed with their
        #     background images when attached to another widget. A workaround
        #     is to call beforeShow after attaching the container.
        if isinstance(top_widget, pychan.Container):
            top_widget.beforeShow()
        xml_editor = self.xml_editor
        xml_file.seek(0)
        xml_editor.text = unicode(xml_file.read(), 'utf8')
        xml_editor.resizeToContent()
        self.logger.info(
            'successfully loaded file {0}'.format(
                getattr(xml_file, 'name', '')
            )
        )


def main(argv=sys.argv):
    option_parser = OptionParser(
        usage=USAGE_MESSAGE,
        args=argv[1:]
    )
    logging_level = logging.WARNING
    for option in option_parser:
        if option == '-h' or option =='--help':
            print(option_parser.usage)
            sys.exit(0)
        elif option == '-v':
            logging_level -= 10
        elif option == '-q':
            logging_level += 10
        else:
            print('Error: unknown option {0!r}\n'.format(option),
                  file=sys.stderr)
            print(option_parser.usage, file=sys.stderr)
            sys.exit(1)
    try:
        xml_script_path = os.path.abspath(option_parser.get_next_prog_arg())
    except OptionError as exception:
        print('Error: {0}\n'.format(exception), file=sys.stderr)
        print(option_parser.usage, file=sys.stderr)
        sys.exit(1)
    application = GuichanDesignerApplication()
    application.setupLogging(logging_level)
    parpg_root = os.path.abspath(os.path.join('..', '..', 'game'))
    os.chdir(parpg_root)
    # Load PARPG fonts
    fonts_directory = os.path.abspath('fonts')
    file_names = os.listdir(fonts_directory)
    for file_name in file_names:
        base_name, extension = os.path.splitext(file_name)
        if extension == '.fontdef':
            file_path = os.path.join(fonts_directory, file_name)
            pychan.loadFonts(file_path)
    application.xml_script_path = xml_script_path
    with file(xml_script_path) as xml_file:
        application.loadXml(xml_file)
    application.run()


if __name__ == '__main__':
    main()
