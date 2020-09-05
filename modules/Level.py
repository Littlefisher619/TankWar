from .interfaces.Interface import Interface
import random
import sys
import pygame
from modules.sprites.home import *
from modules.sprites.tanks import *
from modules.sprites.scenes import *

class Level(Interface):

    def _init_resources(self):
        config = self._getGameConfig()

        self.__is_multiplayer_mode = self._getGameInstance().getMultiPlayerMode
        self.__sounds = self._getGameInstance().getSounds()
        self.__border_len = config.BORDER_LEN
        self.__grid_size = config.GRID_SIZE
        self.__screen_width, self.__screen_height = config.WIDTH, config.HEIGHT
        self.__panel_width = config.PANEL_WIDTH
        self.__background = pygame.image.load(config.OTHER_IMAGE_PATHS.get('background'))
        self.__scene_image = config.SCENE_IMAGE_PATHS
        self.__other_image = config.OTHER_IMAGE_PATHS
        self.__player_tank_image = config.PLAYER_TANK_IMAGE_PATHS
        self.__bullet_image = config.BULLET_IMAGE_PATHS
        self.__enemy_tank_image = config.ENEMY_TANK_IMAGE_PATHS
        self.__food_image = config.FOOD_IMAGE_PATHS
        self.__home_image = config.HOME_IMAGE_PATHS
        self.__font = pygame.font.Font(config.FONTPATH, config.HEIGHT // 30)

    def _init_level(self):
        self.__scene_elems = {
            'brick_group': pygame.sprite.Group(),
            'iron_group': pygame.sprite.Group(),
            'ice_group': pygame.sprite.Group(),
            'river_group': pygame.sprite.Group(),
            'tree_group': pygame.sprite.Group()
        }

        self.__level = self._getGameInstance().getLevel()
        self.__level_file = self._getGameConfig().getLevelFile()
        self.__load_level_file()

    def _draw_interface(self):
        screen = self._getGameScreen()
        screen.fill((0, 0, 0))
        screen.blit(self.__background, (0, 0))
        self._draw_panel()

    def _main_loop(self):
        clock = pygame.time.Clock()
        # 该关卡通过与否的flags
        is_win = False
        is_running = True
        # 游戏主循环
        player_tanks_group = pygame.sprite.Group()
        enemy_tanks_group = pygame.sprite.Group()
        player_bullets_group = pygame.sprite.Group()
        enemy_bullets_group = pygame.sprite.Group()
        foods_group = pygame.sprite.Group()

        while is_running:

            # 用户事件捕捉
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._draw_interface()

    def show(self):
        self._init_level()

    def _draw_panel(self):
        color_white = (255, 255, 255)
        screen = self._getGameScreen()
        tank_player2 = None

        text_tips = {
            16: {'text': 'Life: %s' % 1},
            17: {'text': 'TLevel: %s' % 2},
            # 16: {'text': 'Life: %s' % tank_player1.num_lifes},
            # 17: {'text': 'TLevel: %s' % tank_player1.tanklevel},
            23: {'text': 'Game Level: %s' % self.__level},
            24: {'text': 'Remain Enemy: %s' % self.total_enemy_num}
        }
        if tank_player2:
            text_tips[20] = {'text': 'Life: %s' % 1}
            text_tips[21] = {'text': 'TLevel: %s' % 2}
            # text_tips[20] = {'text': 'Life: %s' % tank_player2.num_lifes}
            # text_tips[21] = {'text': 'TLevel: %s' % tank_player2.tanklevel}
        else:
            text_tips[20] = {'text': 'Life: %s' % None}
            text_tips[21] = {'text': 'TLevel: %s' % None}

        for pos, tip in text_tips.items():
            tip['render'] = self.__font.render(tip['text'], True, color_white)
            tip['rect'] = tip['render'].get_rect()
            tip['rect'].left, tip['rect'].top = self.__screen_width + 5, self.__screen_height * pos / 30

        for pos, tip in self.__fix_text_tips.items():
            screen.blit(tip['render'], tip['rect'])

        for pos, tip in text_tips.items():
            screen.blit(tip['render'], tip['rect'])

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

    def __load_level_file(self):
        f = open(self.__level_file, errors='ignore')
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
                self.home_position = (self.__border_len + self.home_position[0] * self.__grid_size,
                                      self.__border_len + self.home_position[1] * self.__grid_size)
            # 大本营周围位置
            elif line.startswith('%HOMEAROUNDPOS'):
                self.home_around_positions = line.split(':')[-1]
                self.home_around_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in
                                              self.home_around_positions.split(' ')]
                self.home_around_positions = [
                    (self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for
                    pos in self.home_around_positions]
            # 我方坦克初始位置
            elif line.startswith('%PLAYERTANKPOS'):
                self.player_tank_positions = line.split(':')[-1]
                self.player_tank_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in
                                              self.player_tank_positions.split(' ')]
                self.player_tank_positions = [
                    (self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for
                    pos in self.player_tank_positions]
            # 敌方坦克初始位置
            elif line.startswith('%ENEMYTANKPOS'):
                self.enemy_tank_positions = line.split(':')[-1]
                self.enemy_tank_positions = [[int(pos.split(',')[0]), int(pos.split(',')[1])] for pos in
                                             self.enemy_tank_positions.split(' ')]
                self.enemy_tank_positions = [
                    (self.__border_len + pos[0] * self.__grid_size, self.__border_len + pos[1] * self.__grid_size) for
                    pos in self.enemy_tank_positions]
            # 地图元素
            else:
                num_row += 1
                for num_col, elem in enumerate(line.split(' ')):
                    position = self.__border_len + num_col * self.__grid_size, self.__border_len + num_row * self.__grid_size
                    if elem == 'B':
                        self.__scene_elems['brick_group'].add(Brick(position, self.__scene_image.get('brick')))
                    elif elem == 'I':
                        self.__scene_elems['iron_group'].add(Iron(position, self.__scene_image.get('iron')))
                    elif elem == 'R':
                        self.__scene_elems['river_group'].add(
                            River(position, self.__scene_image.get(random.choice(['river1', 'river2']))))
                    elif elem == 'C':
                        self.__scene_elems['ice_group'].add(Ice(position, self.__scene_image.get('ice')))
                    elif elem == 'T':
                        self.__scene_elems['tree_group'].add(Tree(position, self.__scene_image.get('tree')))