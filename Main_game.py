# sprites are gotton from "topdown shooter" art by Kenny.nl
# level 1 map is gotton from
# https://github.com/kidscancode/pygame_tutorials/blob/master/tilemap/part%2017/maps/level1.tmx
# sounds are from https://github.com/kidscancode/pygame_tutorials/tree/master/tilemap/part%2018/snd
# music is from https://github.com/kidscancode/pygame_tutorials/tree/master/tilemap/part%2018/music
# font from https://github.com/kidscancode/pygame_tutorials/blob/master/tilemap/part%2019/img/ZOMBIE.TTF
# Game over screen from https://wallpaperstock.net/game-over-poster_wallpapers_38452_1024x768_1.html
import sys
from os import path
from sprites import *
from tilemap import *


# HUB function
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 20
    fill = pct * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    if pct > 0.6:
        color = GREEN
    elif pct > 0.3:
        color = YELLOW
    else:
        color = RED
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# game class makes the whole thing run
class Game:
    def __init__(self):
        # initialize variables needed and loads data which has images
        self.player_img = None
        self.mob_img = None
        self.wall_img = None
        self.all_sprites = None
        self.walls = None
        self.mobs = None
        self.player = None
        self.camera = None
        self.playing = None
        self.dt = None
        self.map = None
        self.bullet_images = None
        self.bullets = None
        self.map_img = None
        self.map_rect = None
        self.draw_debug = None
        self.gun_puffs = None
        self.gun_flashes = None
        self.item_images = None
        self.items = None
        self.effects_sounds = None
        self.weapon_sounds = None
        self.zombie_moan_sounds = None
        self.player_hit_sounds = None
        self.zombie_hit_sounds = None
        self.splat = None
        self.paused = None
        self.title_font = None
        self.dim_screen = None
        self.hud_font = None

        # all fully caped words are from settings
        # gets time
        pygame.mixer.pre_init(44100, -16, 4, 2048)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # load all the images
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "img", "PNG", "Survivor 1")
        img_folder1 = path.join(game_folder, "img", "PNG", "Tiles")
        img_folder2 = path.join(game_folder, "img", "PNG", "Flash")
        snd_folder = path.join(game_folder, "snd")
        music_folder = path.join(game_folder, "music")
        self.title_font = path.join(img_folder2, "ZOMBIE.TTF")
        self.hud_font = path.join(img_folder2, 'Impacted2.0.ttf')
        self.dim_screen = pygame.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_img = pygame.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pygame.image.load(path.join(img_folder1, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pygame.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_img = pygame.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pygame.image.load(path.join(img_folder1, WALL_IMG)).convert_alpha()
        # transform wall size to be the same as Tile size which is 64
        self.wall_img = pygame.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pygame.image.load(path.join(img_folder2, SPLAT)).convert_alpha()
        self.splat = pygame.transform.scale(self.splat, (64, 64))
        self.gun_flashes = []
        for image in MUZZLE_FLASHES:
            self.gun_flashes.append(pygame.image.load(path.join(img_folder2, image)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pygame.image.load(path.join(img_folder1, ITEM_IMAGES[item])).convert_alpha()
        # sound loading
        pygame.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type_sound in EFFECTS_SOUNDS:
            self.effects_sounds[type_sound] = pygame.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type_sound]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pygame.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pygame.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        game_folder = path.dirname(__file__)
        self.map = TiledMap(path.join(game_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.effects_sounds["level_start"].play()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pygame.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over
        if len(self.mobs) == 0:
            self.playing = False
        # player hits item
        hits = pygame.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            # to pick up health pack
            if hit.type == "health" and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds["health_up"].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            # to pick up shotgun
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
        # mobs hit player
        hit_player = pygame.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hit_player:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hit_player:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hit_player[0].rot)
        # bullets hit mobs
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            # hit.health -= WEAPONS[self.player.weapon]["damage"] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

    def draw(self):
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pygame.draw.rect(self.screen, BLUE, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pygame.draw.rect(self.screen, BLUE, self.camera.apply_rect(wall.rect), 1)

        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE,
                       WIDTH - 10, 10, align="ne")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, CYAN, WIDTH / 2, HEIGHT / 2, align="center")
        pygame.display.flip()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                if event.key == pygame.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pygame.K_p:
                    self.paused = not self.paused

    def show_start_screen(self):
        pass

    def show_game_over_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to start", self.title_font, 75, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pygame.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.quit_game()
                if event.type == pygame.KEYUP:
                    waiting = False


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_game_over_screen()
