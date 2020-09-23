import threading

from modules.views import GameStartView, GameOverView, GameLevelView, SwitchLevelView


class ViewManager(object):
    _instance_lock = threading.Lock()
    _init_flag = False

    def __init__(self):
        self.__views = {
            'SwitchLevel': SwitchLevelView(),
            'GameOver': GameOverView(),
            'GameStart': GameStartView(),
            'GameLevelView': GameLevelView(),
        }

    def __new__(cls, *args, **kwargs):
        if not hasattr(ViewManager, "_instance"):
            with ViewManager._instance_lock:
                if not hasattr(ViewManager, "_instance"):
                    ViewManager._instance = object.__new__(cls)
        return ViewManager._instance

    def show(self, view):
        if view not in self.__views:
            raise Exception('View is not found!')
        else:
            self.__views[view].show()

