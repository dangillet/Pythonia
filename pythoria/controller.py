#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygcurse, pygame
from pygame.locals import *

from .hudview import HUDView
from .messageboxview import MessageBoxView
from .messagebox import MessageBox
from .gameview import GameView
from .dungeon import Dungeon
from .dungeonview import ScrollingView
from .player import Player
from .random_dungeon import DungeonGenerator

class DirectionForCommand():
    def __init__(self, controller, command):
        self.controller = controller
        self.dungeon = self.controller.dungeon
        self.player = self.dungeon.player
        self.command = command
    
    def process_event(self, event):
        "Process the events from the event loop"

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.controller.event_handler.pop()
            
        elif event.type == KEYDOWN and event.key == K_RIGHT:
            return self._execute_command(1, 0)
        elif event.type == KEYDOWN and event.key == K_LEFT:
            return self._execute_command(-1, 0)
        elif event.type == KEYDOWN and event.key == K_UP:
            return self._execute_command(0, -1)
        elif event.type == KEYDOWN and event.key == K_DOWN:
            return self._execute_command(0, 1)
    
    def _execute_command(self, dir_x, dir_y):
        """Execute the registered command in the given direction"""
        if not self.command(self.player.x + dir_x, self.player.y + dir_y):
            self.controller.msgbox.append("Vous ne pouvez pas faire cette action dans cette direction.")

        self.controller.event_handler.pop()

class GameEventHandler():
    """
    Normal Game event handler. Maps key press with commands given to the Dungeon.
    """
    def __init__(self, controller):
        self.controller = controller
        self.dungeon = self.controller.dungeon
    
    def process_event(self, event):
        "Process the events from the event loop"

        if event.type == KEYDOWN and event.key == K_RIGHT:
            self.dungeon.move_player(1, 0)
        elif event.type == KEYDOWN and event.key == K_LEFT:
            self.dungeon.move_player(-1, 0)
        elif event.type == KEYDOWN and event.key == K_UP:
            self.dungeon.move_player(0, -1)
        elif event.type == KEYDOWN and event.key == K_DOWN:
            self.dungeon.move_player(0, 1)
        elif event.type == KEYDOWN and event.key == K_o:
            self.controller.event_handler.append(DirectionForCommand(self.controller, self.dungeon.open_door))
            self.controller.msgbox.add("Donnez la direction de la porte à ouvrir. [ESC] pour annuler.")
        elif event.type == KEYDOWN and event.key == K_c:
            self.controller.event_handler.append(DirectionForCommand(self.controller, self.dungeon.close_door))
            self.controller.msgbox.add("Donnez la direction de la porte à fermer. [ESC] pour annuler.")


class Controller():
    """
    Game Controller.
    Its purpose is to make the Dungeon Model and the Dungeon View interact 
    together correctly.
    It responds to pygame events for user inputs (key presses). It delegates
    this task to an Event Handler. A stack of Event Handler can be created. 
    Only the top one (last in the list) will process the events.
    """
    def __init__(self, dungeon, msgbox, view):
        self.dungeon = dungeon
        self._connections = [dungeon.bind("Door Close", self.on_door_moves),
                             dungeon.bind("Door Open", self.on_door_moves)]
        self.player = self.dungeon.player
        self.msgbox = msgbox
        self.view = view
        self.event_handler = [GameEventHandler(self)]
        
    def process_event(self, event):
        """Process the events from the pygame events loop"""
        
        self.event_handler[-1].process_event(event)
    
    def on_door_moves(self):
        self.player.fov = self.dungeon.get_field_of_vision(self.player.x,
                                                           self.player.y,
                                                           5)
        self.dungeon.reveal(self.player.fov)
        
if __name__ == '__main__':
    """
    Quick game setup for testing purposes.
    """
    win = pygcurse.PygcurseWindow(80, 30)
    win.font = pygame.font.Font(pygame.font.match_font('consolas'), 18)
    level1 = Dungeon.generate(35, 20, 10)
    player = Player()
    level1.add_player(player)
    msgbox = MessageBox()

    view = GameView(
        win,
        {
            ScrollingView(level1):         (0  ,   0),
            HUDView(player):               (700,   0),
            MessageBoxView(msgbox, 80, 5): (0  , 460)
        }
    )

    controller = Controller(level1, msgbox,  view)
    win.autoupdate = False
    mainClock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                controller.process_event(event)

        controller.view.draw()
        win.blittowindow()
        mainClock.tick(30)

    pygame.quit()
    sys.exit()
