import sys
import pygame
import random
from modules.sprites.home import *
from modules.sprites.tanks import *
from modules.sprites.scenes import *
from enum import Enum
from .interfaces.Interface import Interface

from .sprites.tanks import DIRECTION


class EntityGroup(object):
    def __init__(self):
        self.player_tanks = pygame.sprite.Group()
        self.enemy_tanks = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()


    def update(self, scene_elements, home):
        # 更新并画我方子弹
        for bullet in self.player_bullets:
            if bullet.move():
                self.player_bullets.remove(bullet)
        # 更新并画敌方子弹
        for bullet in self.enemy_bullets:
            if bullet.move():
                self.enemy_bullets.remove(bullet)
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
        if self.__tank_player1.num_lifes >= 0:
            player_tank_list.append(self.__tank_player1)
        if self._game_instance.multiplayer_mode and (self.__tank_player1.num_lifes >= 0):
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

        if food.name == 'boom':
            for _ in self.__entities.enemy_tanks:
                self.__play_sound('bang')
            self.__total_enemy_num -= len(self.__entities.enemy_tanks)
            self.__entities.enemy_tanks = pygame.sprite.Group()
        elif food.name == 'clock':
            for enemy_tank in self.__entities.enemy_tanks:
                enemy_tank.set_still()
        elif food.name == 'gun':
            player_tank.improve_level()
        elif food.name == 'iron':
            for x, y in self.__home_walls_position:
                self.__scene_elements['iron_group'].add(Iron((x, y), self.__scene_images.get('iron')))
        elif food.name == 'protect':
            player_tank.protected = True
        elif food.name == 'star':
            player_tank.improve_level()
            player_tank.improve_level()
        elif food.name == 'tank':
            player_tank.add_life()

        self.__entities.foods.remove(food)

    def __dispatch_collisions(self):
        collision_results = {
            'group': {},
            'sprite': {},
            'foreach_sprite': {},
        }
        for (collision, args) in self.__collisions['group'].items():
            collision_results['group'][collision] = pygame.sprite.groupcollide(*args)

        for (collision, args) in self.__collisions['sprite'].items():
            collision_results['sprite'][collision] = pygame.sprite.spritecollide(*args)

        for (collision, args) in self.__collisions['foreach_sprite'].items():
            arg_list = list(args)
            sprite_list = arg_list[0]
            for sprite in sprite_list:
                arg_list[0] = sprite
                args = tuple(arg_list)
                collision_results['foreach_sprite'][sprite] = pygame.sprite.spritecollide(*args)

        for bullet in self.__entities.player_bullets:
            collision_result = pygame.sprite.spritecollide(bullet, self.__scene_elements.get('iron_group'), bullet.enhanced, None)
            if collision_result:
                self.__entities.player_bullets.remove(bullet)

        for player_tank in self.__entities.player_tanks:
            for food in self.__entities.foods:
                collision_result = pygame.sprite.collide_rect(player_tank, food)
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
                    if tank.num_lifes < 0:
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

        self.__entities.player_bullets.draw(screen)
        self.__entities.enemy_bullets.draw(screen)
        self.__entities.player_tanks.draw(screen)
        self.__entities.enemy_tanks.draw(screen)
        for tank in self.__entities.player_tanks:
            tank.draw(screen)
        for key, value in self.__scene_elements.items():
            value.draw(screen)
        self.__home.draw(screen)
        self.__entities.foods.draw(screen)
        self.__draw_game_panel()
        pygame.display.flip()

    def _main_loop(self):
        clock = pygame.time.Clock()
        # cheat for test
        self.__tank_player1.improve_level()
        self.__tank_player1.improve_level()
        self.__tank_player1.protected = True
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
                            enemy_tank = EnemyTank(position=position, config=self._game_config)
                            if (
                            not pygame.sprite.spritecollide(enemy_tank, self.__entities.enemy_tanks, False, None)) and (
                            not pygame.sprite.spritecollide(enemy_tank, self.__entities.player_tanks, False, None)):
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
                'PlayerBulletWithBrick': (self.__entities.player_bullets, self.__scene_elements.get('brick_group'), True, True),
                'EnemyBulletWithBrick': (self.__entities.enemy_bullets, self.__scene_elements.get('brick_group'), True, True),
                'EnemyBulletWithIron': (self.__entities.enemy_bullets, self.__scene_elements.get('iron_group'), True, False),
                'BulletWithBullet': (self.__entities.player_bullets, self.__entities.enemy_bullets, True, True),
                'PlayerTankWithTree': (self.__entities.player_tanks, self.__scene_elements.get('tree_group'), False, False),
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
        self.__tank_player1 = PlayerTank('player1', position=self.__player_spawn_point[0], game_config=self._game_config)
        self.__entities.player_tanks.add(self.__tank_player1)

        self.__tank_player2 = None
        if self._game_instance.multiplayer_mode:
            self.__tank_player2 = PlayerTank('player2', position=self.__player_spawn_point[1], game_config=self._game_config)
            self.__entities.player_tanks.add(self.__tank_player2)
        # 敌方坦克
        for position in self.__enemy_spawn_point:
            self.__entities.enemy_tanks.add(EnemyTank(position=position, config=self._game_config))
    def __init_home(self):
        self.__home = Home(position=self.__home_position, imagefile=self.__home_images)

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
        self.__init_home()
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
            16: {'text': 'Health: %s' % self.__tank_player1.num_lifes},
            17: {'text': 'Level: %s' % self.__tank_player1._level},
            23: {'text': 'Game Level: %s' % (self._game_instance.level + 1)},
            24: {'text': 'Remain Enemy: %s' % self.__total_enemy_num}
        }
        if self.__tank_player2:
            dynamic_text_tips[20] = {'text': 'Health: %s' % self.__tank_player2.num_lifes}
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
        self.__scene_elements = {
            'brick_group': pygame.sprite.Group(),
            'iron_group': pygame.sprite.Group(),
            'ice_group': pygame.sprite.Group(),
            'river_group': pygame.sprite.Group(),
            'tree_group': pygame.sprite.Group()
        }
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
                self.__home_position = line.split(':')[-1]
                self.__home_position = [
                    int(self.__home_position.split(',')[0]), int(self.__home_position.split(',')[1])
                ]
                self.__home_position = (
                    self.__border_len + self.__home_position[0] * self.__grid_size,
                    self.__border_len + self.__home_position[1] * self.__grid_size
                )
            # 大本营周围位置
            elif line.startswith('%HOMEAROUNDPOS'):
                self.__home_walls_position = line.split(':')[-1]
                self.__home_walls_position = [
                    [
                        int(pos.split(',')[0]), int(pos.split(',')[1])
                    ] for pos in self.__home_walls_position.split(' ')
                ]
                self.__home_walls_position = [
                    (
                        self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size
                    ) for pos in self.__home_walls_position
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
                    if elem == 'B':
                        self.__scene_elements['brick_group'].add(
                            Brick(position, self.__scene_images.get('brick'))
                        )
                    elif elem == 'I':
                        self.__scene_elements['iron_group'].add(
                            Iron(position, self.__scene_images.get('iron'))
                        )
                    elif elem == 'R':
                        print(position)
                        self.__scene_elements['river_group'].add(
                            River(position, self.__scene_images.get(random.choice(['river1', 'river2'])))
                        )
                    elif elem == 'C':
                        self.__scene_elements['ice_group'].add(
                            Ice(position, self.__scene_images.get('ice'))
                        )
                    elif elem == 'T':
                        self.__scene_elements['tree_group'].add(
                            Tree(position, self.__scene_images.get('tree'))
                        )
