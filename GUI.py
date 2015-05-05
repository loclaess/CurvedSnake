from tkinter import *
from tkinter.messagebox import showwarning
from tkinter.ttk import Combobox

from random import randint, random, choice
from math import pi

from Snake import *
from Bonus import *
from InputManager import *

class GUI:
    DEFAULT_WIDTH = 800        #pixels
    DEFAULT_HEIGHT = 800       #pixels
    DEFAULT_SPAWN_OFFSET = 60  #pixels
    DEFAULT_REFRESH_TIMER = 15 #ms
    BONUS_PROBABILITY = 0.01
    DEFAULT_NAME = 'GuestMooh'
    DEFAULT_COLORS = ['yellow', 'pink', 'red', 'blue', 'green', 'orange']
    DEFAULT_COMMANDS = [('Left', 'Right'),
                        ('s', 'd'),
                        ('o', 'p'),
                        ('b', 'n'),
                        ('1', '2'),
                        ('asterisk', 'minus')]
    
    MAXIMUM_NAME_LENGTH = 16 #chars
    
    BONUS_TIME = 300 #frames
    BONUS_SPRITES_DIMENSIONS = (32, 32) #pixels
    BONUS_DIRECTORY = './sprites/'
    BONUS_FILES = ['self_speedup.gif', 'self_speeddown.gif', 'thickness_down.gif',
                   'all_speeddown.gif', 'reversed_commands.gif', 'all_speedup.gif',
                   'right_angles.gif', 'thickness_up.gif', 'rotation_angle_down.gif',
                   'bonus_chance.gif', 'change_color.gif', 'change_chance_hole.gif',
                   'clean_map.gif', 'change_bg.gif', 'invincible.gif']
    def __init__(self):
        #window
        self.window = Tk()
        self.window_width = GUI.DEFAULT_WIDTH
        self.window_height = GUI.DEFAULT_HEIGHT
        self.mini_map = IntVar(value=2)
        self.one_vs_one = IntVar()
        self.window.geometry('{}x{}'.format(self.window_width, self.window_height))
        self.window.resizable(width=FALSE, height=FALSE)
        self.window.wm_title('Curved Snake')
        self.timer = GUI.DEFAULT_REFRESH_TIMER
        #GUI variables
        self.snakes_colors = []
        self.commands_list = []
        self.snakes_names = []
        self.regular_player = []
        self.regular_colors = []
        self.regular_commands = []
        self.random_colors_used = []
        self.random_commands_used = []
        self.left_key = self.right_key = False
        self.is_regular_list = False
        #other variables
        self.inputs = InputManager()
        self.current_loop = 0
        self.step = 0
        self.bonus_percent = 30
        self.bonus_proba = (GUI.BONUS_PROBABILITY/100)*self.bonus_percent
        self.events_queue = list()
        #init
        self.loadBonusImages()
        self.menuStart()
        self.window.mainloop()
    
    def loadBonusImages(self):
        '''
            loads all the images in GUI
        '''
        self.bonus_list = list()
        for file_name in GUI.BONUS_FILES:
            self.bonus_list.append(Bonus(GUI.BONUS_DIRECTORY + file_name))
        self.add_bonus_bool = [IntVar(value=1) for i in range(len(self.bonus_list))]
        
    def generateBonus(self):
        '''
            generates a random bonus and puts it on canvas
        '''
        xmin, ymin = GUI.BONUS_SPRITES_DIMENSIONS
        xmax, ymax = self.window_width-xmin, self.window_height-ymin
        x, y = self.findRandomFreePosition(xmin, xmax, ymin, ymax)
        bonus = choice(self.available_bonus)
        self.canvas.create_image(x, y, image=bonus.image,
                                 tags='bonus,{}'.format(bonus.name))
    
    def findRandomFreePosition(self, xmin, xmax, ymin, ymax):
        '''
            returns a (X, Y) coordinate on canvas
        '''
        return randint(xmin, xmax), randint(ymin, ymax) 
    
    def changeDirections(self):
        '''
            updates the snakes direction according to the pressed keys
        '''
        for i in range(len(self.commands_list)):
            left, right = self.commands_list[i]
            if self.inputs.isPressed(left):
                self.snakes[i].turn(TURN_LEFT)
            elif self.inputs.isPressed(right):
                self.snakes[i].turn(TURN_RIGHT)
    
    def refresh(self):
        '''
            refreshes the window every $self.timer seconds
        '''
        self.changeDirections()
        if len(self.events_queue) != 0:
            for event in self.events_queue:
                event[1] -= 1
            if self.events_queue[0][1] == 0:
                exec(self.events_queue[0][0])
                del self.events_queue[0]
        for snake in self.snakes_alive:
            if len(snake.events_queue) != 0:
                for event in snake.events_queue:
                    event[1] -= 1
                if snake.events_queue[0][1] == 0:
                    exec(snake.events_queue[0][0])
                    del snake.events_queue[0]
        if random() < self.bonus_proba:
            self.generateBonus()
        for snake in self.snakes_alive:
            snake.move(self.step)
            if not snake.getAlive():
                self.snakes_alive.remove(snake)
        if len(self.snakes_alive) <= 1:
            add_event = lambda l, f: l.append([f, 250])
            add_event(self.events_queue, 'self.newRound = True')
            self.text_before_round = True
        if self.text_before_round:
            self.canvas.create_text(self.window_height//2,
                                    self.window_width//2,
                                    text=self.snakes_alive[0].getName() +
                                    ' won this round!',
                                    fill='white')
        if self.newRound:
            return self.playNewRound()
        self.step += 1
        self.current_loop = self.window.after(self.timer, self.refresh)
        
    def playNewRound(self):
        self.clearWindow()
        self.play()
        
    def geometryMap(self):
        self.window.geometry('{}x{}'.format(self.window_width, self.window_height))
        self.window.resizable(width=FALSE, height=FALSE)
    
    def quitCurrentPlay(self):
        '''
            stops the current game and resets the start menu
        '''
        self.window.after_cancel(self.current_loop)
        self.random_colors_used = []
        self.random_commands_used = []
        self.window_height = GUI.DEFAULT_HEIGHT
        self.window_width = GUI.DEFAULT_WIDTH
        self.geometryMap()
        self.menuStart()
    
    def clearWindow(self):
        '''
            clears the whole content of the window
        '''
        for child in self.window.winfo_children():
            child.pack_forget()
    
    def menuStart(self):
        '''
            sets the whole GUI start menu
        '''
        self.clearWindow()
        Label(self.window, width=100, text='Curved Snake').pack()
        Label(self.window, width=250, text='New player').pack()
        self.current_name = StringVar()
        self.name = Entry(self.window, textvariable=self.current_name)
        self.name.bind('<Button-1>', self.removeFocus)
        self.name.pack()
        self.selectRandomName()
        Label(self.window, width=250, text='Already played ?').pack()
        self.player_known = Listbox(self.window, selectmode=SINGLE)
        self.player_known.insert(END, *self.regular_player)
        self.player_known.bind('<<ListboxSelect>>', self.showInfoPlayer)
        self.player_known.pack()
        self.button_left = Button(self.window, text=GUI.DEFAULT_COMMANDS[0][0],
                            bg='white', command=lambda:self.modifBgColor('L'))
        self.button_left.pack()
        self.button_right = Button(self.window, text=GUI.DEFAULT_COMMANDS[0][1],
                            bg='white', command=lambda:self.modifBgColor('R'))
        self.button_right.pack()
        self.selectRandomCommands()
        self.color = Combobox(self.window, state='readonly', exportselection=0)
        self.color['values'] = GUI.DEFAULT_COLORS
        self.selectRandomColor()
        self.color.bind('<<ComboboxSelected>>', self.newSelection)
        self.color.pack()
        Button(self.window, text='Add player', command=self.addPlayer).pack()
        Button(self.window, text='Remove player', command=self.removePlayer).pack()
        Label(self.window, width=250, text='Player ready to play').pack()
        self.player_ingame = Listbox(self.window, height=6, selectmode=SINGLE)
        self.player_ingame.bind('<<ListboxSelect>>', self.showInfoPlayer)
        self.player_ingame.insert(END, *self.regular_player)
        self.player_ingame.pack()
        Button(self.window, text='Parameters', command=self.parameters).pack()
        Button(self.window, text='Play!', command=self.playPressed).pack()
        
    def parameters(self):
        '''
            sets powerups and their probability
        '''
        self.top_bonus = Toplevel()
        self.top_bonus.grab_set()
        for i in range(len(self.bonus_list)):
            add_bonus = Checkbutton(self.top_bonus, image=self.bonus_list[i].image, variable=self.add_bonus_bool[i])
            y = i%3
            x = i//3
            add_bonus.grid(row=y, column=x)
        self.bonus_scale = Scale(self.top_bonus,
                                    label='probability',
                                    to=100,
                                    orient=HORIZONTAL)
        self.bonus_scale.set(self.bonus_percent)
        self.bonus_scale.grid(row=4, column=1)
        Radiobutton(self.top_bonus, text='normal', variable=self.mini_map, value=2).grid(row=5, column=1)
        Radiobutton(self.top_bonus, text='mini map', variable=self.mini_map, value=0).grid(row=5, column=2)
        Radiobutton(self.top_bonus, text='1v1', variable=self.mini_map, value=1).grid(row=5, column=0)
        Button(self.top_bonus, text='Set', command=self.closeAndGetVal).grid(row=6, column=1)
        
    def closeAndGetVal(self):
        self.bonus_percent = self.bonus_scale.get()
        self.bonus_proba = (GUI.BONUS_PROBABILITY/100)*self.bonus_percent
        self.top_bonus.destroy()
    
    def selectRandomColor(self):
        '''
            sets a random color in combobox for player
        '''
        availables = [color for color in GUI.DEFAULT_COLORS \
                                if color not in self.random_colors_used]
        if len(availables) > 0:
            self.color.set(choice(availables))
            self.current_color = self.color.get()
    
    def selectRandomCommands(self):
        '''
            sets the default commands for player
        '''
        commands = None
        i = 0
        while i < len(GUI.DEFAULT_COMMANDS) and commands is None:
            if GUI.DEFAULT_COMMANDS[i] not in self.random_commands_used:
                commands = GUI.DEFAULT_COMMANDS[i]
                left_button, right_button = commands
                self.button_left.configure(text=left_button)
                self.move_command_left = left_button
                self.button_right.configure(text=right_button)
                self.move_command_right = right_button
            i += 1
    
    def selectRandomName(self):
        '''
            creates a random name for next player
        '''
        self.current_name.set('{}{}'.format(GUI.DEFAULT_NAME,
                              '' if len(self.snakes_names) == 0 \
                                 else '_' + str(randint(0, 666))))
    
    def removePlayer(self):
        '''
            callback fucntion when 'remove player' button is pressed: removes
            selection from current lists
        '''
        if len(self.player_ingame.curselection()) > 0:
            self.player_ingame.delete(self.selected[0])
            try:
                del self.snakes_names[self.selected[0]]
                del self.snakes_colors[self.selected[0]]
                del self.commands_list[self.selected[0]]
            except:
                showwarning('No one to remove', 'You have no one to remove')
        else:
            showwarning('No one chosen', 'Choose a player to remove')
    
    def addPlayer(self):
        '''
            callback function when 'add player' button is pressed: saves
            config to create a new character for the following play.
        '''
        if len(self.player_known.curselection()) > 0:
            if self.regular_player[self.id] in self.snakes_names:
                showwarning('Added player', 'This player is already going to play!')
                return
            if self.regular_colors[self.id] in self.snakes_colors:
                showwarning('Color', 'The color chosen is already taken')
                return
            if [commands for commands in self.commands_list \
                                if self.move_command_left in commands or \
                                   self.move_command_right in commands] != []:
                showwarning('Commands', 'Another player has already those commands')
                return
            self.snakes_colors.append(self.regular_colors[self.id])
            self.commands_list.append(self.regular_commands[self.id])
            self.snakes_names.append(self.regular_player[self.id])
            self.player_ingame.insert(END, self.regular_player[self.id])
            self.random_colors_used.append(self.regular_colors[self.id])
            self.random_commands_used.append(self.regular_commands[self.id])
        else:
            if self.current_name.get() in self.snakes_names:
                showwarning('Added player', 'This player is already going to play!')
                return
            if len(self.current_name.get()) > GUI.MAXIMUM_NAME_LENGTH:
                showwarning('Name player', 'Your name is too long. Pick a new one')
                return
            if self.current_name.get() in self.regular_player:
                showwarning('Name player', 'This name is already taken')
                return
            if self.current_color in self.snakes_colors:
                showwarning('Color', 'The color chosen is already taken')
                return
            if [commands for commands in self.commands_list \
                                if self.move_command_left in commands or \
                                   self.move_command_right in commands] != []:
                showwarning('Commands', 'Another player has already those commands')
                return
            self.snakes_names.append(self.current_name.get())
            self.player_ingame.insert(END, self.current_name.get())
            self.snakes_colors.append(self.current_color)
            self.commands_list.append([self.move_command_left, self.move_command_right])
            self.random_colors_used.append(self.current_color)
            self.random_commands_used.append((self.move_command_left, self.move_command_right))
            self.selectRandomCommands()
            self.selectRandomColor()
            self.selectRandomName()
    
    def playPressed(self):
        '''
            callback function when play button is pressed
        '''
        self.clearWindow()
        for i in range(len(self.snakes_names)):
            if self.snakes_names[i] not in self.regular_player:
                self.regular_player.append(self.snakes_names[i])
                self.regular_colors.append(self.snakes_colors[i])
                self.regular_commands.append(self.commands_list[i])
        self.available_bonus = [self.bonus_list[i] for i in range(len(self.bonus_list)) if self.add_bonus_bool[i].get() == 1]
        if self.mini_map.get() == 0:
            self.window_height -= 150
            self.window_width -= 150
            self.geometryMap()
        elif self.mini_map.get() == 1:
            self.window_height -= 300
            self.window_width -= 300
            self.geometryMap()
        self.window.after(1000, self.play)
    
    def modifBgColor(self, side):
        '''
            Changes button background color when clicked so user knows when
            he can press a key to set his preferences
        '''
        self.window.focus()
        if side == 'L':
            self.button_left.configure(bg='red')
            self.left_key = True
        else:
            self.button_right.configure(bg='red')
            self.right_key = True
        self.window.bind('<Key>', self.setCommand)
    
    def play(self):
        '''
            prepares the game
        '''
        self.canvas = Canvas(self.window, bg='black', highlightthickness=0)
        self.canvas.pack(expand=1, fill='both')
        xmin = ymin = GUI.DEFAULT_SPAWN_OFFSET
        xmax, ymax = self.window_width, self.window_height
        self.snakes = list()
        self.newRound = False
        self.text_before_round = False
        for i in range(len(self.snakes_names)):
            self.snakes.append(Snake(self,
                                     self.snakes_names[i],
                                     randint(xmin, xmax-xmin),
                                     randint(ymin, ymax-ymin),
                                     random()*2*pi,
                                     self.snakes_colors[i]))
        self.snakes_alive = self.snakes[:]
        self.startInvincible()
        #add create_text with command of each player 
        self.refresh()
        self.canvas.focus_set()
        self.canvas.bind('<Key>', self.keyPressed)
        self.canvas.bind('<KeyRelease>', lambda e: self.inputs.release(e.keysym))
        
    def startInvincible(self):
        players = list()
        for snake in self.snakes:
            players.append(snake)
        add_event = lambda l, f: l.append([f, 150])
        for snake in players:
            add_event(snake.events_queue, 'snake.time_before_start = False')
    
    def handleBonus(self, sender_name, bonus_type):
        '''
            sets bonus and handles events queues
        '''
        sender = None
        others = list()
        for snake in self.snakes:
            if snake.name == sender_name:
                sender = snake
            else:
                others.append(snake)
        add_event = lambda l, f: l.append([f, GUI.BONUS_TIME])
        if bonus_type == 'self_speedup':
            sender.speed += 1
            add_event(sender.events_queue, 'snake.speed -= 1')
        elif bonus_type == 'all_speedup':
            for snake in others:
                snake.speed += 1
                add_event(snake.events_queue, 'snake.speed -= 1')
        elif bonus_type == 'self_speeddown':
            add_event = lambda l, f: l.append([f, 600])
            if sender.speed > 1:
                sender.speed /= 1.5
                add_event(sender.events_queue,'snake.speed *= 1.5')
        elif bonus_type == 'all_speeddown':
            add_event = lambda l, f: l.append([f, 250])
            for snake in others:
                if snake.speed > 1:
                    snake.speed /= 1.5
                    add_event(snake.events_queue, 'snake.speed *= 1.5')
        elif bonus_type == 'reversed_commands':
            for snake in others:
                snake.inversed_commands = True
                add_event(snake.events_queue, 'snake.inversed_commands = False')
        elif bonus_type == 'right_angles':
            for snake in others:
                snake.previous_angles.append(snake.rotating_angle)
                snake.rotating_angle = pi/2
                add_event(snake.events_queue, 'snake.restoreAngle()')
        elif bonus_type == 'thickness_up':
            for snake in others:
                snake.thickness += DEFAULT_THICKNESS
                add_event(snake.events_queue, 'snake.thickness -= DEFAULT_THICKNESS')
        elif bonus_type == 'thickness_down':
            sender.thickness /= 2
            add_event(sender.events_queue, 'snake.thickness *= 2')
        elif bonus_type == 'bonus_chance':
            add_event = lambda l, f: l.append([f, 50])
            self.bonus_proba *= 4
            add_event(self.events_queue, 'self.bonus_proba /= 4')
        elif bonus_type == 'rotation_angle_down':
            for snake in others:
                snake.rotating_angle /= 2
                add_event(snake.events_queue, 'snake.rotating_angle *= 2')
        elif bonus_type == 'change_color':
            for snake in others:
                snake.color = sender.color
                add_event(snake.events_queue, 'snake.color = snake.color_unchanged')
        elif bonus_type == 'change_chance_hole':
            add_event = lambda l, f: l.append([f, 750])
            for snake in others:
                snake.hole_probability *= 10
                add_event(snake.events_queue, 'snake.hole_probability /= 10')
        elif bonus_type == 'invincible':
            sender.invincible = True
            add_event(sender.events_queue, 'snake.invincible = False')
        elif bonus_type == 'clean_map':
            self.canvas.delete(ALL)
        elif bonus_type == 'change_bg':
            self.canvas.configure(bg='white')
            add_event(self.events_queue, 'self.canvas.configure(bg="black")')
        # time_bonus_left = GUI.BONUS_TIME
        # angle = (time_bonus_left/GUI.BONUS_TIME)*360
        # if sender == snake:
            # head = sender.coords()
            # head.create_arc(head, style = ARC, extent=angle, width = 2, oultine='white')
        # time_bonus_left -= 1
        
    #callbacks
    
    def setCommand(self, e):
        '''
            callback function when new command (left/right) is chosen
        '''
        if self.left_key:
            if len(self.player_ingame.curselection()) > 0 or \
               len(self.player_known.curselection()) > 0:
                if self.is_regular_list:
                    self.regular_commands[self.id][0] = e.keysym
                else:
                    self.commands_list[self.id][0] = e.keysym
            self.move_command_left = e.keysym
            self.button_left.configure(text=self.move_command_left)
            self.button_left.configure(bg='white')
        elif self.right_key:
            if self.is_regular_list:
                self.regular_commands[self.id][1] = e.keysym
            if len(self.player_ingame.curselection()) > 0:
                self.commands_list[self.id][1] = e.keysym
            self.move_command_right = e.keysym
            self.button_right.configure(text=self.move_command_right)
            self.button_right.configure(bg='white')
        self.left_key = False
        self.right_key = False
        self.window.unbind('<Key>')
    
    def newSelection(self, e):
        '''
            callback function when combobox selection changes
        '''
        if len(self.player_ingame.curselection()) > 0:
            self.snakes_colors[self.id] = self.color.get().lower()
        elif len(self.player_known.curselection()) > 0:
            self.regular_colors[self.id] = self.color.get().lower()
        self.current_color = self.color.get().lower()
        self.color.selection_clear()
        
    def showInfoPlayer(self, e):
        '''
            resets informations about selected user
        '''
        if len(self.player_known.curselection()) > 0:
            self.is_regular_list = True
        elif len(self.player_ingame.curselection()) > 0:
            self.is_regular_list = False
        self.selected = list(map(int, e.widget.curselection()))
        if self.selected:
            self.colors_list = list(self.color.cget('values'))
            if self.is_regular_list:
                self.id = self.regular_player.index(e.widget.get(self.selected[0]))
                self.button_left.configure(text=self.regular_commands[self.id][0])
                self.button_right.configure(text=self.regular_commands[self.id][1])
                self.color.current(self.colors_list.index(self.regular_colors[self.id]))
                self.move_command_left = self.regular_commands[self.id][0]
                self.move_command_right = self.regular_commands[self.id][1]
            else:
                self.id = self.snakes_names.index(e.widget.get(self.selected[0]))
                self.button_left.configure(text=self.commands_list[self.id][0])
                self.button_right.configure(text=self.commands_list[self.id][1])
                self.color.current(self.colors_list.index(self.snakes_colors[self.id]))
    
    def removeFocus(self, e):
        '''
            clears selection from listboxes
        '''
        self.player_ingame.selection_clear(0,END)
        self.player_known.selection_clear(0,END)
    
    def keyPressed(self, e):
        '''
            callback function when any key is pressed in canvas
        '''
        key = e.keysym
        if key.lower() == 'q':
            self.quitCurrentPlay()
        else:
            self.inputs.press(key)
            #move the correct player(s) when key is pressed
            
    
    
if __name__ == '__main__':
    GUI()
