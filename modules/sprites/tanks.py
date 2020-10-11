import pygame
import random

from modules.TankGame import TankGame
from modules.sprites import groups

from modules.sprites.foods import Foods
from modules.sprites.bullet import Bullet
from enum import Enum
from pygame.sprite import spritecollide




class DIRECTION(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @classmethod
    def list(cls):
        return [DIRECTION.UP, DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT]

    @classmethod
    def random(cls):
        return random.choice([DIRECTION.UP, DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT])


class COLLISION:
    WITH_TANK = 0b00001
    WITH_HOME = 0b00010
    WITH_BORDER = 0b00100
    WITH_SCENE_ELEMENTS = 0b01000


class Tank(pygame.sprite.Sprite):
    def __init__(self, game_config):
        super().__init__()
        self.__game_config = game_config
        # 坦克轮子转动效果
        self._switch_count = 0
        self._switch_time = 1
        self._switch_pointer = False
        # 移动缓冲
        self._move_cache_time = 4
        self._move_cache_count = 0
        # 爆炸
        self._boom_last_time = 5
        self._boom_count = 0
        self._booming_flag = False

        self._level = 0
        self._speed = 8
        # 地图边缘宽度/屏幕大小
        self._border_len = game_config.BORDER_LEN
        self._screen_size = [game_config.WIDTH, game_config.HEIGHT]
        self._init_resources()

        self.bullet_count = 0
        self._is_bullet_cooling = False
        self._bullet_config = {
            0: {
                'speed': 8,
                'enhanced': False
            },
            1: {
                'speed': 10,
                'enhanced': False
            },
            2: {
                'speed': 10,
                'enhanced': True
            },
            'count': 1,
            'infinity': False
        }

    @property
    def infinity_bullet(self):
        return self._bullet_config['infinity']

    @property
    def bullet_limit(self):
        return self._bullet_config['count']

    @property
    def _game_config(self):
        return self.__game_config

    def shoot(self):
        if self._booming_flag:
            return False
        if not self._is_bullet_cooling:
            if not self.infinity_bullet:
                if self.bullet_count >= self.bullet_limit:
                    return False
                else:
                    self.bullet_count += 1

            self._is_bullet_cooling = True
            position = (self.rect.centerx + self._direction.value[0], self.rect.centery + self._direction.value[1])
            bullet = Bullet(direction=self._direction, position=position, tank=self, config=self._game_config)
            configkey = self._level
            if configkey >= 2:
                configkey = 2
            bullet.speed = self._bullet_config[configkey]['speed']
            bullet.enhanced = self._bullet_config[configkey]['enhanced']
            return bullet

        return False

    @property
    def image(self):
        if self._booming_flag:
            return self._boom_image
        return self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))

    def decrease_level(self):
        if self._booming_flag:
            return False
        self._level -= 1
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self._update_direction(self._direction)
        # self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        if self._level < 0:
            self._booming_flag = True
        return True if self._level < 0 else False

    '''设置坦克方向'''
    def _update_direction(self, direction):
        self._direction = direction
        if self._direction == DIRECTION.UP:
            self._tank_direction_image = self._tank_image.subsurface((0, 0), (96, 48))
        elif self._direction == DIRECTION.DOWN:
            self._tank_direction_image = self._tank_image.subsurface((0, 48), (96, 48))
        elif self._direction == DIRECTION.LEFT:
            self._tank_direction_image = self._tank_image.subsurface((0, 96), (96, 48))
        elif self._direction == DIRECTION.RIGHT:
            self._tank_direction_image = self._tank_image.subsurface((0, 144), (96, 48))

    def _init_resources(self):
        config = self._game_config
        self._bullet_images = config.BULLET_IMAGE_PATHS
        self._boom_image = pygame.image.load(config.OTHER_IMAGE_PATHS.get('boom_static'))
        pass

    def roll(self):
        # 为了坦克轮动特效切换图片
        self._switch_count += 1
        if self._switch_count > self._switch_time:
            self._switch_count = 0
            self._switch_pointer = not self._switch_pointer

    def move(self, direction, scene_elems, player_tanks_group, enemy_tanks_group, home):
        # 爆炸时无法移动
        if self._booming_flag:
            return
        # 方向不一致先改变方向
        if self._direction != direction:
            self._update_direction(direction)
            self._switch_count = self._switch_time
            self._move_cache_count = self._move_cache_time
        # 移动(使用缓冲)
        self._move_cache_count += 1
        if self._move_cache_count < self._move_cache_time:
            return
        self._move_cache_count = 0

        new_position = (self._direction.value[0] * self._speed, self._direction.value[1] * self._speed)
        old_rect = self.rect
        self.rect = self.rect.move(new_position)
        # --碰到场景元素
        collisons = 0
        cannot_passthrough = [scene_elems.brick_group, scene_elems.iron_group, scene_elems.river_group]
        for i in cannot_passthrough:
            if spritecollide(self, i, False, None):
                self.rect = old_rect
                collisons |= COLLISION.WITH_SCENE_ELEMENTS



        # --碰到其他玩家坦克/碰到敌方坦克
        if spritecollide(self, player_tanks_group, False, None) or spritecollide(self, enemy_tanks_group, False, None):
            collisons |= COLLISION.WITH_TANK
            self.rect = old_rect

        # --碰到玩家大本营
        if pygame.sprite.collide_rect(self, home):
            collisons |= COLLISION.WITH_HOME
            self.rect = old_rect

        # --碰到边界
        if self.rect.left < self._border_len:
            self.rect.left = self._border_len
            collisons |= COLLISION.WITH_BORDER
        elif self.rect.right > self._screen_size[0] - self._border_len:
            collisons |= COLLISION.WITH_BORDER
            self.rect.right = self._screen_size[0] - self._border_len
        elif self.rect.top < self._border_len:
            collisons |= COLLISION.WITH_BORDER
            self.rect.top = self._border_len
        elif self.rect.bottom > self._screen_size[1] - self._border_len:
            collisons |= COLLISION.WITH_BORDER
            self.rect.bottom = self._screen_size[1] - self._border_len

        if collisons == 0 and spritecollide(self, scene_elems.ice_group, False, None):
            self.rect = self.rect.move(new_position)

        return collisons


