import pygame
import random
from .scenes import SceneElement


class Foods(SceneElement):
	BOOM = 'boom'
	IRON = 'iron'
	CLOCK = 'clock'
	GUN = 'gun'
	TANK = 'tank'
	PROTECT = 'protect'
	STAR = 'star'

	# 食物类. 用于获得奖励
	def __init__(self, food_image_paths, screensize):
		random_position = (random.randint(100, screensize[0]-100), random.randint(100, screensize[1]-100))
		random_food = random.choice(list(food_image_paths.keys()))
		self.__name = random_food
		super().__init__(random_position, food_image_paths.get(self.__name))

		self.exist_time = 1000

	@property
	def type(self):
		return self.__name

	def update(self):
		self.exist_time -= 1
		return True if self.exist_time < 0 else False