import pygame
import random
from .foods import Foods
from .bullet import Bullet
from enum import Enum


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


class Tank(pygame.sprite.Sprite):
    def __init__(self, game_instance):
        super().__init__()
        self.__game_instance = game_instance
        self._bullet_images = self._game_instance.config.BULLET_IMAGE_PATHS
        # 坦克轮子转动效果
        self._switch_count = 0
        self._switch_time = 1
        self._switch_pointer = False
        # 移动缓冲
        self._move_cache_time = 4
        self._move_cache_count = 0

        self._boom_image = pygame.image.load(self._game_instance.config.OTHER_IMAGE_PATHS.get('boom_static'))
        self._boom_last_time = 5
        self._boom_count = 0
        self._booming_flag = False

        # 地图边缘宽度
        # 屏幕大小
        self._border_len = self._game_instance.config.BORDER_LEN
        self._screen_size = [self._game_instance.config.WIDTH, self._game_instance.config.HEIGHT]

    @property
    def _game_instance(self):
        return self.__game_instance

    def shoot(self):
        if self._booming_flag:
            return False
        if not self._is_bullet_cooling:
            self._is_bullet_cooling = True
            position = (self.rect.centerx + self._direction.value[0], self.rect.centery + self._direction.value[1])
            bullet = Bullet(bullet_image_paths=self._bullet_images, screensize=self._screen_size,
                            direction=self._direction, position=position, border_len=self._border_len)
            configkey = self._level
            if configkey >= 2:
                configkey = 2
            bullet.speed = self._bullet_config[configkey]['_speed']
            bullet.is_stronger = self._bullet_config[configkey]['is_stronger']
            return bullet
        return False

    def decrease_level(self):
        if self._booming_flag:
            return False
        self._level -= 1
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self.set_direction(self._direction)
        self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        if self._level < 0:
            self._booming_flag = True
        return True if self._level < 0 else False

    '''设置坦克方向'''

    def set_direction(self, direction):
        self._direction = direction
        if self._direction == DIRECTION.UP:
            self._tank_direction_image = self._tank_image.subsurface((0, 0), (96, 48))
        elif self._direction == DIRECTION.DOWN:
            self._tank_direction_image = self._tank_image.subsurface((0, 48), (96, 48))
        elif self._direction == DIRECTION.LEFT:
            self._tank_direction_image = self._tank_image.subsurface((0, 96), (96, 48))
        elif self._direction == DIRECTION.RIGHT:
            self._tank_direction_image = self._tank_image.subsurface((0, 144), (96, 48))


'''玩家坦克类'''


