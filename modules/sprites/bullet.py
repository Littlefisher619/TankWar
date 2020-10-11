
import pygame

'''子弹'''


class Bullet(pygame.sprite.Sprite):

    def __init__(self, direction, position, config, tank, enhanced=False, speed=8):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(config.BULLET_IMAGE_PATHS.get(direction.value))
        self.width, self.height = config.WIDTH, config.HEIGHT
        self.border_len = config.BORDER_LEN
        self.direction = direction
        self.rect = self.image.get_rect()
        self.position = self.rect.center = position
        self.tank = tank

        # 地图边缘宽度

        # 是否为加强版子弹(加强版可碎铁墙)
        self.enhanced = enhanced
        # 子弹速度
        self.speed = speed

    def move(self):
        # 移动子弹, 若子弹越界, 则返回True, 否则为False
        self.rect = self.rect.move(self.direction.value[0] * self.speed, self.direction.value[1] * self.speed)
        return (self.rect.top < self.border_len) or (self.rect.bottom > self.height) or (
                    self.rect.left < self.border_len) or (self.rect.right > self.width)

    def kill(self):
        if not self.tank.infinity_bullet:
            self.tank.bullet_count -= 1

        super().kill()