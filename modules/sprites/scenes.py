import pygame


class SceneElement(pygame.sprite.Sprite):
    def __init__(self, position, imagefile, blitimage=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        if blitimage:
            self.image = pygame.Surface((24, 24))
            for i in range(2):
                for j in range(2):
                    self.image.blit(pygame.image.load(imagefile), (12 * i, 12 * j))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position


class Brick(SceneElement):
    # 砖墙
    pass


class Iron(SceneElement):
    # 铁墙
    pass


class Ice(SceneElement):
    # 冰
    def __init__(self, position, imagefile):
        super().__init__(position, imagefile, True)


class River(SceneElement):
    # 河流
    def __init__(self, position, imagefile):
        super().__init__(position, imagefile, True)


class Tree(SceneElement):
    # 树
    def __init__(self, position, imagefile):
        super().__init__(position, imagefile, True)


class SceneFactory(object):
    BRICK = 'brick'
    IRON = 'iron'
    RIVER_1 = 'river1'
    RIVER_2 = 'river2'
    ICE = 'ice'
    SCENE_MAPS = {
        BRICK: Brick,
        IRON: Iron,
        RIVER_1: River,
        RIVER_2: River,
        ICE: Ice,
    }

    def __init__(self, game_config):
        self.__scene_images = game_config.SCENE_IMAGE_PATHS

    def create_element(self, position, element_type):
        return SceneFactory.SCENE_MAPS[element_type](position, self.__scene_images.get(element_type))

