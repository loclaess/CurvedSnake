from tkinter import *
from math import cos, sin
from random import random, randint

DEFAULT_SPEED = 2
DEFAULT_THICKNESS = 4
DEFAULT_CHANCE_HOLE = 0.02
DEFAULT_MAX_HOLE_LENGTH = 20
DEFAULT_MIN_HOLE_LENGTH = 5

class Snake:
    def __init__(self, parent, name, x_head, y_head, angle, color,
                            moveCommandL, moveCommandR,
                            hole_proba=DEFAULT_CHANCE_HOLE,
                            max_hole_length=DEFAULT_MAX_HOLE_LENGTH,
                            min_hole_length=DEFAULT_MIN_HOLE_LENGTH,
                            speed=DEFAULT_SPEED, thickness=DEFAULT_THICKNESS):
        #list and not tuple because tuples can't be modified
        self.head_coord = [x_head, y_head]
        self.speed = speed
        self.angle = angle #radians!
        self.canvas = parent.canvas
        self.parent = parent
        self.thickness = thickness
        self.color = color
        self.alive = True
        self.name = str(name)
        self.hole = 0
        self.hole_probability = hole_proba
        self.max_hole_length = max_hole_length
        self.min_hole_length = min_hole_length
        r = self.thickness//2
        self.moveCommandL = moveCommandL
        self.moveCommandR = moveCommandR
        self.head_id = self.canvas.create_oval(x_head-r, y_head-r, x_head+r, y_head+r,
                                        fill=self.color, outline=self.color,
                                        tag='snake,{},{}'.format(self.name, -1))
        self.events_queue = list()
    
    def isInScreen(self, x, y):
        self.canvas.update()
        return 0 <= x < self.canvas.winfo_width() and \
               0 <= y < self.canvas.winfo_height()
    
    def handleCollision(self, step, collisions):
        first_elem = int(collisions[0])
        tags = self.canvas.gettags(first_elem)
        if len(tags) != 0:
            info = tags[0].split(',')
            if info[0] == 'snake':
                self.alive = int(info[2]) >= step-self.thickness*3
                if not self.alive:
                    print('dead')
            elif info[0] == 'bonus':
                self.canvas.delete(first_elem)
                self.parent.handleBonus(self.name, info[1])
    
    def handleMove(self, step):
        x, y = self.head_coord
        #if there is contact, snake is dead
        #WARNING: when the snake moves, it always touches its previous position
        #so step of appearance is written as a tag.
        if not self.isInScreen(x, y):
            self.alive = False
        else:
            r = self.thickness // 2
            #find all items in contact with new position
            collisions = self.canvas.find_overlapping(x-r, y-r, x+r, y+r)
            if len(collisions) != 0 and collisions[0] == self.head_id:
                collisions = collisions[1:]
            #if there is something
            if len(collisions) != 0:
                self.handleCollision(step, collisions)
    
    def move(self, step):
        #stop moving if snake is dead
        if not self.alive:
            return
        #step is used to handle collisions
        if not isinstance(step, int):
            #if it is under form 'after#<step>', remove 'after#'
            step = int(step[step.find('#')+1:])
        #find new coordinates
        x, y = self.head_coord
        x += self.speed * cos(self.angle)
        y += self.speed * sin(self.angle)
        #update head_coord
        self.head_coord = [x, y]
        #radius of oval
        r = self.thickness // 2
        self.handleMove(step)
        
        if self.hole == 0:
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.color,
                                        outline=self.color,
                                        tag='snake,{},{}'.format(self.name, step))
            if random() < self.hole_probability:
                self.hole = randint(self.min_hole_length, self.max_hole_length)
        else:
            self.hole -= 1
        self.canvas.coords(self.head_id, x-r, y-r, x+r, y+r)
    
    def getMoveCommandL(self):
        return self.moveCommandL
        
    def getMoveCommandR(self):
        return self.moveCommandR
    #
