from settings import *
from tilemap import collide_hit_rect
from random import uniform, choice, randint, random
import pytweening
from itertools import chain
import math
vec = pygame.math.Vector2


def collide_with_walls(sprite, group, direction):
    if direction == "x":
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if direction == "y":
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.rot_speed = None
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = "pistol"
        self.damaged = False
        self.damage_alpha = None
        self.joystick = None
        self.horiz_axis_pos_r = None
        self.vert_axis_pos_r = None
        self.angle = None

    def get_keys(self):
        my_joystick = pygame.joystick.Joystick(0)
        my_joystick.init()
        shooting = my_joystick.get_button(5)
        horiz_axis_pos = my_joystick.get_axis(0)
        vert_axis_pos = my_joystick.get_axis(1)
        self.pos.x = self.pos.x + int(horiz_axis_pos * 5)
        self.pos.y = self.pos.y + int(vert_axis_pos * 5)
        self.horiz_axis_pos_r = my_joystick.get_axis(3)
        self.vert_axis_pos_r = my_joystick.get_axis(2)
        self.angle = math.atan2(self.horiz_axis_pos_r, self.vert_axis_pos_r)
        self.angle = self.angle * (180 / math.pi)
        if shooting:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            direction = vec(1, 0).rotate(self.angle)
            pos = self.pos + BARREL_OFFSET.rotate(self.angle)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, direction.rotate(spread), WEAPONS[self.weapon]["damage"])
                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            Muzzleflash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        self.get_keys()
        self.image = pygame.transform.rotate(self.game.player_img, -self.angle)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH


class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health_bar = None
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player
        self.damaged = False
        self.damage_alpha = None

    def avoid_other_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        target_distance = self.target.pos - self.pos
        if target_distance.length_squared() < DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_distance.angle_to(vec(1, 0))
            self.image = pygame.transform.rotate(self.game.mob_img, self.rot)
            self.rect.center = self.pos
            self.acc = vec(1, .2).rotate(-self.rot)
            self.avoid_other_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

    def draw_health(self):
        if self.health > 60:
            color = GREEN
        elif self.health > 30:
            color = YELLOW
        else:
            color = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pygame.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pygame.draw.rect(self.image, color, self.health_bar)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, pos, direction, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = direction * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pygame.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pygame.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Muzzleflash(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pygame.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Item(pygame.sprite.Sprite):
    def __init__(self, game, pos, type_of_item):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type_of_item]
        self.rect = self.image.get_rect()
        self.type = type_of_item
        self.pos = pos
        self.rect.center = pos
        self.tween = pytweening.easeInOutSine
        self.step = 0
        self.direction = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.direction
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.direction *= -1
