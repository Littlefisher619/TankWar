
import sys
import pygame

from .Interface import Interface

class GameStartInterface(Interface):

	def _init_resources(self):
		config = self._getGameConfig()
		self.__background_img = pygame.image.load(config.OTHER_IMAGE_PATHS.get('background'))
		self.__font = pygame.font.Font(config.FONTPATH, config.WIDTH // 12)
		self.__logo_img = pygame.image.load(config.OTHER_IMAGE_PATHS.get('logo'))
		self.__logo_img = pygame.transform.scale(self.__logo_img, (446, 70))
		self.__tank_cursor = pygame.image.load(
			config.PLAYER_TANK_IMAGE_PATHS.get('player1')[0]
		).convert_alpha().subsurface((0, 144), (48, 48))

	def _init_logo(self):
		self.__logo_rect = self.__logo_img.get_rect()
		self.__logo_rect.centerx, self.__logo_rect.centery = self._getGameConfig().WIDTH / 2, self._getGameConfig().HEIGHT // 4

	def _init_text(self):
		color_white = (255, 255, 255)
		color_red = (255, 0, 0)
		config = self._getGameConfig()
		self.__player_render_white = self.__font.render('1 PLAYER', True, color_white)
		self.__player_render_red = self.__font.render('1 PLAYER', True, color_red)
		self.__players_render_white = self.__font.render('2 PLAYERS', True, color_white)
		self.__players_render_red = self.__font.render('2 PLAYERS', True, color_red)
		self.__game_tip = self.__font.render('press <Enter> to start', True, color_white)
		self.__game_tip_rect = self.__game_tip.get_rect()
		self.__game_tip_rect.centerx, self.__game_tip_rect.top = config.WIDTH / 2, config.HEIGHT / 1.4

	def _init_bottons(self):
		config = self._getGameConfig()
		self.__player_rect = self.__player_render_white.get_rect()
		self.__player_rect.left, self.__player_rect.top = config.WIDTH / 2.8, config.HEIGHT / 2.5
		self.__players_rect = self.__players_render_white.get_rect()
		self.__players_rect.left, self.__players_rect.top = config.WIDTH / 2.8, config.HEIGHT / 2
		self.__tank_rect = self.__tank_cursor.get_rect()

	def _draw_interface(self):
		screen = self._getGameScreen()
		screen.blit(self.__background_img, (0, 0))
		screen.blit(self.__logo_img, self.__logo_rect)
		if self.__game_tip_show_flag:
			screen.blit(self.__game_tip, self.__game_tip_rect)

		if not self.__is_multiplayer_mode:
			screen.blit(self.__tank_cursor, self.__tank_rect)
			screen.blit(self.__player_render_red, self.__player_rect)
			screen.blit(self.__players_render_white, self.__players_rect)
		else:
			screen.blit(self.__tank_cursor, self.__tank_rect)
			screen.blit(self.__player_render_white, self.__player_rect)
			screen.blit(self.__players_render_red, self.__players_rect)

	def _main_loop(self):
		game_tip_flash_time = 25
		game_tip_flash_count = 0
		self.__game_tip_show_flag = True
		self.__is_multiplayer_mode = False
		clock = pygame.time.Clock()
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						self._getGameInstance().setMultiplayerMode(self.__is_multiplayer_mode)
						return
					elif event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_w or event.key == pygame.K_s:
						self.__is_multiplayer_mode = not self.__is_multiplayer_mode

			game_tip_flash_count += 1
			if game_tip_flash_count > game_tip_flash_time:
				self.__game_tip_show_flag = not self.__game_tip_show_flag
				game_tip_flash_count = 0

			if self.__is_multiplayer_mode:
				self.__tank_rect.right, self.__tank_rect.top = self.__players_rect.left - 10, self.__players_rect.top
			else:
				self.__tank_rect.right, self.__tank_rect.top = self.__player_rect.left - 10, self.__player_rect.top

			self._draw_interface()
			pygame.display.update()
			clock.tick(60)
