import sys
import pygame
import random
from modules.sprites.home import *
from modules.sprites.tanks import *
from modules.sprites.scenes import *
from enum import Enum
from .interfaces.Interface import Interface


class EntityGroup(object):
	def __init__(self):
		self.player_tanks = pygame.sprite.Group()
		self.enemy_tanks = pygame.sprite.Group()
		self.player_bullets = pygame.sprite.Group()
		self.enemy_bullets = pygame.sprite.Group()
		self.foods = pygame.sprite.Group()


class GameLevel(Interface):
	def _init_resources(self):
		config = self._getGameInstance().getConfig()
		self.__sounds = self._getGameInstance().getSounds()
		self.__scene_images = config.SCENE_IMAGE_PATHS
		self.__other_images = config.OTHER_IMAGE_PATHS
		self.__player_tank_images = config.PLAYER_TANK_IMAGE_PATHS
		self.__bullet_images = config.BULLET_IMAGE_PATHS
		self.__enemy_tank_images = config.ENEMY_TANK_IMAGE_PATHS
		self.__food_images = config.FOOD_IMAGE_PATHS
		self.__home_images = config.HOME_IMAGE_PATHS
		self.__background_img = pygame.image.load(self.__other_images.get('background'))
		self.__font = pygame.font.Font(config.FONTPATH, config.HEIGHT // 30)

		self.__border_len = config.BORDER_LEN
		self.__grid_size = config.GRID_SIZE
		self.__screen_width, self.__screen_height = config.WIDTH, config.HEIGHT
		self.__panel_width = config.PANEL_WIDTH
		self.__scene_elements = {
			'brick_group': pygame.sprite.Group(),
			'iron_group': pygame.sprite.Group(),
			'ice_group': pygame.sprite.Group(),
			'river_group': pygame.sprite.Group(),
			'tree_group': pygame.sprite.Group()
		}

	def _init_text(self):
		color_white = (255, 255, 255)
		self.__fix_text_tips = {
			1: {'text': 'Operate-P1'},
			2: {'text': 'K_w: Up'},
			3: {'text': 'K_s: Down'},
			4: {'text': 'K_a: Left'},
			5: {'text': 'K_d: Right'},
			6: {'text': 'K_SPACE: Shoot'},
			8: {'text': 'Operate-P2:'},
			9: {'text': 'K_UP: Up'},
			10: {'text': 'K_DOWN: Down'},
			11: {'text': 'K_LEFT: Left'},
			12: {'text': 'K_RIGHT: Right'},
			13: {'text': 'K_KP0: Shoot'},
			15: {'text': 'State-P1:'},
			19: {'text': 'State-P2:'},
		}
		for pos, tip in self.__fix_text_tips.items():
			tip['render'] = self.__font.render(tip['text'], True, color_white)
			tip['rect'] = tip['render'].get_rect()
			tip['rect'].left, tip['rect'].top = self.__screen_width + 5, self.__screen_height * pos / 30

		pass

	'''开始游戏'''
	def _init_game_window(self):
		self._getGameInstance().init_game_window(
			(self._getGameConfig().WIDTH + self._getGameConfig().PANEL_WIDTH, self._getGameConfig().HEIGHT)
		)

	def __dispatch_player_operation(self):
		key_pressed = pygame.key.get_pressed()
		key_maps = {
			self.__tank_player1: {
				pygame.K_w: 'up',
				pygame.K_s: 'down',
				pygame.K_a: 'left',
				pygame.K_d: 'right'

			},
			self.__tank_player2: {
				pygame.K_UP: 'up',
				pygame.K_DOWN: 'down',
				pygame.K_LEFT: 'left',
				pygame.K_RIGHT: 'right'
			},
		}

		# 玩家一, WSAD移动, 空格键射击
		player_tank_list = []
		if self.__tank_player1.num_lifes >= 0:
			player_tank_list.append(self.__tank_player1)
		if self._getGameInstance().getMultiPlayerMode() and (self.__tank_player1.num_lifes >= 0):
			player_tank_list.append(self.__tank_player2)

		for tank in player_tank_list:
			for key, dir in key_maps[tank].items():
				if key_pressed[key]:
					self.__entities.player_tanks.remove(tank)
					tank.move(dir, self.__scene_elements, self.__entities.player_tanks,
									  self.__entities.enemy_tanks, self.__home)
					self.__entities.player_tanks.add(tank)
					break

			if key_pressed[pygame.K_SPACE]:
				bullet = tank.shoot()
				if bullet:
					self.__sounds['fire'].play() if tank.tanklevel < 2 else self.__sounds['Gunfire'].play()
					self.__entities.player_bullets.add(bullet)

	def __dispatch_collisions(self):
		pass
	def show(self):
		self._init_game_window()
		self.__load_level_file()
		self._init_text()
		self.__entities = EntityGroup()
		screen = self._getGameInstance().getScreen()

		self.__entities.player_tanks = pygame.sprite.Group()
		self.__entities.enemy_tanks = pygame.sprite.Group()
		self.__entities.player_bullets = pygame.sprite.Group()
		self.__entities.enemy_bullets = pygame.sprite.Group()
		self.__entities.foods = pygame.sprite.Group()
		# 定义敌方坦克生成事件
		generate_enemies_event = pygame.constants.USEREVENT
		pygame.time.set_timer(generate_enemies_event, 20000)
		# 我方大本营
		self.__home = Home(position=self.home_position, imagepaths=self.__home_images)
		# 我方坦克

		self.__tank_player1 = PlayerTank('player1', position=self.player_tank_positions[0], player_tank_image_paths=self.__player_tank_images, border_len=self.__border_len, screensize=[self.__screen_width, self.__screen_height], bullet_image_paths=self.__bullet_images, protected_mask_path=self.__other_images.get('protect'), boom_image_path=self.__other_images.get('boom_static'))
		self.__entities.player_tanks.add(self.__tank_player1)

		self.__tank_player2 = None
		if self._getGameInstance().getMultiPlayerMode():
			self.__tank_player2 = PlayerTank('player2', position=self.player_tank_positions[1], player_tank_image_paths=self.__player_tank_images, border_len=self.__border_len, screensize=[self.__screen_width, self.__screen_height], bullet_image_paths=self.__bullet_images, protected_mask_path=self.__other_images.get('protect'), boom_image_path=self.__other_images.get('boom_static'))
			self.__entities.player_tanks.add(self.__tank_player2)
		# 敌方坦克
		for position in self.enemy_tank_positions:
			self.__entities.enemy_tanks.add(EnemyTank(enemy_tank_image_paths=self.__enemy_tank_images, appear_image_path=self.__other_images.get('appear'), position=position, border_len=self.__border_len, screensize=[self.__screen_width, self.__screen_height], bullet_image_paths=self.__bullet_images, food_image_paths=self.__food_images, boom_image_path=self.__other_images.get('boom_static')))
		# 游戏开始音乐
		self.__sounds['start'].play()
		clock = pygame.time.Clock()
		# 该关卡通过与否的flags
		is_win = False
		is_running = True
		# 游戏主循环
		while is_running:
			screen.fill((0, 0, 0))
			screen.blit(self.__background_img, (0, 0))
			# 用户事件捕捉
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				# --敌方坦克生成
				elif event.type == generate_enemies_event:
					if self.max_enemy_num > len(self.__entities.enemy_tanks):
						for position in self.enemy_tank_positions:
							if len(self.__entities.enemy_tanks) == self.total_enemy_num:
								break
							enemy_tank = EnemyTank(enemy_tank_image_paths=self.__enemy_tank_images, appear_image_path=self.__other_images.get('appear'), position=position, border_len=self.__border_len, screensize=[self.__screen_width, self.__screen_height], bullet_image_paths=self.__bullet_images, food_image_paths=self.__food_images, boom_image_path=self.__other_images.get('boom_static'))
							if (not pygame.sprite.spritecollide(enemy_tank, self.__entities.enemy_tanks, False, None)) and (not pygame.sprite.spritecollide(enemy_tank, self.__entities.player_tanks, False, None)):
								self.__entities.enemy_tanks.add(enemy_tank)
			# --用户按键

			self.__dispatch_player_operation()

			# 碰撞检测
			# --子弹和砖墙
			pygame.sprite.groupcollide(self.__entities.player_bullets, self.__scene_elements.get('brick_group'), True, True)
			pygame.sprite.groupcollide(self.__entities.enemy_bullets, self.__scene_elements.get('brick_group'), True, True)
			# --子弹和铁墙
			for bullet in self.__entities.player_bullets:
				if pygame.sprite.spritecollide(bullet, self.__scene_elements.get('iron_group'), bullet.is_stronger, None):
					self.__entities.player_bullets.remove(bullet)
			pygame.sprite.groupcollide(self.__entities.enemy_bullets, self.__scene_elements.get('iron_group'), True, False)
			# --子弹撞子弹
			pygame.sprite.groupcollide(self.__entities.player_bullets, self.__entities.enemy_bullets, True, True)
			# --我方子弹撞敌方坦克
			for tank in self.__entities.enemy_tanks:
				if pygame.sprite.spritecollide(tank, self.__entities.player_bullets, True, None):
					if tank.food:
						self.__entities.foods.add(tank.food)
						tank.food = None
					if tank.decreaseTankLevel():
						self.__sounds['bang'].play()
						self.total_enemy_num -= 1
			# --敌方子弹撞我方坦克
			for tank in self.__entities.player_tanks:
				if pygame.sprite.spritecollide(tank, self.__entities.enemy_bullets, True, None):
					if tank.is_protected:
						self.__sounds['blast'].play()
					else:
						if tank.decreaseTankLevel():
							self.__sounds['bang'].play()
						if tank.num_lifes < 0:
							self.__entities.player_tanks.remove(tank)
			# --我方子弹撞我方大本营
			if pygame.sprite.spritecollide(self.__home, self.__entities.player_bullets, True, None):
				is_win = False
				is_running = False
				self.__home.setDead()
			# --敌方子弹撞我方大本营
			if pygame.sprite.spritecollide(self.__home, self.__entities.enemy_bullets, True, None):
				is_win = False
				is_running = False
				self.__home.setDead()
			# --我方坦克在植物里
			if pygame.sprite.groupcollide(self.__entities.player_tanks, self.__scene_elements.get('tree_group'), False, False):
				self.__sounds['hit'].play()
			# --我方坦克吃到食物
			for player_tank in self.__entities.player_tanks:
				for food in self.__entities.foods:
					if pygame.sprite.collide_rect(player_tank, food):
						if food.name == 'boom':
							self.__sounds['add'].play()
							for _ in self.__entities.enemy_tanks:
								self.__sounds['bang'].play()
							self.total_enemy_num -= len(self.__entities.enemy_tanks)
							self.__entities.enemy_tanks = pygame.sprite.Group()
						elif food.name == 'clock':
							self.__sounds['add'].play()
							for enemy_tank in self.__entities.enemy_tanks:
								enemy_tank.setStill()
						elif food.name == 'gun':
							self.__sounds['add'].play()
							player_tank.improveTankLevel()
						elif food.name == 'iron':
							self.__sounds['add'].play()
							self.__pretectHome()
						elif food.name == 'protect':
							self.__sounds['add'].play()
							player_tank.setProtected()
						elif food.name == 'star':
							self.__sounds['add'].play()
							player_tank.improveTankLevel()
							player_tank.improveTankLevel()
						elif food.name == 'tank':
							self.__sounds['add'].play()
							player_tank.addLife()
						self.__entities.foods.remove(food)
			# 画场景地图
			for key, value in self.__scene_elements.items():
				if key in ['ice_group', 'river_group']:
					value.draw(screen)
			# 更新并画我方子弹
			for bullet in self.__entities.player_bullets:
				if bullet.move():
					self.__entities.player_bullets.remove(bullet)
			self.__entities.player_bullets.draw(screen)
			# 更新并画敌方子弹
			for bullet in self.__entities.enemy_bullets:
				if bullet.move():
					self.__entities.enemy_bullets.remove(bullet)
			self.__entities.enemy_bullets.draw(screen)
			# 更新并画我方坦克
			for tank in self.__entities.player_tanks:
				tank.update()
				tank.draw(screen)
			# 更新并画敌方坦克
			for tank in self.__entities.enemy_tanks:
				self.__entities.enemy_tanks.remove(tank)
				data_return = tank.update(self.__scene_elements, self.__entities.player_tanks, self.__entities.enemy_tanks, self.__home)
				self.__entities.enemy_tanks.add(tank)
				if data_return.get('bullet'):
					self.__entities.enemy_bullets.add(data_return.get('bullet'))
				if data_return.get('boomed'):
					self.__entities.enemy_tanks.remove(tank)
			self.__entities.enemy_tanks.draw(screen)
			# 画场景地图
			for key, value in self.__scene_elements.items():
				if key not in ['ice_group', 'river_group']:
					value.draw(screen)
			# 画大本营
			self.__home.draw(screen)
			# 更新并显示食物
			for food in self.__entities.foods:
				if food.update():
					self.__entities.foods.remove(food)
			self.__entities.foods.draw(screen)
			self.__draw_game_panel(screen, self.__tank_player1, self.__tank_player2) if self._getGameInstance().getMultiPlayerMode() else self.__draw_game_panel(screen, self.__tank_player1)
			# 我方坦克都挂了
			if len(self.__entities.player_tanks) == 0:
				is_win = False
				is_running = False
			# 敌方坦克都挂了
			if self.total_enemy_num <= 0:
				is_win = True
				is_running = False
			pygame.display.flip()
			clock.tick(60)
		screen = pygame.display.set_mode((self.__screen_width, self.__screen_height))
		self._getGameInstance().setIsWin(is_win)


	'''显示游戏面板'''
	def __draw_game_panel(self, screen, tank_player1, tank_player2=None):
		color_white = (255, 255, 255)
		dynamic_text_tips = {
			16: {'text': 'Life: %s' % tank_player1.num_lifes},
			17: {'text': 'TLevel: %s' % tank_player1.tanklevel},
			23: {'text': 'Game Level: %s' % self._getGameInstance().getLevel()},
			24: {'text': 'Remain Enemy: %s' % self.total_enemy_num}
		}
		if tank_player2:
			dynamic_text_tips[20] = {'text': 'Life: %s' % tank_player2.num_lifes}
			dynamic_text_tips[21] = {'text': 'TLevel: %s' % tank_player2.tanklevel}
		else:
			dynamic_text_tips[20] = {'text': 'Life: %s' % None}
			dynamic_text_tips[21] = {'text': 'TLevel: %s' % None}

		for pos, tip in dynamic_text_tips.items():
			tip['render'] = self.__font.render(tip['text'], True, color_white)
			tip['rect'] = tip['render'].get_rect()
			tip['rect'].left, tip['rect'].top = self.__screen_width + 5, self.__screen_height * pos / 30

		for pos, tip in self.__fix_text_tips.items():
			screen.blit(tip['render'], tip['rect'])
		for pos, tip in dynamic_text_tips.items():
			screen.blit(tip['render'], tip['rect'])

	'''保护大本营'''
	def __pretectHome(self):
		for x, y in self.home_around_positions:
			self.__scene_elements['iron_group'].add(Iron((x, y), self.__scene_images.get('iron')))
	'''解析关卡文件'''
	def __load_level_file(self):

		f = open(self._getGameInstance().getLevelFile(), errors='ignore')
		num_row = -1
		for line in f.readlines():
			line = line.strip('\n')
			# 注释
			if line.startswith('#') or (not line):
				continue
			# 敌方坦克总数量
			elif line.startswith('%TOTALENEMYNUM'):
				self.total_enemy_num = int(line.split(':')[-1])
			# 场上敌方坦克最大数量
			elif line.startswith('%MAXENEMYNUM'):
				self.max_enemy_num = int(line.split(':')[-1])
			# 大本营位置
			elif line.startswith('%HOMEPOS'):
				self.home_position = line.split(':')[-1]
				self.home_position = [int(self.home_position.split(',')[0]), int(self.home_position.split(',')[1])]
				self.home_position = (self.__border_len + self.home_position[0] * self.__grid_size, self.__border_len + self.home_position[1] * self.__grid_size)
			# 大本营周围位置
			elif line.startswith('%HOMEAROUNDPOS'):
				self.home_around_positions = line.split(':')[-1]
				self.home_around_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in self.home_around_positions.split(' ')]
				self.home_around_positions = [(self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for pos in self.home_around_positions]
			# 我方坦克初始位置
			elif line.startswith('%PLAYERTANKPOS'):
				self.player_tank_positions = line.split(':')[-1]
				self.player_tank_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in self.player_tank_positions.split(' ')]
				self.player_tank_positions = [(self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for pos in self.player_tank_positions]
			# 敌方坦克初始位置
			elif line.startswith('%ENEMYTANKPOS'):
				self.enemy_tank_positions = line.split(':')[-1]
				self.enemy_tank_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in self.enemy_tank_positions.split(' ')]
				self.enemy_tank_positions = [(self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for pos in self.enemy_tank_positions]
			# 地图元素
			else:
				num_row += 1
				for num_col, elem in enumerate(line.split(' ')):
					position = self.__border_len + num_col * self.__grid_size, self.__border_len + num_row * self.__grid_size
					if elem == 'B':
						self.__scene_elements['brick_group'].add(Brick(position, self.__scene_images.get('brick')))
					elif elem == 'I':
						self.__scene_elements['iron_group'].add(Iron(position, self.__scene_images.get('iron')))
					elif elem == 'R':
						self.__scene_elements['river_group'].add(River(position, self.__scene_images.get(random.choice(['river1', 'river2']))))
					elif elem == 'C':
						self.__scene_elements['ice_group'].add(Ice(position, self.__scene_images.get('ice')))
					elif elem == 'T':
						self.__scene_elements['tree_group'].add(Tree(position, self.__scene_images.get('tree')))