class PlayerTank(Tank):
    def __init__(self, name, position, game_config, **kwargs):
        super().__init__(game_config=game_config)
        self._level_images = self._game_config.PLAYER_TANK_IMAGE_PATHS.get(name)

        # 玩家1/玩家2
        self.name = name
        # 初始坦克方向
        self.__init_direction = DIRECTION.UP
        # 初始位置
        self.__init_position = position
        # 保护罩
        self.__protected = False
        self.__protected_mask_flash_time = 25
        self.__protected_mask_flash_count = 0
        self.__protected_mask_pointer = False
        # 坦克生命数量
        self.health = 3
        # 重置
        self.__reborn()

    def _init_resources(self):
        super()._init_resources()
        # 保护罩
        self.__protected_mask = pygame.image.load(self._game_config.OTHER_IMAGE_PATHS.get('protect'))

    def update(self):
        # 坦克子弹冷却更新
        if self._is_bullet_cooling:
            self._bullet_cooling_count += 1
            if self._bullet_cooling_count >= self._bullet_cooling_time:
                self._bullet_cooling_count = 0
                self._is_bullet_cooling = False
        # 无敌状态更新
        if self.protected:
            self.__protected_count += 1
            if self.__protected_count > self.__protected_time:
                self.protected = False
                self.__protected_count = 0
        # 爆炸状态更新
        if self._booming_flag:
            self._boom_count += 1
            if self._boom_count > self._boom_last_time:
                self._boom_count = 0
                self._booming_flag = False
                self.__reborn()

    def improve_level(self):
        # 提高坦克等级
        if self._booming_flag:
            return False
        self._level = min(self._level + 1, len(self._level_images) - 1)
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self._update_direction(self._direction)
        return True

    def decrease_level(self):
        # 降低坦克等级
        res = super().decrease_level()
        if self._level < 0:
            self.health -= 1

        return res

    def add_health(self):
        # 增加生命值
        self.health += 1

    @property
    def protected(self):
        return self.__protected

    @protected.setter
    def protected(self, protected):
        self.__protected = protected

    def draw(self, screen):
        # 画我方坦克
        screen.blit(self.image, self.rect)
        if self.protected:
            self.__protected_mask_flash_count += 1
            if self.__protected_mask_flash_count > self.__protected_mask_flash_time:
                self.__protected_mask_pointer = not self.__protected_mask_pointer
                self.__protected_mask_flash_count = 0
            screen.blit(self.__protected_mask.subsurface((48 * self.__protected_mask_pointer, 0), (48, 48)), self.rect)

    def __reborn(self):
        # 重置坦克, 重生的时候用

        # 移动缓冲, 用于避免坦克连续运行不方便调整位置
        self._move_cache_time = 4
        self._move_cache_count = 0
        # 是否无敌状态
        self.protected = False
        self.__protected_time = 1500
        self.__protected_count = 0
        # 坦克移动速度
        self._speed = 8
        # 子弹冷却时间
        self._bullet_cooling_time = 30
        self._bullet_cooling_count = 0
        self._is_bullet_cooling = False
        # 坦克等级
        self._level = 0

        # 坦克图片
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self._update_direction(self.__init_direction)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.__init_position


'''敌方坦克类'''


