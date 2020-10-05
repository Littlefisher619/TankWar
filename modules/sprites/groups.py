import pygame

from modules.sprites import tanks
from modules.sprites.bullet import Bullet
from modules.sprites.foods import Foods
from modules.sprites.home import Home
from modules.sprites import SceneElement, Ice, Brick, Tree, River, Iron


class SceneElementsGroup(object):
    def __init__(self):
        self.__ice_group = pygame.sprite.Group()
        self.__iron_group = pygame.sprite.Group()
        self.__brick_group = pygame.sprite.Group()
        self.__tree_group = pygame.sprite.Group()
        self.__river_group = pygame.sprite.Group()

    @property
    def ice_group(self):
        return self.__ice_group

    @property
    def iron_group(self):
        return self.__iron_group

    @property
    def brick_group(self):
        return self.__brick_group

    @property
    def tree_group(self):
        return self.__tree_group

    @property
    def river_group(self):
        return self.__river_group

    def add(self, scene_element: SceneElement):
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

    def draw(self, screen: pygame.Surface, layer: int):
        if layer == 1:
            self.ice_group.draw(screen)
            self.river_group.draw(screen)
        elif layer == 2:
            self.brick_group.draw(screen)
            self.iron_group.draw(screen)
            self.tree_group.draw(screen)


class EntityGroup(object):
    def __init__(self):
        self.__player_tanks = pygame.sprite.Group()
        self.__enemy_tanks = pygame.sprite.Group()
        self.__player_bullets = pygame.sprite.Group()
        self.__enemy_bullets = pygame.sprite.Group()
        self.__foods = pygame.sprite.Group()

    @property
    def player_tanks(self):
        return self.__player_tanks

    @property
    def enemy_tanks(self):
        return self.__enemy_tanks

    @property
    def player_bullets(self):
        return self.__player_bullets

    @property
    def enemy_bullets(self):
        return self.__enemy_bullets

    @property
    def foods(self):
        return self.__foods

    def add(self, entity: pygame.sprite):
        if isinstance(entity, tanks.PlayerTank):
            self.player_tanks.add(entity)
        elif isinstance(entity, tanks.EnemyTank):
            self.enemy_tanks.add(entity)
        elif isinstance(entity, Foods):
            self.foods.add(entity)
        elif isinstance(entity, Bullet):
            if isinstance(entity.tank, tanks.PlayerTank):
                self.player_bullets.add(entity)
            elif isinstance(entity.tank, tanks.EnemyTank):
                self.enemy_bullets.add(entity)
        else:
            raise TypeError('Unknown Entity Type')

    def clear_enemy_tanks(self):
        self.enemy_tanks.empty()

    def remove(self, entity: pygame.sprite):
        if isinstance(entity, tanks.PlayerTank):
            self.player_tanks.remove(entity)
        elif isinstance(entity, tanks.EnemyTank):
            self.enemy_tanks.remove(entity)
        elif isinstance(entity, Foods):
            self.foods.remove(entity)
        elif isinstance(entity, Bullet):
            if isinstance(entity.tank, tanks.PlayerTank):
                self.player_bullets.remove(entity)
            elif isinstance(entity.tank, tanks.EnemyTank):
                self.enemy_bullets.remove(entity)
        else:
            raise TypeError('Unknown Entity Type')

    def draw(self, screen: pygame.Surface, layer: int):
        if layer == 1:
            self.player_bullets.draw(screen)
            self.enemy_bullets.draw(screen)
            self.player_tanks.draw(screen)
            for tank in self.player_tanks:
                tank.draw(screen)
            self.enemy_tanks.draw(screen)
        elif layer == 2:
            self.foods.draw(screen)

    def update(self, scene_elements: SceneElementsGroup, home: Home):
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
            self.remove(tank)
            remove_flag, bullet = tank.update(
                scene_elements, self.player_tanks, self.enemy_tanks, home
            )
            self.add(tank)
            if isinstance(bullet, Bullet):
                self.add(bullet)
            if remove_flag:
                self.remove(tank)
        # 更新食物
        for food in self.foods:
            if food.update():
                self.remove(food)