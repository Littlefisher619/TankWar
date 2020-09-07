import pygame
from .scenes import SceneElement


class Home(SceneElement):
	# 大本营
	def __init__(self, position, imagefile, walls_position):
		super().__init__(position, imagefile[0])
		self.__destroyed_image = imagefile[1]
		self.__destroyed = False
		self.walls_position = walls_position


	@property
	def destroyed(self):
		return self.__destroyed

	@destroyed.setter
	def destroyed(self, destroyed):
		self.__destroyed = destroyed
		if destroyed:
			self.image = pygame.image.load(self.__destroyed_image)

	def draw(self, screen):
		screen.blit(self.image, self.rect)