class EnemyTank(Tank):
    def __init__(self, position, game_config, **kwargs):
        super().__init__(game_config=game_config)
        enemy_level_images = self._game_config.ENEMY_TANK_IMAGE_PATHS
        self.__tank_type =  random.choices(['0', '1', '2'], weights=[10, 10, TankGame().level+10])[0]#random.choice(list(enemy_level_images.keys()))
        self._level_images = enemy_level_images.get(self.__tank_type)
        self._bullet_config[2]['enhanced'] = False

        self._level = int(self.__tank_type) #random.randint(0, len(self._level_images) - 2)
        # 子弹冷却时间
        self._bullet_cooling_time = 120 - self._level * 10
        self._bullet_cooling_count = 0
        self._is_bullet_cooling = False
        # 用于给刚生成的坦克播放出生特效
        self._is_borning = True
        self._borning_left_time = 90
        # 坦克是否可以行动(玩家坦克捡到食物clock可以触发为True)
        self.is_keep_still = False
        self.keep_still_time = 500
        self.keep_still_count = 0

        # 坦克移动速度，等级越高速度越低
        self._speed = 10 - self._level * 3

        self.__food = None
        # 坦克出场特效
        appear_image = pygame.image.load(self._game_config.OTHER_IMAGE_PATHS.get('appear')).convert_alpha()
        self.__appear_images = [
            appear_image.subsurface((0, 0), (48, 48)),
            appear_image.subsurface((48, 0), (48, 48)),
            appear_image.subsurface((96, 0), (48, 48))
        ]
        if random.random() <= 0.3 * self._level:
        # if (random.random() >= 0.6) and (self._level == len(self._level_images) - 2):
            # self._level += 1
            self.__food = Foods(food_image_paths=self._game_config.FOOD_IMAGE_PATHS, screensize=self._screen_size)

        # 坦克图片路径
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self._direction = DIRECTION.random()
        self._update_direction(self._direction)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        # 坦克爆炸图

    @property
    def food(self):
        return self.__food

    def clear_food(self):
        self.__food = None

    @property
    def image(self):
        if self._is_borning:
            return self.__appear_images[(90 - self._borning_left_time // 10) % 3]
        return super().image

    def update(self, scene_elems, player_tanks_group, enemy_tanks_group, home):
        # 死后爆炸
        remove_flag = False
        bullet = None
        if self._booming_flag:

            self._boom_count += 1
            if self._boom_count > self._boom_last_time:
                self._boom_count = 0
                self._booming_flag = False
                remove_flag = True
            return remove_flag, bullet

        # 禁止行动时不更新
        if self.is_keep_still:
            self.keep_still_count += 1
            if self.keep_still_count > self.keep_still_time:
                self.is_keep_still = False
                self.keep_still_count = 0
            return remove_flag, bullet

        # 播放出生特效
        if self._is_borning:
            self._borning_left_time -= 1
            if self._borning_left_time < 0:
                self._is_borning = False
        # 出生后实时更新
        else:
            # --坦克移动
            self.move(self._direction, scene_elems, player_tanks_group, enemy_tanks_group, home)
            self.roll()
            # --坦克子弹冷却更新
            if self._is_bullet_cooling:
                self._bullet_cooling_count += 1
                if self._bullet_cooling_count >= self._bullet_cooling_time:
                    self._bullet_cooling_count = 0
                    self._is_bullet_cooling = False
            # --能射击就射击
            bullet = self.shoot()
        return remove_flag, bullet

    def random_change_direction(self, exclude_current_direction=False):
        list = DIRECTION.list()
        if exclude_current_direction:
            list.remove(self._direction)

        self._update_direction(random.choice(list))
        self._switch_count = self._switch_time
        self._move_cache_count = self._move_cache_time

    def move(self, direction, scene_elems, player_tanks_group, enemy_tanks_group, home):
        # 遇到障碍物考虑改变方向
        collisions = super().move(direction, scene_elems, player_tanks_group, enemy_tanks_group, home)
        if collisions is None or collisions == 0:
            return

        change_direction = False
        if collisions & COLLISION.WITH_SCENE_ELEMENTS & COLLISION.WITH_BORDER:
            change_direction = True
        self.random_change_direction(change_direction)

    def set_still(self):
        self.is_keep_still = True


class TankFactory(object):
    ENEMY_TANK = 0
    PLAYER1_TANK = 1
    PLAYER2_TANK = 2

    def __init__(self, config):
        self.__game_config = config

    def create_tank(self, position, tank_type):
        if tank_type == TankFactory.ENEMY_TANK:
            return EnemyTank(position=position, game_config=self.__game_config)
        elif tank_type == TankFactory.PLAYER1_TANK:
            return PlayerTank(name='player1', position=position, game_config=self.__game_config)
        elif tank_type == TankFactory.PLAYER2_TANK:
            return PlayerTank(name='player2', position=position, game_config=self.__game_config)

