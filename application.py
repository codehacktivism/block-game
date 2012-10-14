import pyglet
from pyglet.gl import *
from pyglet.sprite import Sprite
from pyglet.text import Label
from pyglet.text.caret import Caret
from pyglet.text.document import UnformattedDocument
from pyglet.text.layout import IncrementalTextLayout
from pyglet.window import key

import string

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def set_menu_style(**kwargs):
    '''Updates the dictionary that determines the visual style of menus.
    Keyword aruments are used to specify values. If a value is ommitted its
    value in the default style is used instead.
    '''
    global MENU_STYLE
    MENU_STYLE = DEFAULT_MENU_STYLE.copy()
    MENU_STYLE.update(kwargs)
    
def draw_cursor(width, height, color):
    '''Default cursor style for menus.'''
    glColor3f(*color)
    
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(-height, -height / 2)
    glVertex2f(-height, height / 2)
    glEnd()
    
    glTranslatef(width, 0, 0)
    
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(height, height / 2)
    glVertex2f(height, -height / 2)
    glEnd()

DEFAULT_MENU_STYLE = {
    'width': 300,
    'height': 300,
    'title_size': 30,
    'text_size': 20,
    'text_spacing': 2,
    'text_width': 200,
    'draw_cursor': draw_cursor,
    'title_color': (255, 0, 0, 255),
    'text_color': (255, 255, 255, 255),
    'header_color': (255, 255, 0, 255),
    'cursor_color': (0.0, 1.0, 0.0),
    'bg_color': (0.0, 0.0, 0.0),
    'bg_image': None,
}

MENU_STYLE = DEFAULT_MENU_STYLE

class PageException(Exception):
    '''Raised when a page can't be found or an empty page stack is popped.'''
    pass
    
class Page(object):
    '''Represents any visual section of an application. Used for organizing
    application state.
    '''
    def __init__(self, app):
        self.app = app
        self.batch = pyglet.graphics.Batch()
        
    def on_focus(self):
        '''Called when the page is pushed onto the stack and when a page is
        popped to reveal this page.
        '''
        pass
        
    def on_unfocus(self):
        '''Called when a page is pushed onto the stack to hide this page and
        when this page is popped off the stack.
        '''
        pass
        
    def on_destroy(self):
        '''Called when this page is popped off the stack.'''
        pass
        
    def draw(self):
        glLoadIdentity()
        self.batch.draw()

class MenuException(Exception):
    '''Raised when a menu performs an illegal operation.'''
    pass

class MenuItem(object):
    '''Represents a single item in a menu.'''
    
    def __init__(self, name, menu, selectable=True):
        self.name = name
        self.menu = menu
        self.selectable = selectable
        self.label = Label(name,
                           color=MENU_STYLE['text_color'],
                           font_size=MENU_STYLE['text_size'],
                           batch=menu.batch)
        
    def on_key_press(self, symbol, modifiers):
        '''Called when a key press occurrs while  this item is selected.'''
        pass
        
    def on_key_release(self, symbol, modifiers):
        '''Called when a key release occurrs while this item is selected.'''
        pass
        
class TitleItem(MenuItem):
    def __init__(self, name, menu):
        super(TitleItem, self).__init__(name, menu, selectable=False)
        self.label.font_size = MENU_STYLE['title_size']
        
class LabelItem(MenuItem):
    def __init__(self, name, menu):
        super(TitleItem, self).__init__(name, menu, selectable=False)
        
class NavItem(MenuItem):
    '''A menu item that takes the user to a different page when executed.
    Destinations take the form of the class name of the destination page, the
    target, prefixed with an optional method by which to navigate. The method
    '+', the default, pushes a new instance of the class onto the page stack.
    The method '-' pops pages off the stack until an instance of the class is
    reached. If a single '-' is used, the stack is popped once.
    '''
    
    def __init__(self, name, dest, menu):
        super(NavItem, self).__init__(name, menu)
        self.dest = dest
        
        if len(self.dest) == 0:
            self.method = '-'
            self.target = None
        elif len(self.dest) == 1:
            self.method = self.dest
            self.target = None
        elif self.dest[0] in string.ascii_letters + '_':
            self.method = '+'
            self.target = self.dest
        else:
            self.method = self.dest[0]
            self.target = self.dest[1:]
            
    def on_key_press(self, symbol, modifiers):
        if symbol == key.RETURN:
            if self.method == '+':
                if self.target == None:
                    raise MenuException('Pushing requires a target.')
                self.menu.app.push_page(self.target)
            elif self.method == '-':
                self.menu.app.pop_page(self.target)
            else:
                raise MenuException('Unknown method "{0}"'.format(method))
                
