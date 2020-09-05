import config
from modules.TankGame import TankGame

game_instance = None

if __name__ == '__main__':
	game_instance = TankGame(config)
	game_instance.start()
