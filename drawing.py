
from ctypes import *
import pyglet
from pyglet.gl import *

from geom import *

def draw_block(block):
    glColor3f(*block.color)
    for square in block:
        x1 = square[0]
        x2 = square[0] + 1
        y1 = -square[1]
        y2 = -square[1] - 1
        # glRectf(x1, y1, x2, y2)
        glLineWidth(3)
        glBegin(GL_LINES)
        if not block.matrix.get((-y1 - 1, x1), False):
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
        if not block.matrix.get((-y1, x1 + 1), False):
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
        if not block.matrix.get((-y1 + 1, x1), False):
            glVertex2f(x1, y2)
            glVertex2f(x2, y2)
        if not block.matrix.get((-y1, x1 - 1), False):
            glVertex2f(x1, y1)
            glVertex2f(x1, y2)
        glEnd()
        
def draw_block_dump(dump):
    y = dump.rows
    x = 0
    row = col = 0
    for square in dump:
        if x == dump.cols:
            x = 0
            y -= 1
            row += 1
            col = 0
        if square == 0:
            x += 1
            col += 1
            continue
        
        x1 = x
        x2 = (x + 1)
        y1 = y
        y2 = (y - 1)
        w = 0.1
        
        # glColor3f(*square)
        glColor3f(0.0, 0.0, 0.0)
        
        if not dump.get((row - 1, col), 0) == square:
            glRectf(x1, y1, x2, y1 - w)
        if not dump.get((row, col + 1), 0) == square:
            glRectf(x2, y1, x2 - w, y2)
        if not dump.get((row + 1, col), 0) == square:
            glRectf(x1, y2, x2, y2 + w)
        if not dump.get((row, col - 1), 0) == square:
            glRectf(x1, y1, x1 + w, y2)
            
        glColor4f(*(square + (0.5,)))
        glRectf(x1, y1, x2, y2)
            
        x += 1
        col += 1

def draw_block_queue(queue):
    glPushMatrix()
    glTranslatef(1.0, -0.5, 0.0)
    for block in queue:
        d_block = Block(block.shape, block.color)
        draw_block(d_block)
        glTranslatef(block.matrix.cols + 2, 0, 0)
    glPopMatrix()

def draw_border(color, width, height, thickness):
    glColor3f(*color)
    glLineWidth(thickness)
    glBegin(GL_LINE_LOOP)
    glVertex2f(0, 0)
    glVertex2f(width, 0)
    glVertex2f(width, height)
    glVertex2f(0, height)
    glEnd()
    
def draw_block_field(field):
    width = field.w
    height = field.h
    thickness = 3
    
    draw_border((1.0, 1.0, 0.0), width, height, thickness)
    draw_block_dump(field.dump)
    
    glPushMatrix()
    
    glTranslatef(0.0, field.h, 0.0)
    eqn = (c_double * 4)(0.0, -1.0, 0.0, 0.0)
    glClipPlane(GL_CLIP_PLANE0, eqn)
    glEnable(GL_CLIP_PLANE0)
    
    if field.block:
        glPushMatrix()
        glTranslatef(field.block.x, -field.block.y, 0)
        draw_block(field.block)
        glPopMatrix()
        
    glDisable(GL_CLIP_PLANE0)
    
    glTranslatef(width, 0.0, 0.0)
    
    max_block_size = 4
    num_blocks = len(field.queue)
    
    glScalef(0.7, 0.7, 1.0)
    glTranslatef(0, -max_block_size, 0)
    draw_border((1.0, 1.0, 0.0),
                (max_block_size + 2) * num_blocks, max_block_size, thickness)
    glTranslatef(0, max_block_size, 0)
    draw_block_queue(field.queue)
        
    glPopMatrix()
    
def draw_cursor_border(width, height, color):
    glTranslatef(0, -height/2, 0)
    draw_border(color, width, height, 2)
    
        