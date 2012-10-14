from geom import *
import random

BLOCKS = []

B = Matrix(1, 4)
B[0, 0] = B[0, 1] = B[0, 2] = B[0, 3] = 1 # I block
BLOCKS.append(Shape(B))

B = Matrix(3, 2)
B[0, 1] = B[1, 1] = B[2, 1] = B[2, 0] = 1 # J block
BLOCKS.append(Shape(B))

B = Matrix(3, 2)
B[0, 0] = B[1, 0] = B[2, 0] = B[2, 1] = 1 # L block
BLOCKS.append(Shape(B))

B = Matrix(2, 3)
B[0, 0] = B[0, 1] = B[1, 1] = B[1, 2] = 1 # Z block
BLOCKS.append(Shape(B))

B = Matrix(2, 3)
B[1, 0] = B[1, 1] = B[0, 1] = B[0, 2] = 1 # S block
BLOCKS.append(Shape(B))

B = Matrix(2, 3)
B[1, 0] = B[1, 1] = B[1, 2] = B[0, 1] = 1 # T block
BLOCKS.append(Shape(B))

B = Matrix(2, 2)
B[0, 0] = B[0, 1] = B[1, 0] = B[1, 1] = 1 # O block
BLOCKS.append(Shape(B))

COLORS = [
    (0.0, 0.75, 1.0),
    (0.9, 0.5, 0.0),
    (0.3, 1.0, 0.3),
    (0.75, 0.0, 0.0),
    (0.9, 0.9, 0.0),
    (0.75, 0.0, 1.0),
    (0.0, 0.0, 0.75),
]

class BlockField:
    LEFT = -1
    RIGHT = 1
    
    QUEUE_LEN = 4
    
    MIN_SPEED = 5
    MAX_SPEED = 20
    SPEED_STEP = 1
    LEVEL_INTERVAL = 10
    
    PLAY = 0
    OVER = 1
    
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.dump = BlockDump(w, h)
        self.block = None
        self.queue = []
        while len(self.queue) < self.QUEUE_LEN:
            self.queue_new_block()
        self.get_new_block()
        
        self.lines = 0
        self.level = 1
        self.next_level = self.LEVEL_INTERVAL
        self.points = 0
        self.state = self.PLAY
        
        self.last_update = 0
        self.speed = self.MIN_SPEED
        
    def update(self, dt):
        if self.state == self.OVER:
            return
        
        self.last_update += dt
        if self.last_update > 1.0 / self.speed:
            self.last_update -= 1.0 / self.speed
            self.fall()
            if self.lines >= self.next_level:
                self.level += 1
                self.speed = min(self.speed + self.SPEED_STEP, self.MAX_SPEED)
                self.next_level += self.LEVEL_INTERVAL
        
    def queue_new_block(self):
        choice = random.randrange(len(BLOCKS))
        block = Block(BLOCKS[choice], COLORS[choice])
        self.queue.append(block)
        
    def get_new_block(self):
        self.block = self.queue.pop(0)
        self.block.x = self.dump.cols / 2 - self.block.matrix.cols / 2
        self.block.y = -self.block.matrix.rows
        self.queue_new_block()
    
    def move(self, drc):
        self.block.x += drc
        collision = self.dump.collision(self.block)
        if collision != BlockDump.NO_COL:
            self.block.x -= drc
    
    def rotate(self, drc):
        block = self.block.clone()
        block.rotate(drc)
        collision = self.dump.collision(block)
        
        if collision == BlockDump.SIDE_COL | BlockDump.BLOCK_COL:
            return
        elif collision & BlockDump.SIDE_COL:
            block.x = self.dump.cols - block.matrix.cols
            if not self.dump.collision(block):
                self.block = block
        elif collision & BlockDump.BLOCK_COL:
            block.x += 1
            if self.dump.collision(block) == BlockDump.NO_COL:
                self.block = block
                return
            block.x -= 2
            if self.dump.collision(block) == BlockDump.NO_COL:
                self.block = block
                return
        elif collision & BlockDump.BOTTOM_COL:
            block.y = self.dump.rows - block.matrix.rows
            if not self.dump.collision(block):
                self.block = block
        else:
            self.block = block
    
    def fall(self):
        self.block.y += 1
        collision = self.dump.collision(self.block)
        if collision & (BlockDump.BLOCK_COL | BlockDump.BOTTOM_COL):
            self.block.y -= 1
            self.dump.add_block(self.block)
            if self.block.y < 0:
                self.state = self.OVER
            new_lines = self.dump.remove_filled_lines()
            self.lines += new_lines
            self.points += self.level * new_lines**2
            self.get_new_block()
            
    def drop(self):
        cur_block = self.block
        points = 0
        while self.block == cur_block:
            self.fall()
            points += 1
        self.points += points / (self.h / 3)
        
