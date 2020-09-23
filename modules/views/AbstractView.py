import pygame,sys

from modules.TankGame import TankGame


class AbstractView(object):
    def __init__(self):
        self._init_resources()
        self._init_logo()

    @property
    def config(self):
        return TankGame().config

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
        TankGame().init_game_window()
        self._init_text()
        self._init_bottons()
        self._main_loop()
        pass