class PlayerTank(Tank):
    def __init__(self, name, position, game_instance, **kwargs):
        super().__init__(game_instance=game_instance)
        self._level_images = game_instance.config.PLAYER_TANK_IMAGE_PATHS.get(name)
        self._bullet_config = {
            0: {
                '_speed': 8,
                'is_stronger': False
            },
            1: {
                '_speed': 10,
                'is_stronger': False
            },
            2: {
                '_speed': 10,
                'is_stronger': True
            }
        }
        # 玩家1/玩家2
        self.name = name
        # 初始坦克方向
        self.__init_direction = DIRECTION.UP
        # 初始位置
        self.__init_position = position
        # 子弹图片
        # 保护罩图片路径
        self.__protected_mask = pygame.image.load(game_instance.config.OTHER_IMAGE_PATHS.get('protect'))
        self.__protected_mask_flash_time = 25
        self.__protected_mask_flash_count = 0
        self.__protected_mask_pointer = False
        # 坦克生命数量
        self.num_lifes = 3
        # 重置
        self.__reborn()

    '''移动'''

    def move(self, direction, scene_elems, player_tanks_group, enemy_tanks_group, home):
        # 爆炸时无法移动
        if self._booming_flag:
            return
        # 方向不一致先改变方向
        if self._direction != direction:
            self.set_direction(direction)
            self._switch_count = self._switch_time
            self._move_cache_count = self._move_cache_time
        # 移动(使用缓冲)
        self._move_cache_count += 1
        if self._move_cache_count < self._move_cache_time:
            return
        self._move_cache_count = 0
        speed = (self._direction.value[0] * self._speed, self._direction.value[1] * self._speed)
        rect_ori = self.rect
        self.rect = self.rect.move(speed)
        # --碰到场景元素
        for key, value in scene_elems.items():
            if key in ['brick_group', 'iron_group', 'river_group']:
                if pygame.sprite.spritecollide(self, value, False, None):
                    self.rect = rect_ori
            elif key in ['ice_group']:
                if pygame.sprite.spritecollide(self, value, False, None):
                    self.rect = self.rect.move(speed)
        # --碰到其他玩家坦克
        if pygame.sprite.spritecollide(self, player_tanks_group, False, None):
            self.rect = rect_ori
        # --碰到敌方坦克
        if pygame.sprite.spritecollide(self, enemy_tanks_group, False, None):
            self.rect = rect_ori
        # --碰到玩家大本营
        if pygame.sprite.collide_rect(self, home):
            self.rect = rect_ori
        # --碰到边界
        if self.rect.left < self._border_len:
            self.rect.left = self._border_len
        elif self.rect.right > self._screen_size[0] - self._border_len:
            self.rect.right = self._screen_size[0] - self._border_len
        elif self.rect.top < self._border_len:
            self.rect.top = self._border_len
        elif self.rect.bottom > self._screen_size[1] - self._border_len:
            self.rect.bottom = self._screen_size[1] - self._border_len
        # 为了坦克轮动特效切换图片
        self._switch_count += 1
        if self._switch_count > self._switch_time:
            self._switch_count = 0
            self._switch_pointer = not self._switch_pointer
            self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))

    '''更新'''

    def update(self):
        # 坦克子弹冷却更新
        if self._is_bullet_cooling:
            self._bullet_cooling_count += 1
            if self._bullet_cooling_count >= self._bullet_cooling_time:
                self._bullet_cooling_count = 0
                self._is_bullet_cooling = False
        # 无敌状态更新
        if self.is_protected:
            self.protected_count += 1
            if self.protected_count > self.protected_time:
                self.is_protected = False
                self.protected_count = 0
        # 爆炸状态更新
        if self._booming_flag:
            self.image = self._boom_image
            self._boom_count += 1
            if self._boom_count > self._boom_last_time:
                self._boom_count = 0
                self._booming_flag = False
                self.__reborn()

    '''提高坦克等级'''

    def improve_level(self):
        if self._booming_flag:
            return False
        self._level = min(self._level + 1, len(self._level_images) - 1)
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self.set_direction(self._direction)
        self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        return True

    '''降低坦克等级'''

    def decrease_level(self):
        res = super().decrease_level()

        # if self._booming_flag:
        # 	return False
        # self._level -= 1
        if self._level < 0:
            self.num_lifes -= 1

        # self._booming_flag = True
        # else:
        # 	self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        # 	self.set_direction(self._direction)
        # 	self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        # return True if self._level < 0 else False
        return res

    '''增加生命值'''

    def add_life(self):
        self.num_lifes += 1

    '''设置为无敌状态'''

    def set_protected(self):
        self.is_protected = True

    '''画我方坦克'''

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.is_protected:
            self.__protected_mask_flash_count += 1
            if self.__protected_mask_flash_count > self.__protected_mask_flash_time:
                self.__protected_mask_pointer = not self.__protected_mask_pointer
                self.__protected_mask_flash_count = 0
            screen.blit(self.__protected_mask.subsurface((48 * self.__protected_mask_pointer, 0), (48, 48)), self.rect)

    '''重置坦克, 重生的时候用'''

    def __reborn(self):
        # 坦克方向
        self._direction = self.__init_direction
        # 移动缓冲, 用于避免坦克连续运行不方便调整位置
        self._move_cache_time = 4
        self._move_cache_count = 0
        # 是否无敌状态
        self.is_protected = False
        self.protected_time = 1500
        self.protected_count = 0
        # 坦克移动速度
        self._speed = 8
        # 子弹冷却时间
        self._bullet_cooling_time = 30
        self._bullet_cooling_count = 0
        self._is_bullet_cooling = False
        # 坦克等级
        self._level = 0
        # 坦克轮子转动效果

        # 坦克图片
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self.set_direction(self._direction)
        self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.__init_position


'''敌方坦克类'''