class TextItem(MenuItem):
    CHARS = string.ascii_letters + string.punctuation + ' '
    CURSOR = '_'
    BLINK_SPEED = 2
    
    def __init__(self, name, length, menu):
        super(TextItem, self).__init__(name, menu)
        self.text = ''
        self.length = length
        self.update_label()
        
    def on_key_press(self, symbol, modifiers):
        if symbol < 256 and chr(symbol) in self.CHARS:
            if len(self.text) < self.length:
                self.text += chr(symbol)
                self.update_label()
        elif symbol == key.BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[:-1]
                self.update_label()
            
    def update_label(self, cursor=True):
        text = '{0}: {1}'.format(self.name, self.text)
        if cursor:
            text += self.CURSOR
        self.label.text = text
        
class Menu(Page):
    '''A menu holds a collection of menu items which can be navigated through
    and interacted with.
    '''
    
    def __init__(self, app):
        super(Menu, self).__init__(app)
        self.items = []
        self.selection = 0
        self.cur_item = None
        
        if MENU_STYLE['bg_image']:
            self.bg_image = Sprite(MENU_STYLE['bg_image'], batch=self.batch)
        
    def set_items(self, *items):
        self.items = items
        
        style = MENU_STYLE
        y = style['height']
        x = (style['width'] - style['text_width']) / 2
        
        for item in self.items:
            item.label.batch = self.batch
            y -= item.label.font_size * style['text_spacing']
            item.label.x = x
            item.label.y = y
        
    def select(self, drc):
        '''Uses the sign of drc to navigate upwards or downwards in the menu.'''
        drc = sign(drc)
        i = self.selection + drc
        i %= len(self.items)
        while not self.items[i].selectable:
            i += drc
            i %= len(self.items)
        self.selection = i
        self.cur_item = self.items[i]
        
    def on_focus(self):
        for i, item in enumerate(self.items):
            if item.selectable:
                self.selection = i
                self.cur_item = item
                break
        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.select(-1)
        elif symbol == key.DOWN:
            self.select(1)
        else:
            self.cur_item.on_key_press(symbol, modifiers)
        
    def on_key_release(self, symbol, modifiers):
        self.cur_item.on_key_release(symbol, modifiers)
        
    def draw(self):
        super(Menu, self).draw()
        label = self.cur_item.label
        glTranslatef(label.x,
                     label.y + label.font_size / 2,
                     0)
        MENU_STYLE['draw_cursor'](MENU_STYLE['text_width'],
                                  MENU_STYLE['text_spacing'] * label.font_size,
                                  MENU_STYLE['cursor_color'])

class Application(pyglet.window.Window):
    '''A window that manages a stack of pages. The page on the top of the stack
    at any given time receives events from the window as well as being drawn
    every frame. Pages below the top are simply stored until they are needed
    again and pages that are popped off the stack are discarded.'''
    
    def __init__(self, width, height, **kwargs):
        super(Application, self).__init__(width, height, **kwargs)
        self.pages = {}
        self.page_stack = []
        
    def add_page(self, page):
        '''Takes a class that subclasses Page and adds it to the dictionary of
        pages that the application knows about.
        '''
        self.pages[page.__name__] = page
        page.app = self
        
    def add_pages(self, *pages):
        for page in pages:
            self.add_page(page)
        
    def push_page(self, name):
        '''Pushes a new instance of the class named by name onto the page stack,
        adding its event handlers and popping the previous page's event
        handlers.
        '''
        if name not in self.pages:
            raise PageException('No such page "{0}"'.format(name))
        
        if len(self.page_stack) > 0:
            self.page_stack[-1].on_unfocus()
            self.pop_handlers()
        
        new_page = self.pages[name](self)
        new_page.on_focus()
        self.page_stack.append(new_page)
        self.push_handlers(new_page)
        
    def pop_page(self, target=None):
        '''Discards the top page and removes its event listeners. Pushes the
        next page's event listeners onto the stack.
        '''
        if len(self.page_stack) == 0:
            if target != None:
                raise PageException('No page in stack "{0}"'.format(target))
            else:
                raise PageException('Page stack empty.')
            
        self.page_stack[-1].on_unfocus()
        self.page_stack[-1].on_destroy()
        self.pop_handlers()
        self.page_stack.pop()
        
        if len(self.page_stack) > 0:
            self.page_stack[-1].on_focus()
            self.push_handlers(self.page_stack[-1])
        else:
            self.close()
            
        if target != None:
            if self.page_stack[-1].__class__.__name__ != target:
                self.pop_page(target)
        
    def on_draw(self):
        self.clear()
        if len(self.page_stack) > 0:
            self.page_stack[-1].draw()
            

