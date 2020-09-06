import pygame


class Home(pygame.sprite.Sprite):
	# 大本营
	def __init__(self, position, imagefile, **kwargs):
		pygame.sprite.Sprite.__init__(self)
		self.imagefile = imagefile
		self.image = pygame.image.load(self.imagefile[0])
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = position
		self.__destroyed = False

	@property
	def destroyed(self):
		return self.__destroyed

	@destroyed.setter
	def destroyed(self, destroyed):
		self.__destroyed = destroyed
		if destroyed:
			self.image = pygame.image.load(self.imagefile[1])

	def draw(self, screen):
		screen.blit(self.image, self.rect)