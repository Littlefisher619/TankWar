import pygame
import sys
import os
from .interfaces import *
from .GameLevel import GameLevel


class TankGame(object):

    def __init__(self, config):
        self.__screen = None
        self.__levels = None
        self.__sounds = {}
        self.__multiplayer_mode = False
        self.__config = config
        self.__is_win = False
        self.__quit_game_flag = False

    @property
    def sounds(self):
        return self.__sounds

    @property
    def screen(self):
        return self.__screen

    @property
    def quit_game_flag(self):
        return self.__quit_game_flag

    @quit_game_flag.setter
    def quit_game_flag(self, quit_game_flag):
        self.__quit_game_flag = quit_game_flag

    @property
    def config(self):
        return self.__config

    @property
    def level(self):
        return self.__level

    @property
    def level_file(self):
        return self.__levels[self.__level]

    @property
    def is_win(self):
        return self.__is_win

    @is_win.setter
    def is_win(self, is_win):
        self.__is_win = is_win

    @property
    def multiplayer_mode(self):
        return self.__multiplayer_mode

    @multiplayer_mode.setter
    def multiplayer_mode(self, multiplayer_mode):
        self.__multiplayer_mode = multiplayer_mode

    def __show_interface(self, interface):
        self.__interfaces[interface].show()

    def init_game_window(self, size_tuple=None):
        if size_tuple is None:
            self.__screen = pygame.display.set_mode(
                (self.config.WIDTH, self.config.HEIGHT)
            )
        else:
            self.__screen = pygame.display.set_mode(size_tuple)

    def __init_sounds(self):
        for sound, file in self.config.AUDIO_PATHS.items():
            self.__sounds[sound] = pygame.mixer.Sound(file)
            self.__sounds[sound].set_volume(1)

    def __load_levels(self):
        self.__levels = [
            os.path.join(
                self.config.LEVELFILEDIR,
                filename
            ) for filename in sorted(os.listdir(self.config.LEVELFILEDIR))
        ]

    def __enter_loop(self):
        self.__show_interface('GameStart')
        while True:
            for level in range(len(self.__levels)):
                self.__level = level
                self.__show_interface('SwitchLevel')
                self.__show_interface('GameLevel')
                if not self.is_win:
                    break

            self.__show_interface('GameOver')
            if self.quit_game_flag:
                break

    def __init_interfaces(self):
        self.__interfaces = {
            'SwitchLevel': SwitchLevelInterface(self),
            'GameOver': GameOverInterface(self),
            'GameStart': GameStartInterface(self),
            'GameLevel': GameLevel(self),
        }

    def __init_game(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.config.TITLE)
        self.init_game_window()
        self.__init_sounds()
        self.__load_levels()

    def start(self):
        self.__init_game()
        self.__init_interfaces()
        self.__enter_loop()



