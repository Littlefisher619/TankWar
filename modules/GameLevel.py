import sys
import pygame
import random
from modules.sprites.home import *
from modules.sprites.tanks import *
from modules.sprites.scenes import *
from enum import Enum
from .interfaces.Interface import Interface

from .sprites.tanks import DIRECTION
from pygame.sprite import spritecollide, groupcollide, collide_rect


class SceneElementsGroup(object):
    def __init__(self):
        self.ice_group = pygame.sprite.Group()
        self.iron_group = pygame.sprite.Group()
        self.brick_group = pygame.sprite.Group()
        self.tree_group = pygame.sprite.Group()
        self.river_group = pygame.sprite.Group()

    def add(self, scene_element):
        if isinstance(scene_element, Ice):
            self.ice_group.add(scene_element)
        elif isinstance(scene_element, Brick):
            self.brick_group.add(scene_element)
        elif isinstance(scene_element, Tree):
            self.tree_group.add(scene_element)
        elif isinstance(scene_element, River):
            self.river_group.add(scene_element)
        elif isinstance(scene_element, Iron):
            self.iron_group.add(scene_element)

    def draw(self, screen, layer):
        if layer == 1:
            self.ice_group.draw(screen)
            self.river_group.draw(screen)
        elif layer == 2:
            self.brick_group.draw(screen)
            self.iron_group.draw(screen)
            self.tree_group.draw(screen)


class EntityGroup(object):
    def __init__(self):
        self.player_tanks = pygame.sprite.Group()
        self.enemy_tanks = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()

    def draw(self, screen, layer):
        if layer == 1:
            self.player_bullets.draw(screen)
            self.enemy_bullets.draw(screen)
            self.player_tanks.draw(screen)
            for tank in self.player_tanks:
                tank.draw(screen)
            self.enemy_tanks.draw(screen)
        elif layer == 2:
            self.foods.draw(screen)

    def update(self, scene_elements, home):
        # 更新并画我方子弹
        for bullet in self.player_bullets:
            if bullet.move():
                bullet.kill()
        # 更新并画敌方子弹
        for bullet in self.enemy_bullets:
            if bullet.move():
                bullet.kill()
        # 更新并画我方坦克
        for tank in self.player_tanks:
            tank.update()
        # 更新并画敌方坦克
        for tank in self.enemy_tanks:
            self.enemy_tanks.remove(tank)
            remove_flag, bullet = tank.update(
                scene_elements, self.player_tanks, self.enemy_tanks, home
            )
            self.enemy_tanks.add(tank)
            if isinstance(bullet, Bullet):
                self.enemy_bullets.add(bullet)
            if remove_flag:
                self.enemy_tanks.remove(tank)
        # 更新食物
        for food in self.foods:
            if food.update():
                self.foods.remove(food)


