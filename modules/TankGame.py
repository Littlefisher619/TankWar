import pygame
import sys
import os
from interfaces import *
from GameLevel import GameLevel


class TankGame(object):

    def __init__(self, config):
        self.__screen = None
        self.__levels = None
        self.__sounds = {}
        self.__multiplayer_mode = False
        self.__config = config
        self.__is_win = False
        self.__quit_game_flag = False

    def getSounds(self):
        return self.__sounds

    def getScreen(self):
        return self.__screen

    def setQuitGameFlag(self, quit_game_flag):
        self.__quit_game_flag = quit_game_flag

    def getQuitGameFlag(self):
        return self.__quit_game_flag

    def getConfig(self):
        return self.__config

    def getLevel(self):
        return self.__level

    def getLevelFile(self):
        return self.__level_file

    def getIsWin(self):
        return self.__is_win

    def setIsWin(self, is_win):
        self.__is_win = is_win

    def setMultiplayerMode(self, multiplayer_mode):
        self.__multiplayer_mode = multiplayer_mode

    def getMultiPlayerMode(self):
        return self.__multiplayer_mode

    def __showInterface(self, interface):
        self.__interfaces[interface].show()

    def __init_game_window(self):
        config = self.getConfig()
        pygame.init()
        pygame.mixer.init()
        self.__screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption(config.TITLE)

    def __init_sounds(self):
        for sound, file in self.getConfig().AUDIO_PATHS.items():
            self.__sounds[sound] = pygame.mixer.Sound(file)
            self.__sounds[sound].set_volume(1)

    def __load_levels(self):
        self.__levels = [
            os.path.join(
                self.getConfig().LEVELFILEDIR,
                filename
            ) for filename in sorted(os.listdir(self.getConfig().LEVELFILEDIR))
        ]

    def __enter_loop(self):
        self.__showInterface('GameStart')
        while True:
            for level, level_file in enumerate(self.__levels):
                self.__level = level
                self.__showInterface('SwitchLevel')
                self.__level_file = level_file

                game_level = GameLevel(level + 1, level_file, self.__sounds, self.__multiplayer_mode, self.getConfig())

                self.__is_win = game_level.start(self.__screen)
                if not self.__is_win:
                    break

            self.__showInterface('GameOver')
            if self.getQuitGameFlag():
                break

    def __init_interfaces(self):
        self.__interfaces = {
            'SwitchLevel': SwitchLevelInterface(self),
            'GameOver': GameOverInterface(self),
            'GameStart': GameStartInterface(self)
        }

    def __init_game(self):
        self.__init_game_window()
        self.__init_sounds()
        self.__load_levels()

    def start(self):
        self.__init_game()
        self.__init_interfaces()
        self.__enter_loop()



