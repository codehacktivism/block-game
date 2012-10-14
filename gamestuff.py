
import pyglet
from pyglet.window import key
from pyglet.gl import *

from blockstuff import *
from drawing import *
from keydict import *
import application
from application import MenuItem, NavItem, TextItem, TitleItem

MENU_IMAGE = pyglet.image.load('res/menu.jpg')
GAME_IMAGE = pyglet.image.load('res/game_bg.jpg')

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

FIELD_WIDTH = 10
FIELD_HEIGHT = 20
SQUARE_SIZE = WINDOW_HEIGHT / (FIELD_HEIGHT + 2)

SCORES_FILE = './scores.txt'
SCORE_TEXT = 'Your score: {0}\nHigh score: {1}'
LINES_TEXT = 'Lines: {0}'
LEVEL_TEXT = 'Level: {0}'
NEXT_LEVEL_TEXT = 'Next in: {0}'
POINTS_TEXT = 'Points: {0}'

KEY_DELAY = 3

application.set_menu_style(
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT - 120,
    text_width=WINDOW_WIDTH / 2,
    draw_cursor=draw_cursor_border,
    bg_image=MENU_IMAGE,
)

class MainMenu(application.Menu):
    def __init__(self, app):
        super(MainMenu, self).__init__(app)
        
        self.title = ''
        self.set_items(
            NavItem('New game', 'GamePage', self),
            NavItem('Quit', 'QuitPage', self),
        )
        
        self.scores_label = pyglet.text.Label(
            font_size=20, color=(255, 0, 0, 255), x=160, y=60,
            multiline=True, width=WINDOW_WIDTH / 2)
        
    def on_focus(self):
        super(MainMenu, self).on_focus()
        self.scores_label.text = SCORE_TEXT.format(
            self.app.last_score, self.app.high_score)
            
    def draw(self):
        super(MainMenu, self).draw()
        glLoadIdentity()
        self.scores_label.draw()
        
class PauseMenu(application.Menu):
    def __init__(self, app):
        super(PauseMenu, self).__init__(app)
        
        self.set_items(
            TitleItem('Paused', self),
            NavItem('Continue', '-GamePage', self),
            NavItem('Main menu', '-MainMenu', self),
            NavItem('Quit', 'QuitPage', self),
        )
        
class NewScoreMenu(application.Menu):
    def __init__(self, app):
        super(NewScoreMenu, self).__init__(app)
        
        self.set_items(
            TitleItem('New High Score!', self),
            TextItem('Name', 15, self),
            NavItem('Enter', '-', self),
        )

class QuitPage(application.Menu):
    def __init__(self, app):
        super(QuitPage, self).__init__(app)
        
        self.set_items(
            TitleItem('Bye bye!', self),
            MenuItem(':)', self),
        )
        
    def on_focus(self):
        super(QuitPage, self).on_focus()
        pyglet.clock.schedule_once(lambda dt: self.app.close(), 1)

class GamePage(application.Page):
    def __init__(self, app):
        super(GamePage, self).__init__(app)
        self.field = BlockField(FIELD_WIDTH, FIELD_HEIGHT)
        self.keys = KeyDict()
        
        self.bg = pyglet.sprite.Sprite(GAME_IMAGE, batch=self.batch)
        
        font_size = SQUARE_SIZE
        x = (FIELD_WIDTH + 2) * SQUARE_SIZE
        y = (FIELD_HEIGHT - 5) * SQUARE_SIZE
        
        self.lines_label = pyglet.text.Label(
            font_size=font_size, x=x, y=y, batch=self.batch)
        self.level_label = pyglet.text.Label(
            font_size=font_size, x=x, y=y - font_size, batch=self.batch)
        self.next_level_label = pyglet.text.Label(
            font_size=font_size, x=x, y=y - 2 * font_size, batch=self.batch)
        self.points_label = pyglet.text.Label(
            font_size=font_size, x=x, y=y - 3 * font_size, batch=self.batch)
            
        self.update_labels()
        
    def on_focus(self):
        pyglet.clock.schedule_interval(self.step, 1.0/self.field.MAX_SPEED)
        
    def on_unfocus(self):
        self.keys.clear()
        pyglet.clock.unschedule(self.step)
        
    def on_destroy(self):
        self.app.set_last_score(self.field.points)
        
    def step(self, dt):
        self.process_input()
        self.field.update(dt)
        if self.field.state == self.field.OVER:
            self.app.pop_page()
        self.update_labels()
        
    def update_labels(self):
        self.lines_label.text = LINES_TEXT.format(self.field.lines)
        self.level_label.text = LEVEL_TEXT.format(self.field.level)
        self.next_level_label.text = NEXT_LEVEL_TEXT.format(
            self.field.next_level - self.field.lines)
        self.points_label.text = POINTS_TEXT.format(self.field.points)
    
    def process_input(self, delay=KEY_DELAY):
        if self.keys.poll_key_once(key.UP) > delay:
            self.field.drop()
        if self.keys.poll_key(key.LEFT) > delay:
            self.field.move(BlockField.LEFT)
        if self.keys.poll_key(key.RIGHT) > delay:
            self.field.move(BlockField.RIGHT)
        if self.keys.poll_key(key.DOWN) > delay:
            self.field.fall()
        if self.keys.poll_key_once(key.Z) > delay:
            self.field.rotate(BlockField.LEFT)
        if self.keys.poll_key_once(key.X) > delay:
            self.field.rotate(BlockField.RIGHT)
            
    def draw(self):
        super(GamePage, self).draw()
        glScalef(SQUARE_SIZE, SQUARE_SIZE, 1.0)
        glTranslatef(1, 1, 0)
        draw_block_field(self.field)
        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.P:
            self.app.push_page('PauseMenu')
        else:
            self.keys.press_key(symbol)
            self.process_input(delay=0)
        
    def on_key_release(self, symbol, modifiers):
        self.keys.release_key(symbol)
        
class BlockGame(application.Application):
    def __init__(self):
        super(BlockGame, self).__init__(
            WINDOW_WIDTH, WINDOW_HEIGHT, caption='Block game')
        self.add_pages(
            MainMenu,
            PauseMenu,
            NewScoreMenu,
            QuitPage,
            GamePage
        )
        
        self.high_score = self.load_high_score()
        self.last_score = 0
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.push_page('MainMenu')
        
    def load_high_score(self):
        try:
            scores = open(SCORES_FILE, 'r')
            high_score = int(scores.readline())
            scores.close()
        except:
            scores = open(SCORES_FILE, 'w')
            scores.write('0')
            scores.close()
            high_score = 0
        return high_score
            
    def set_last_score(self, score):
        if score > self.high_score:
            scores = open(SCORES_FILE, 'w')
            scores.write(str(score))
            scores.close()
            self.high_score = score
        self.last_score = score
        

