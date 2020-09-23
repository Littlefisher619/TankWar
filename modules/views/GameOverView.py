import sys
import pygame

from modules.TankGame import TankGame
from modules.views.AbstractView import AbstractView


class GameOverView(AbstractView):

	def _init_resources(self):
		config = self.config
		self.__background_img = pygame.image.load(config.OTHER_IMAGE_PATHS.get('background'))
		self.__gameover_logo = pygame.image.load(config.OTHER_IMAGE_PATHS.get('gameover'))
		self.__gameover_logo = pygame.transform.scale(self.__gameover_logo, (150, 75))
		self.__font = pygame.font.Font(config.FONTPATH, config.WIDTH // 12)
		self.__tank_cursor = pygame.image.load(
			config.PLAYER_TANK_IMAGE_PATHS.get('player1')[0]
		).convert_alpha().subsurface((0, 144), (48, 48))

	def _init_text(self):
		config = self.config
		if TankGame().is_win:
			self.__font_render = self.__font.render('Congratulations, You win!', True, (255, 255, 255))
		else:
			self.__font_render = self.__font.render('Sorry, You fail!', True, (255, 0, 0))
		self.__font_rect = self.__font_render.get_rect()
		self.__font_rect.centerx, self.__font_rect.centery = config.WIDTH / 2, config.HEIGHT / 3
		self.__restart_render_white = self.__font.render('RESTART', True, (255, 255, 255))
		self.__restart_render_red = self.__font.render('RESTART', True, (255, 0, 0))
		self.__quit_render_white = self.__font.render('QUIT', True, (255, 255, 255))
		self.__quit_render_red = self.__font.render('QUIT', True, (255, 0, 0))

	def _init_logo(self):
		config = self.config
		self.__gameover_logo_rect = self.__gameover_logo.get_rect()
		self.__gameover_logo_rect.midtop = config.WIDTH / 2, config.HEIGHT / 8

	def _draw_interface(self):
		screen = TankGame().screen
		screen.blit(self.__background_img, (0, 0))

		if self.__gameover_show_flag:
			screen.blit(self.__gameover_logo, self.__gameover_logo_rect)

		screen.blit(self.__font_render, self.__font_rect)

		if not self.__is_quit_game:
			screen.blit(self.__tank_cursor, self.__tank_rect)
			screen.blit(self.__restart_render_red, self.__restart_rect)
			screen.blit(self.__quit_render_white, self.__quit_rect)
		else:
			screen.blit(self.__tank_cursor, self.__tank_rect)
			screen.blit(self.__restart_render_white, self.__restart_rect)
			screen.blit(self.__quit_render_red, self.__quit_rect)

	def _init_bottons(self):
		config = self.config
		self.__tank_rect = self.__tank_cursor.get_rect()
		self.__restart_rect = self.__restart_render_white.get_rect()
		self.__restart_rect.left, self.__restart_rect.top = config.WIDTH / 2.4, config.HEIGHT / 2
		self.__quit_rect = self.__quit_render_white.get_rect()
		self.__quit_rect.left, self.__quit_rect.top = config.WIDTH / 2.4, config.HEIGHT / 1.6

	def _main_loop(self):
		gameover_flash_time = 25
		gameover_flash_count = 0
		self.__gameover_show_flag = True
		self.__is_quit_game = False

		clock = pygame.time.Clock()
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						TankGame().quit_game_flag = self.__is_quit_game
						return
					elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
						self.__is_quit_game = not self.__is_quit_game

			gameover_flash_count += 1
			if gameover_flash_count > gameover_flash_time:
				self.__gameover_show_flag = not self.__gameover_show_flag
				gameover_flash_count = 0
			if self.__is_quit_game:
				self.__tank_rect.right, self.__tank_rect.top = self.__quit_rect.left - 10, self.__quit_rect.top
			else:
				self.__tank_rect.right, self.__tank_rect.top = self.__restart_rect.left - 10, self.__restart_rect.top

			self._draw_interface()

			pygame.display.update()
			clock.tick(60)