class GameLevel(Interface):

    def _init_resources(self):
        config = self._game_config
        self.__sounds = self._game_instance.sounds
        self.__scene_images = config.SCENE_IMAGE_PATHS
        self.__other_images = config.OTHER_IMAGE_PATHS
        self.__player_tank_images = config.PLAYER_TANK_IMAGE_PATHS
        self.__food_images = config.FOOD_IMAGE_PATHS
        self.__home_images = config.HOME_IMAGE_PATHS
        self.__background_img = pygame.image.load(self.__other_images.get('background'))
        self.__font = pygame.font.Font(config.FONTPATH, config.HEIGHT // 35)

        self.__border_len = config.BORDER_LEN
        self.__grid_size = config.GRID_SIZE
        self.__screen_width, self.__screen_height = config.WIDTH, config.HEIGHT
        self.__panel_width = config.PANEL_WIDTH
        self.__tank_factory = TankFactory(self._game_config)
        self.__scene_factory = SceneFactory(self._game_config)
        self.__scene_elements = None

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
        self._game_instance.init_game_window(
            (self._game_config.WIDTH + self._game_config.PANEL_WIDTH, self._game_config.HEIGHT)
        )

    def __play_sound(self,sound):
        self.__sounds[sound].play()

    def __dispatch_player_operation(self):
        key_pressed = pygame.key.get_pressed()
        key_maps = {
            'dir': {
                self.__tank_player1: {
                    pygame.K_w: DIRECTION.UP,
                    pygame.K_s: DIRECTION.DOWN,
                    pygame.K_a: DIRECTION.LEFT,
                    pygame.K_d: DIRECTION.RIGHT,
                },
                self.__tank_player2: {
                    pygame.K_UP: DIRECTION.UP,
                    pygame.K_DOWN: DIRECTION.DOWN,
                    pygame.K_LEFT: DIRECTION.LEFT,
                    pygame.K_RIGHT: DIRECTION.RIGHT,
                },
            },
            'fire': {
                self.__tank_player1: pygame.K_SPACE,
                self.__tank_player2: pygame.K_KP0,
            },

        }

        # 玩家一, WSAD移动, 空格键射击
        player_tank_list = []
        if self.__tank_player1.health >= 0:
            player_tank_list.append(self.__tank_player1)
        if self._game_instance.multiplayer_mode and (self.__tank_player1.health >= 0):
            player_tank_list.append(self.__tank_player2)

        for tank in player_tank_list:
            for key, dir in key_maps['dir'][tank].items():
                if key_pressed[key]:
                    self.__entities.player_tanks.remove(tank)
                    tank.move(dir, self.__scene_elements, self.__entities.player_tanks,
                              self.__entities.enemy_tanks, self.__home)
                    tank.roll()
                    self.__entities.player_tanks.add(tank)
                    break

            if key_pressed[key_maps['fire'][tank]]:
                bullet = tank.shoot()
                if bullet:
                    self.__play_sound('fire') if tank._level < 2 else self.__play_sound('Gunfire')
                    self.__entities.player_bullets.add(bullet)

    def __dispatch_food_effect(self, food, player_tank):
        self.__play_sound('add')

        if food.type == Foods.BOOM:
            for _ in self.__entities.enemy_tanks:
                self.__play_sound('bang')
            self.__total_enemy_num -= len(self.__entities.enemy_tanks)
            self.__entities.enemy_tanks = pygame.sprite.Group()
        elif food.type == Foods.CLOCK:
            for enemy_tank in self.__entities.enemy_tanks:
                enemy_tank.set_still()
        elif food.type == Foods.GUN:
            player_tank.improve_level()
        elif food.type == Foods.IRON:
            for x, y in self.__home.walls_position:
                self.__scene_elements.add(
                    self.__scene_factory.create_element((x, y), SceneFactory.IRON)
                )
        elif food.type == Foods.PROTECT:
            player_tank.protected = True
        elif food.type == Foods.STAR:
            player_tank.improve_level()
            player_tank.improve_level()
        elif food.type == Foods.TANK:
            player_tank.add_health()

        self.__entities.foods.remove(food)

    def __dispatch_collisions(self):
        collision_results = {
            'group': {},
            'sprite': {},
            'foreach_sprite': {},
        }
        for (collision, args) in self.__collisions['group'].items():
            collision_results['group'][collision] = groupcollide(*args)

        for (collision, args) in self.__collisions['sprite'].items():
            collision_results['sprite'][collision] = spritecollide(*args)

        for (collision, args) in self.__collisions['foreach_sprite'].items():
            arg_list = list(args)
            sprite_list = arg_list[0]
            for sprite in sprite_list:
                arg_list[0] = sprite
                args = tuple(arg_list)
                collision_results['foreach_sprite'][sprite] = spritecollide(*args)

        for bullet in self.__entities.player_bullets:
            collision_result = spritecollide(bullet, self.__scene_elements.iron_group, bullet.enhanced, None)
            if collision_result:
                bullet.kill()

        for player_tank in self.__entities.player_tanks:
            for food in self.__entities.foods:
                collision_result = collide_rect(player_tank, food)
                if collision_result:
                    self.__dispatch_food_effect(food, player_tank)

        # --我方子弹撞敌方坦克
        for tank in self.__entities.enemy_tanks:
            if collision_results['foreach_sprite'][tank]:
                if tank.food:
                    self.__entities.foods.add(tank.food)
                    tank.clear_food()
                if tank.decrease_level():
                    self.__play_sound('bang')
                    self.__total_enemy_num -= 1

        # --敌方子弹撞我方坦克
        for tank in self.__entities.player_tanks:
            if collision_results['foreach_sprite'][tank]:
                if tank.protected:
                    self.__play_sound('blast')
                else:
                    if tank.decrease_level():
                        self.__play_sound('bang')
                    if tank.health < 0:
                        self.__entities.player_tanks.remove(tank)

        if collision_results['sprite']['PlayerBulletWithHome'] or collision_results['sprite']['EnemyBulletWithHome']:
            self.__is_win_flag = False
            self.__has_next_loop = False
            self.__play_sound('bang')
            self.__home.destroyed = True

        if collision_results['group']['PlayerTankWithTree']:
            self.__play_sound('hit')

    def _draw_interface(self):
        screen = self._game_screen
        screen.fill((0, 0, 0))
        screen.blit(self.__background_img, (0, 0))
        self.__scene_elements.draw(screen, 1)
        self.__entities.draw(screen, 1)
        self.__scene_elements.draw(screen, 2)
        self.__home.draw(screen)
        self.__entities.draw(screen, 2)
        self.__draw_game_panel()
        pygame.display.flip()

    def _main_loop(self):
        clock = pygame.time.Clock()
        # cheat for test
        # self.__tank_player1.improve_level()
        # self.__tank_player1.improve_level()
        # self.__tank_player1.protected = True
        while self.__has_next_loop:
            # 用户事件捕捉
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # --敌方坦克生成
                elif event.type == self.__generate_enemies_event:
                    if self.max_enemy_num > len(self.__entities.enemy_tanks):
                        for position in self.__enemy_spawn_point:
                            if len(self.__entities.enemy_tanks) == self.__total_enemy_num:
                                break
                            enemy_tank = self.__tank_factory.create_tank(position, TankFactory.ENEMY_TANK)
                            if spritecollide(enemy_tank, self.__entities.enemy_tanks, False, None) or\
                                spritecollide(enemy_tank, self.__entities.player_tanks, False, None):
                                del enemy_tank
                            else:
                                self.__entities.enemy_tanks.add(enemy_tank)
            # --用户按键
            self.__dispatch_player_operation()
            # 碰撞检测
            self.__dispatch_collisions()
            self.__entities.update(self.__scene_elements, self.__home)
            self._draw_interface()
            # 我方坦克都挂了
            if len(self.__entities.player_tanks) == 0:
                self.__is_win_flag = False
                self.__has_next_loop = False
            # 敌方坦克都挂了
            if self.__total_enemy_num <= 0:
                self.__is_win_flag = True
                self.__has_next_loop = False

            clock.tick(60)

    def __init_collision_config(self):
        self.__collisions = {
            'group': {
                'PlayerBulletWithBrick': (self.__entities.player_bullets, self.__scene_elements.brick_group, True, True),
                'EnemyBulletWithBrick': (self.__entities.enemy_bullets, self.__scene_elements.brick_group, True, True),
                'EnemyBulletWithIron': (self.__entities.enemy_bullets, self.__scene_elements.iron_group, True, False),
                'BulletWithBullet': (self.__entities.player_bullets, self.__entities.enemy_bullets, True, True),
                'PlayerTankWithTree': (self.__entities.player_tanks, self.__scene_elements.tree_group, False, False),
            },
            'sprite': {
                'EnemyBulletWithHome': (self.__home, self.__entities.enemy_bullets, True, None),
                'PlayerBulletWithHome': (self.__home, self.__entities.player_bullets, True, None),

            },
            'foreach_sprite': {
                'PlayerTankWithEnemyBullet': (self.__entities.player_tanks, self.__entities.enemy_bullets, True, None),
                'EnemyTankWithPlayerBullet': (self.__entities.enemy_tanks, self.__entities.player_bullets, True, None),
            }
        }

    def __init_tanks(self):
        self.__tank_player1 = self.__tank_factory.create_tank(
            self.__player_spawn_point[0], TankFactory.PLAYER1_TANK
        )
        self.__entities.player_tanks.add(self.__tank_player1)

        self.__tank_player2 = None
        if self._game_instance.multiplayer_mode:
            self.__tank_player2 = self.__tank_factory.create_tank(
                self.__player_spawn_point[1], TankFactory.PLAYER2_TANK
            )
            self.__entities.player_tanks.add(self.__tank_player2)
        # 敌方坦克
        for position in self.__enemy_spawn_point:
            self.__entities.enemy_tanks.add(
                self.__tank_factory.create_tank(position, TankFactory.ENEMY_TANK)
            )

    def __init_user_event(self):
        self.__generate_enemies_event = pygame.constants.USEREVENT
        pygame.time.set_timer(self.__generate_enemies_event, 20000)

    def __init_entities(self):
        self.__entities = EntityGroup()

    def show(self):
        self._init_game_window()
        self._init_text()
        self.__load_level_file()
        self.__init_entities()
        self.__init_user_event()
        self.__init_tanks()
        self.__init_collision_config()
        self.__play_sound('start')
        self.__is_win_flag = False
        self.__has_next_loop = True
        self._main_loop()
        self._game_instance.is_win = self.__is_win_flag


    '''显示游戏面板'''
    def __draw_game_panel(self):
        color_white = (255, 255, 255)
        dynamic_text_tips = {
            16: {'text': 'Health: %s' % self.__tank_player1.health},
            17: {'text': 'Level: %s' % self.__tank_player1._level},
            23: {'text': 'Game Level: %s' % (self._game_instance.level + 1)},
            24: {'text': 'Remain Enemy: %s' % self.__total_enemy_num}
        }
        if self.__tank_player2:
            dynamic_text_tips[20] = {'text': 'Health: %s' % self.__tank_player2.health}
            dynamic_text_tips[21] = {'text': 'Level: %s' % self.__tank_player2._level}
        else:
            dynamic_text_tips[20] = {'text': 'Health: %s' % None}
            dynamic_text_tips[21] = {'text': 'Level: %s' % None}

        for pos, tip in dynamic_text_tips.items():
            tip['render'] = self.__font.render(tip['text'], True, color_white)
            tip['rect'] = tip['render'].get_rect()
            tip['rect'].left, tip['rect'].top = self.__screen_width + 5, self.__screen_height * pos / 30

        screen = self._game_screen
        for pos, tip in self.__fix_text_tips.items():
            screen.blit(tip['render'], tip['rect'])
        for pos, tip in dynamic_text_tips.items():
            screen.blit(tip['render'], tip['rect'])


    def __load_level_file(self):
        self.__scene_elements = SceneElementsGroup()

        elems_map = {
            'B': SceneFactory.BRICK,
            'I': SceneFactory.IRON,
            'C': SceneFactory.ICE,
            'T': SceneFactory.TREE,
            'R': SceneFactory.RIVER_1
        }

        home_walls_position = []
        home_position = ()

        f = open(self._game_instance.level_file, errors='ignore')
        num_row = -1
        for line in f.readlines():
            line = line.strip('\n')
            # 注释
            if line.startswith('#') or (not line):
                continue
            # 敌方坦克总数量
            elif line.startswith('%TOTALENEMYNUM'):
                self.__total_enemy_num = int(line.split(':')[-1])
            # 场上敌方坦克最大数量
            elif line.startswith('%MAXENEMYNUM'):
                self.max_enemy_num = int(line.split(':')[-1])
            # 大本营位置
            elif line.startswith('%HOMEPOS'):
                home_position = line.split(':')[-1]
                home_position = [
                    int(home_position.split(',')[0]), int(home_position.split(',')[1])
                ]
                home_position = (
                    self.__border_len + home_position[0] * self.__grid_size,
                    self.__border_len + home_position[1] * self.__grid_size
                )
            # 大本营周围位置
            elif line.startswith('%HOMEAROUNDPOS'):
                home_walls_position = line.split(':')[-1]
                home_walls_position = [
                    [
                        int(pos.split(',')[0]), int(pos.split(',')[1])
                    ] for pos in home_walls_position.split(' ')
                ]
                home_walls_position = [
                    (
                        self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size
                    ) for pos in home_walls_position
                ]
            # 我方坦克初始位置
            elif line.startswith('%PLAYERTANKPOS'):
                self.__player_spawn_point = line.split(':')[-1]
                self.__player_spawn_point = [
                    [
                        int(pos.split(',')[0]), int(pos.split(',')[1])
                    ] for pos in self.__player_spawn_point.split(' ')
                ]
                self.__player_spawn_point = [
                    (
                        self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size
                    ) for pos in self.__player_spawn_point
                ]
            # 敌方坦克初始位置
            elif line.startswith('%ENEMYTANKPOS'):
                self.__enemy_spawn_point = line.split(':')[-1]
                self.__enemy_spawn_point = [
                    [
                        int(pos.split(',')[0]), int(pos.split(',')[1])
                    ] for pos in self.__enemy_spawn_point.split(' ')
                ]
                self.__enemy_spawn_point = [
                    (
                        self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size
                    ) for pos in self.__enemy_spawn_point
                ]
            # 地图元素
            else:
                num_row += 1
                for num_col, elem in enumerate(line.split(' ')):
                    position = self.__border_len + num_col * self.__grid_size, self.__border_len + num_row * self.__grid_size

                    scene_element = None
                    if elem in elems_map:
                        scene_element = self.__scene_factory.create_element(position, elems_map[elem])
                    elif elem == 'R':
                        scene_element = self.__scene_factory.create_element(
                            position, random.choice([SceneFactory.RIVER_1, SceneFactory.RIVER_2])
                        )
                    if scene_element is not None:
                        self.__scene_elements.add(scene_element)
        self.__home = Home(position=home_position, imagefile=self.__home_images, walls_position=home_walls_position)