class EnemyTank(Tank):
    def __init__(self, position, game_instance, **kwargs):
        super().__init__(game_instance=game_instance)
        level_images = game_instance.config.ENEMY_TANK_IMAGE_PATHS
        self.tanktype = random.choice(list(level_images.keys()))
        self._level_images = level_images.get(self.tanktype)

        self._bullet_config = {
            0: {
                '_speed': 8,
                'is_stronger': False
            },
            1: {
                '_speed': 10,
                'is_stronger': False
            },
            2: {
                '_speed': 10,
                'is_stronger': False
            }
        }

        # 坦克出场特效
        appear_image = pygame.image.load(game_instance.config.OTHER_IMAGE_PATHS.get('appear')).convert_alpha()
        self.__appear_images = [appear_image.subsurface((0, 0), (48, 48)), appear_image.subsurface((48, 0), (48, 48)),
                                appear_image.subsurface((96, 0), (48, 48))]
        # 坦克类型

        # 坦克等级
        self._level = random.randint(0, len(self._level_images) - 2)
        self.food = None

        if (random.random() >= 0.6) and (self._level == len(self._level_images) - 2):
            self._level += 1
            self.food = Foods(food_image_paths=game_instance.config.FOOD_IMAGE_PATHS, screensize=self._screen_size)

        # 坦克图片路径
        self._tank_image = pygame.image.load(self._level_images[self._level]).convert_alpha()
        self._direction = DIRECTION.random()
        self.set_direction(self._direction)
        self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.image = self.__appear_images[0]
        # 坦克爆炸图

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
        # 坦克移动速度
        self._speed = 10 - int(self.tanktype) * 2

    '''实时更新坦克'''

    def update(self, scene_elems, player_tanks_group, enemy_tanks_group, home):
        data_return = dict()
        # 死后爆炸
        if self._booming_flag:
            self.image = self._boom_image
            self._boom_count += 1
            data_return['boomed'] = False
            if self._boom_count > self._boom_last_time:
                self._boom_count = 0
                self._booming_flag = False
                data_return['boomed'] = True
            return data_return
        # 禁止行动时不更新
        if self.is_keep_still:
            self.keep_still_count += 1
            if self.keep_still_count > self.keep_still_time:
                self.is_keep_still = False
                self.keep_still_count = 0
            return data_return
        # 播放出生特效
        if self._is_borning:
            self._borning_left_time -= 1
            if self._borning_left_time < 0:
                self._is_borning = False
            elif self._borning_left_time <= 10:
                self.image = self.__appear_images[2]
            elif self._borning_left_time <= 20:
                self.image = self.__appear_images[1]
            elif self._borning_left_time <= 30:
                self.image = self.__appear_images[0]
            elif self._borning_left_time <= 40:
                self.image = self.__appear_images[2]
            elif self._borning_left_time <= 50:
                self.image = self.__appear_images[1]
            elif self._borning_left_time <= 60:
                self.image = self.__appear_images[0]
            elif self._borning_left_time <= 70:
                self.image = self.__appear_images[2]
            elif self._borning_left_time <= 80:
                self.image = self.__appear_images[1]
            elif self._borning_left_time <= 90:
                self.image = self.__appear_images[0]
        # 出生后实时更新
        else:
            # --坦克移动
            self.move(scene_elems, player_tanks_group, enemy_tanks_group, home)
            # --坦克子弹冷却更新
            if self._is_bullet_cooling:
                self._bullet_cooling_count += 1
                if self._bullet_cooling_count >= self._bullet_cooling_time:
                    self._bullet_cooling_count = 0
                    self._is_bullet_cooling = False
            # --能射击就射击
            data_return['bullet'] = self.shoot()
        return data_return

    def random_change_direction(self, exclude_current_direction=False):
        list = DIRECTION.list()
        if exclude_current_direction:
            list.remove(self._direction)

        self.set_direction(random.choice(list))
        self._switch_count = self._switch_time
        self._move_cache_count = self._move_cache_time


    '''随机移动坦克'''
    def move(self, scene_elems, player_tanks_group, enemy_tanks_group, home):
        # 移动(使用缓冲)
        self._move_cache_count += 1
        if self._move_cache_count < self._move_cache_time:
            return
        self._move_cache_count = 0
        speed = (self._speed * self._direction.value[0], self._speed * self._direction.value[1])
        rect_ori = self.rect
        self.rect = self.rect.move(speed)
        # --碰到场景元素

        for key, value in scene_elems.items():
            if key in ['brick_group', 'iron_group', 'river_group']:
                if pygame.sprite.spritecollide(self, value, False, None):
                    self.rect = rect_ori
                    self.random_change_direction(True)
            elif key in ['ice_group']:
                if pygame.sprite.spritecollide(self, value, False, None):
                    self.rect = self.rect.move(speed)

        # --碰到玩家坦克/其他敌方坦克/玩家大本营
        if pygame.sprite.spritecollide(self, player_tanks_group, False, None) or \
           pygame.sprite.spritecollide(self, enemy_tanks_group, False, None) or \
           pygame.sprite.collide_rect(self, home):
            self.rect = rect_ori
            self.random_change_direction()

        # --碰到边界
        if self.rect.left < self._border_len:
            self.random_change_direction(True)
            self.rect.left = self._border_len
        elif self.rect.right > self._screen_size[0] - self._border_len:
            self.random_change_direction(True)
            self.rect.right = self._screen_size[0] - self._border_len
        elif self.rect.top < self._border_len:
            self.random_change_direction(True)
            self.rect.top = self._border_len
        elif self.rect.bottom > self._screen_size[1] - self._border_len:
            self.random_change_direction(True)
            self.rect.bottom = self._screen_size[1] - self._border_len

        # 为了坦克轮动特效切换图片
        self._switch_count += 1
        if self._switch_count > self._switch_time:
            self._switch_count = 0
            self._switch_pointer = not self._switch_pointer
            self.image = self._tank_direction_image.subsurface((48 * int(self._switch_pointer), 0), (48, 48))


    def set_still(self):
        self.is_keep_still = True
