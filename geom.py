#!/usr/bin/env python

class Matrix:
    CW = -1
    CCW = 1
    
    def __init__(self, rows, cols):
        self.rows = max(abs(rows), 1)
        self.cols = max(abs(cols), 1)
        self.size = (self.rows, self.cols)
        self.els = [0] * (self.rows * self.cols)
    
    def rotate(self, drc):
        res = Matrix(self.cols, self.rows)
        
        if drc == Matrix.CW:
            iter_rows = xrange(self.rows - 1, -1, -1)
            iter_cols = xrange(self.cols)
        else:
            iter_rows = xrange(self.rows)
            iter_cols = xrange(self.cols - 1, -1, -1)
        
        i = 0
        for r in iter_rows:
            for c in iter_cols:
                res[c, r] = self.els[i]
                i += 1
        
        return res
        
    def get(self, key, default):
        try:
            return self.__getitem__(key)
        except:
            return default
    
    def __getitem__(self, key):
        row, col = key
        if row < 0 or col < 0:
            raise IndexError('No negative indices!')
        elif row >= self.rows or col >= self.cols:
            raise IndexError('Indices too big!')
        return self.els[self.cols * row + col]
    
    def __setitem__(self, key, value):
        row, col = key
        self.els[self.cols * row + col] = value
        
    def __iter__(self):
        return self.els.__iter__()
        
    def __str__(self):
        res = ''
        for r in range(self.rows):
            res += '['
            for c in range(self.cols):
                if c == self.cols - 1:
                    res += str(self[r, c])
                else:
                    res += str(self[r, c]).ljust(5)
            res += ']\n'
        return res

class BlockDump(Matrix):
    NO_COL = 0
    SIDE_COL = 1
    BLOCK_COL = 2
    BOTTOM_COL = 4
    
    def __init__(self, w, h):
        Matrix.__init__(self, h, w)
    
    def add_block(self, block):
        for square in block:
            r = block.y + square[1]
            c = block.x + square[0]
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self[r, c] = block.color
                
    def collision(self, block):
        res = BlockDump.NO_COL
        
        if block.x < 0 or block.x + block.matrix.cols - 1 >= self.cols:
            res |= BlockDump.SIDE_COL
        if block.y + block.matrix.rows - 1 >= self.rows:
            res |= BlockDump.BOTTOM_COL
            
        for square in block:
            r = block.y + square[1]
            c = block.x + square[0]
            if 0 <= r < self.rows and 0 <= c < self.cols and self[r, c] != 0:
                res |= BlockDump.BLOCK_COL
                break
                
        return res
    
    def remove_line(self, line):
        for r in range(line, -1, -1):
            all_empty = True
            for c in range(self.cols):
                if r == 0:
                    self[r, c] = 0
                else:
                    all_empty = False
                    self[r, c] = self[r - 1, c]
            if all_empty:
                break
                
    def remove_filled_lines(self):
        lines = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self[r, c] == 0:
                    break
            else:
                self.remove_line(r)
                lines += 1
        return lines
        
class Shape:
    def __init__(self, template):
        self.rotations = [template]
        for i in range(3):
            self.rotations.append(self.rotations[i].rotate(Matrix.CW))
        
class Block:
    LEFT = -1
    RIGHT = 1
    
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.matrix = self.shape.rotations[self.rotation]
        
    def rotate(self, drc):
        self.rotation = (self.rotation + drc) % len(self.shape.rotations)
        old_matrix = self.matrix
        self.matrix = self.shape.rotations[self.rotation]
        
    def __getitem__(self, key):
        return self.matrix[key]
        
    def __iter__(self):
        return BlockIterator(self.matrix)
    
    def clone(self):
        block = Block(self.shape, self.color)
        block.x = self.x
        block.y = self.y
        block.rotation = self.rotation
        block.matrix = self.matrix
        return block
        
class BlockIterator:
    def __init__(self, matrix):
        self.els_iter = iter(matrix.els)
        self.cols = matrix.cols
        self.position = 0
        
    def next(self):
        while self.els_iter.next() == 0:
            self.position += 1
        coord = (self.position % self.cols, self.position / self.cols)
        self.position += 1
        return coord
        
    def __iter__(self):
        return self


