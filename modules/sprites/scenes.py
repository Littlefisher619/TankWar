import pygame


class Brick(pygame.sprite.Sprite):
    # 砖墙
    def __init__(self, position, imagefile, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position


class Iron(pygame.sprite.Sprite):
    # 铁墙
    def __init__(self, position, imagefile, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position


class Ice(pygame.sprite.Sprite):
    # 冰
    def __init__(self, position, imagefile, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((24, 24))
        for i in range(2):
            for j in range(2):
                self.image.blit(pygame.image.load(imagefile), (12 * i, 12 * j))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position


class River(pygame.sprite.Sprite):
    # 河流
    def __init__(self, position, imagefile, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((24, 24))
        for i in range(2):
            for j in range(2):
                self.image.blit(pygame.image.load(imagefile), (12 * i, 12 * j))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position


class Tree(pygame.sprite.Sprite):
    # 树
    def __init__(self, position, imagepath, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((24, 24))
        for i in range(2):
            for j in range(2):
                self.image.blit(pygame.image.load(imagepath), (12 * i, 12 * j))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
