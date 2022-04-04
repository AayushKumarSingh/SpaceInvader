from json import load
from json.decoder import JSONDecodeError
from math import ceil, floor
from random import randint
import pygame
from pygame.image import load as load_img
from pygame.transform import scale as scale_img, smoothscale
from pygame.font import Font
from pygame.display import get_window_size, set_mode, set_caption, set_icon, update
from pygame.time import wait


class Invader:

    def __init__(self, sprite, scale=(100, 100), speed=0.002):
        self.player_sprite = scale_img(load_img(sprite), scale)
        self.window_size = get_window_size()
        self.rect = self.player_sprite.get_rect()
        self.rect.x = self.window_size[0] * 0.48
        self.rect.y = self.window_size[1] * 0.9
        self.speed = ceil(speed * self.window_size[0])
        self.scale = scale
        self.change_x = 0
        self.change_y = 0
        self.firing: bool = False
        self.event_tuple = (
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d)

    def player_boundary(self):
        if self.rect.x <= 0:
            self.rect.x = 0
        if self.rect.x >= self.window_size[0] - self.scale[0]:
            self.rect.x = self.window_size[0] - self.scale[0]
        if self.rect.y <= 0:
            self.rect.y = 0
        if self.rect.y >= self.window_size[1] - self.scale[1]:
            self.rect.y = self.window_size[1] - self.scale[1]

    def player_movement(self):
        global screen, resolution, running, resolution_bg
        self.firing = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f:
                    screen = set_mode(resolution, pygame.FULLSCREEN, vsync=1)
                if event.key == pygame.K_ESCAPE:
                    screen = set_mode(resolution, pygame.RESIZABLE, vsync=1)

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.change_x = -self.speed
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.change_x = self.speed
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.change_y = -self.speed
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.change_y = self.speed
                if event.key == pygame.K_SPACE:
                    self.firing = True

            if event.type == pygame.KEYUP:
                if event.key in self.event_tuple:
                    self.change_x = 0
                    self.change_y = 0

        self.rect.x += self.change_x
        self.rect.y += self.change_y

        self.player_boundary()
        self.render()
        self.resize()

    def resize(self):
        current_window_size = get_window_size()

        if current_window_size != self.window_size:
            print(current_window_size, self.window_size, sep="\t\t", end="\n\n")
            self.rect.x = ceil((self.rect.x / self.window_size[0]) * current_window_size[0])
            self.rect.y = ceil((self.rect.y / self.window_size[1]) * current_window_size[1])
            self.speed = abs(ceil((self.speed / self.window_size[0]) * current_window_size[0]))
            self.window_size = current_window_size

    def render(self):
        global screen
        screen.blit(self.player_sprite, (self.rect.x, self.rect.y))


class Enemy:

    def __init__(self, sprite, scale=(75, 75), speed=0.0003, respawn=10):
        self.enemy_sprite = scale_img(load_img(sprite), scale)
        self.window_size = get_window_size()
        self.scale = scale
        self.rect = self.enemy_sprite.get_rect()
        self.rect.x = randint(0, self.window_size[0] - 100)
        self.rect.y = randint(0, floor(0.24 * self.window_size[1]))
        self.change = ceil(speed * self.window_size[0])
        self.killed = False
        self.respawn_count = 0
        self.respawn_time = respawn
        self.displacement = ceil(0.1 * self.window_size[1])

    def enemy_movement(self):
        global screen, resolution

        if self.rect.x >= self.window_size[0] - self.scale[0] or self.rect.x <= 0:
            self.rect.y += self.displacement
            self.change = -self.change

        self.rect.x += self.change

        if not self.killed:
            self.render()
            self.resize()

        if self.killed:
            self.rect.x = -100
            self.rect.y = -100
            self.respawn_count += 1
            self.respawn()

    def render(self):
        global screen
        screen.blit(self.enemy_sprite, (self.rect.x, self.rect.y))

    def enemy_wins(self, players: Invader):
        global running, player_killed
        if self.rect.colliderect(players.rect):
            running = False
            player_killed = True

    def resize(self):
        current_window_size = get_window_size()

        if current_window_size != self.window_size:
            self.rect.x = floor((self.rect.x / self.window_size[0]) * current_window_size[0])
            self.rect.y = floor((self.rect.y / self.window_size[1]) * current_window_size[1])

            if self.rect.x >= current_window_size[0] - self.scale[0]:
                self.rect.x -= self.scale[0]

            self.change = ceil(0.0003 * self.window_size[0] + 0.0001 * (current_window_size[0] - self.window_size[0]))
            self.window_size = current_window_size
            self.displacement = ceil(0.1 * self.window_size[1])

    def respawn(self):
        if self.respawn_count >= self.respawn_time:
            new_x = randint(0, self.window_size[0] - self.scale[0])
            new_y = randint(0, 45)

            if (self.rect.x + 150 <= new_x < self.rect.x - 150) or (self.rect.y + 10 <= new_y < self.rect.y - 10):
                self.respawn()

            self.rect.x = new_x
            self.rect.y = new_y
            self.killed = False
            self.respawn_count = 0


