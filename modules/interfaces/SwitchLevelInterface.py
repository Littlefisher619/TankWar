import sys
import pygame

from .Interface import Interface


class SwitchLevelInterface(Interface):

	def _init_resources(self):
		config = self._getGameConfig()
		self.__loadbar = pygame.image.load(config.OTHER_IMAGE_PATHS.get('__loadbar')).convert_alpha()
		self.__background_img = pygame.image.load(config.OTHER_IMAGE_PATHS.get('background'))
		self.__logo_img = pygame.image.load(config.OTHER_IMAGE_PATHS.get('logo'))
		self.__logo_img = pygame.transform.scale(self.__logo_img, (446, 70))
		self.__font = pygame.font.Font(config.FONTPATH, config.WIDTH // 20)
		self.__tank_cursor_img = pygame.image.load(
			config.ENEMY_TANK_IMAGE_PATHS.get('1')[0]
		).convert_alpha().subsurface((0, 144), (48, 48))

	def _init_text(self):
		config = self._getGameConfig()
		self.__font_render = self.__font.render(
			'LEVEL%d' % (self._getGameInstance().getLevel() + 1),
			True,
			(255, 255, 255) # White
		)
		self.__font_rect = self.__font_render.get_rect()
		self.__font_rect.centerx, self.__font_rect.centery = config.WIDTH / 2, config.HEIGHT / 2

	def _init_loadbar(self):
		config = self._getGameConfig()
		self.__loadbar_rect = self.__loadbar.get_rect()
		self.__loadbar_rect.centerx, self.__loadbar_rect.centery = config.WIDTH / 2, config.HEIGHT / 1.4
		self.__tank_rect = self.__tank_cursor_img.get_rect()
		self.__tank_rect.left = self.__loadbar_rect.left
		self.__tank_rect.centery = self.__loadbar_rect.centery

	def _init_logo(self):
		self.__logo_rect = self.__logo_img.get_rect()
		self.__logo_rect.centerx, self.__logo_rect.centery = self._getGameConfig().WIDTH / 2, self._getGameConfig().HEIGHT // 4

	def _draw_interface(self):
		screen = self._getGameScreen()
		screen.blit(self.__background_img, (0, 0))
		screen.blit(self.__logo_img, self.__logo_rect)
		screen.blit(self.__font_render, self.__font_rect)
		screen.blit(self.__loadbar, self.__loadbar_rect)
		screen.blit(self.__tank_cursor_img, self.__tank_rect)
		pygame.draw.rect(
			screen,
			(192, 192, 192),  # Gray
			(
				self.__loadbar_rect.left + 8,
				self.__loadbar_rect.top + 8,
				self.__tank_rect.left - self.__loadbar_rect.left - 8,
				self.__tank_rect.bottom - self.__loadbar_rect.top - 16
			)
		)
		self.__tank_rect.left += 8

	def _main_loop(self):
		load_time_left = self.__loadbar_rect.right - self.__tank_rect.right + 8
		clock = pygame.time.Clock()

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			if load_time_left <= 0:
				return
			self._draw_interface()
			load_time_left -= 8
			pygame.display.update()
			clock.tick(60)

	def show(self):
		self._init_loadbar()
		super().show()
