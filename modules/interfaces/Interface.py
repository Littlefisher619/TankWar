import pygame,sys


class Interface(object):
    def __init__(self, game_instance):
        self.__game_instance = game_instance
        self._init_resources()
        self._init_logo()

    def _init_game_window(self):
        self._getGameInstance().init_game_window()

    def _getGameInstance(self):
        return self.__game_instance

    def _getGameScreen(self):
        return self._getGameInstance().getScreen()

    def _getGameConfig(self):
        return self._getGameInstance().getConfig()

    def _init_resources(self):
        pass

    def _init_logo(self):
        pass

    def _init_text(self):
        pass

    def _init_bottons(self):
        pass

    def _draw_interface(self):
        pass

    def _main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self._draw_interface()
        pass

    def show(self):
        self._init_game_window()
        self._init_text()
        self._init_bottons()
        self._main_loop()
        pass