class Bullet:
    def __init__(self, sprite, scale=(15, 25), speed=0.0003):
        self.bullet_sprite = scale_img(load_img(sprite), scale)
        self.window_size = get_window_size()
        self.rect = self.bullet_sprite.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.speed = ceil(speed * self.window_size[0])
        self.ready = True

    def shoot(self, player: Invader, alien: Enemy):
        if player.firing and self.ready:
            self.rect.x = self.rect.x = floor(player.rect.x + 0.85 * player.rect.w * 0.5)
            self.rect.y = player.rect.y
            self.ready = False

        if not self.ready:
            self.rect.y -= self.speed
            self.render()

        if self.rect.y <= 1:
            self.ready = True
            self.rect.x = floor(player.rect.x + 0.85 * player.rect.w * 0.5)
            self.rect.y = player.rect.y
        self.resize()

        if self.rect.colliderect(alien.rect):
            global score, multiplier
            score += multiplier
            alien.killed = True
            self.ready = True
            self.rect.x = self.window_size[0] + 100
            self.rect.y = self.window_size[1] + 100

    def render(self):
        global screen
        screen.blit(self.bullet_sprite, (self.rect.x, self.rect.y))

    def resize(self):
        current_window_size = get_window_size()
        if current_window_size != self.window_size:
            self.rect.x = ceil((self.rect.x / self.window_size[0]) * current_window_size[0])
            self.rect.y = ceil((self.rect.y / self.window_size[1]) * current_window_size[1])
            self.window_size = current_window_size
            self.speed = abs(ceil((self.speed / self.window_size[0]) * current_window_size[0]
                                  + 0.0005 * self.speed * (current_window_size[0] - self.window_size[0])))


try:
    with open("config.json") as file:
        config = load(file)

        res: list = config["Resolution"]

        setup = config["setup"]
        ship = config["Invader"]
        enemy = config["Alien"]
        bullet = config["Bullet"]
        multiplier = int(config["score multiplier"])

        enemy_no = int(setup["no_of_enemies"])
        style = str(setup["style"])
        color = str(setup["color"])
        size = int(setup["size"])
        icon_loc = str(setup["icon"])
        bg_img_loc = str(setup["background_img"])
        fullscreen = bool(setup["Start_on_fullscreen"])
        delay = int(setup["Manual_wait"])
        capt = str(setup["caption"])

except JSONDecodeError:
    print("Error Occurred while parsing json")

except ValueError:
    print("Wrong Values initialized in json file")

except FileNotFoundError:
    print("File doesn't exists")

pygame.init()
no_of_enemy = enemy_no
resolution = res
resolution_max = (2160, 1080)

if fullscreen:
    screen = set_mode(resolution, pygame.FULLSCREEN, vsync=1)
else:
    screen = set_mode(resolution, pygame.RESIZABLE, vsync=1)

score: int = 0
font = Font(style, size)

pygame.mouse.set_visible(False)

set_caption(capt)
set_icon(load_img(icon_loc))

background_img, pos = load_img(bg_img_loc), (0, 0)
resolution_bg = resolution_max
background_img = smoothscale(background_img, resolution_bg)

running: bool = True
player_killed: bool = False

player = Invader(ship["img"], ship["scale"], ship["speed"])
alien = [Enemy(enemy["img"], enemy["scale"], enemy["speed"], enemy["respawn time"]) for _ in range(no_of_enemy)]
laser = Bullet(bullet["img"], bullet["scale"], bullet["speed"])

while running:
    text = font.render(f"Score : {score}", True, "White")
    screen.blit(background_img, pos)

    player.player_movement()
    for enemy in range(no_of_enemy):
        alien[enemy].enemy_movement()
        alien[enemy].enemy_wins(player)
        laser.shoot(player, alien[enemy])
        alien[enemy].enemy_movement()
    wait(delay)
    screen.blit(text, (1, 1))
    update()

resolution = get_window_size()

while player_killed:
    text = font.render(f"Game Over", True, "White")
    screen.blit(text, (0.4 * resolution[0], 0.42 * resolution[1]))
    update()
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            exit()
