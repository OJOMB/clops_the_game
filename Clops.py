#Credits to Skorpio for the artwork
#https://opengameart.org/users/skorpio?page=1

import random
import math
import pygame as pg
import os
from pygame.locals import *
import numpy as np

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
grey = (220,220,220)
dark_grey = (105,105,105)

width = 1200
height = 900
half_width, half_height = width/2, height/2
area = width * height

pg.init()
pg.mixer.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((width, height), HWSURFACE | DOUBLEBUF | RESIZABLE)
pg.display.set_caption("gamebro")
fps = 30

#SET UP ASSET DIRECTORIES
game_dir = os.path.dirname(__file__)
img_dir = os.path.join(game_dir, "img")
wav_dir = os.path.join(game_dir, "wav")
font_dir = os.path.join(game_dir, "font")

#LOAD ALL GAME GRAPHICS
#menu
menu_nebula = pg.image.load(os.path.join(img_dir, "menu", "menu_nebula.png")).convert_alpha()

#player images
player_names = ["Oscar", "Dan", "Rob", "Joe", "Allej", "Theo"]
player_imgs = {}
player_mini_imgs = {}
player_lives_imgs = {}
for name in player_names:
    player_imgs[name] = pg.image.load(os.path.join(img_dir,"player", "{}.png".format(name))).convert_alpha()
    mini_width = int(player_imgs[name].get_rect().width * 0.8)
    mini_height = int(player_imgs[name].get_rect().height * 0.8)
    player_mini_imgs[name] = pg.transform.scale(player_imgs[name], (mini_width,mini_height))
    lives_width = int(player_imgs[name].get_rect().width * 0.2)
    lives_height = int(player_imgs[name].get_rect().height * 0.2)
    player_lives_imgs[name] = pg.transform.scale(player_imgs[name], (lives_width,lives_height))

#enemy ships
alien_scout = pg.image.load(os.path.join(img_dir, "enemies", "Alien-Scout.png")).convert_alpha()
alien_cruiser = pg.image.load(os.path.join(img_dir, "enemies", "Alien-Cruiser.png")).convert_alpha()
alien_bomber = pg.image.load(os.path.join(img_dir, "enemies", "Alien-Bomber.png")).convert_alpha()
level_1_aliens = [alien_scout,alien_cruiser,alien_bomber]

#asteroids
asteroids_large = pg.image.load(os.path.join(img_dir, "asteroids", "asteroids_large.png")).convert_alpha()
asteroids_med = pg.image.load(os.path.join(img_dir, "asteroids", "asteroids_medium.png")).convert_alpha()
asteroids_small = pg.image.load(os.path.join(img_dir, "asteroids", "asteroids_small.png")).convert_alpha()
asteroids = {"small":asteroids_small, "medium":asteroids_med, 
             "large":asteroids_large}

#background
stars = pg.image.load(os.path.join(img_dir, "background", "stars.png")).convert_alpha()
stars_rect = stars.get_rect()
stars_copy = stars.copy()
nebulae = {}
for i in range(1,4):
    nebulae[i] = pg.image.load(os.path.join(img_dir, "background",  "Nebula{}.png".format(i))).convert_alpha()

#fx
warp_ss = pg.image.load(os.path.join(img_dir, "FX", "warp_effect.png")).convert_alpha()
player_missile = pg.image.load(os.path.join(img_dir, "FX", "Human-Missile.png")).convert_alpha()

#explosions
l1_enemy_explosion = pg.image.load(os.path.join(img_dir, "explosions", "enemy_explosion.png")).convert_alpha()
asteroid_explosion = {}
asteroid_explosion_ex = {}
for size in ["small","medium","large"]:
    asteroid_explosion[size] = pg.image.load(os.path.join(img_dir, "explosions", "asteroid_explosion_{}.png".format(size))).convert_alpha()
    asteroid_explosion_ex[size] = pg.image.load(os.path.join(img_dir, "explosions", "asteroid_explosion_e_{}.png".format(size))).convert_alpha()
asteroid_explosive_ss = {True:asteroid_explosion_ex, False:asteroid_explosion}

player_explosion = {}
for i in range(1,18):
    player_explosion[i] = pg.image.load(os.path.join(img_dir, "player_explosion", "{}.png".format(i))).convert()

#powerups
powerup_imgs = {}
powerup_names = ['repair', 'coin', 'life', 'rapid_fire', 'missile']
for name in powerup_names:
    powerup_imgs[name] = pg.image.load(os.path.join(img_dir, "powerups", "{}.png".format(name))).convert_alpha()

#controls
keys = ["up", "down", "left", "right", "w", "a", "d", "space"]
controls = {}
for key in keys:
    controls[key] = pg.image.load(os.path.join(img_dir, "controls", "{}.png".format(key))).convert()

#LOAD ALL GAME SOUNDS
player_shoot_sound = pg.mixer.Sound(os.path.join(wav_dir, 'laser_shoot_23_player.wav'))
enemy_shoot_sound = pg.mixer.Sound(os.path.join(wav_dir, 'laser_shoot_23_enemy.wav'))
explosion_1 = pg.mixer.Sound(os.path.join(wav_dir, 'explosion_9.wav'))
explosion_2 = pg.mixer.Sound(os.path.join(wav_dir, 'explosion_9_1.wav'))
explosion_3 = pg.mixer.Sound(os.path.join(wav_dir, 'explosion_9_2.wav'))
dead_sound = pg.mixer.Sound(os.path.join(wav_dir, 'Zap_LongShot_2.wav'))

pg.mixer.music.load(os.path.join(wav_dir, "stellar_awakening.ogg"))
pg.mixer.music.set_volume(0.3)

enemy_explosion_wavs = [explosion_1,explosion_2,explosion_3]

def spawn_l1_mob(mob_number):
    for i in range(mob_number):       
        mob = LevelOneMob()
        mobs.add(mob)
        all_sprites.add(mob)

def draw_text(surface, text, font, size, x, y, colour=white):
    font = pg.font.Font(os.path.join(font_dir, font), size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surface.blit(text_surface, text_rect)

def draw_button(surface,rect,text=None,font=None, colour=(255,255,255)):
    if colour == (255,255,255):
        grey = (220,220,220)
        dark_grey = (105,105,105)
        surface.fill(colour, rect=rect)
        pg.draw.rect(surface, dark_grey, rect, 5)
        inner_rect = (rect[0]+5,rect[1]+5,rect[2]-10,rect[3]-10)
        pg.draw.rect(surface, grey, inner_rect, 5)
        if text:
            x = inner_rect[0] + int(inner_rect[2]/2)
            y = inner_rect[1]
            size = int(inner_rect[3] * 0.65)
            draw_text(surface, text, font, size, x, y ,colour=black)

def draw_shield_bar(surface, x, y, shield_level):
    if shield_level <0:
        shield_level = 0
    bar_length = 100
    bar_height = 10
    fill = (shield_level/100) * bar_length
    outline_rect = pg.Rect(x,y, bar_length, bar_height)
    fill_rect = pg.Rect(x,y,fill,bar_height)
    pg.draw.rect(surface, green, fill_rect)
    pg.draw.rect(surface, white, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def game_over_screen():
    """
    displays game over screen and reinitialise on RETURN keyup event
    """
    draw_text(screen, "Game Over", "NeuePixelSans.ttf", 90, width/2, height/2 - 200)
    draw_text(screen, "Press Enter to restart", "NeuePixelSans.ttf", 45, width/2, height/2)
    draw_text(screen, "Press Esc to Return to Main Menu", "NeuePixelSans.ttf", 45, width/2, height/2 + 50)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYUP:
                if event.key == K_RETURN:
                    waiting = False
                    re_init = True
                    re_init_counter = 0
                    player.reinit()
                    return False, True
                if event.key == K_ESCAPE:
                    for group in all_groups:
                        group.empty()
                    menu = True
                    return True, False

def choose_pilot_screen():
    """
    displays screen where user can select a pilot to play as
    """
    placement_x = 90
    for name in player_names:
        rotator = Rotator(name,(placement_x,350))
        all_sprites.add(rotator)
        placement_x += 200
    placement_x = 10
    button_rects = {}
    for name in player_names:
        button_rects[name] = pg.rect.Rect(placement_x, 500, 190, 120)
        placement_x += 200 
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYUP:
                if event.key == K_ESCAPE:
                    waiting = False
                    all_sprites.empty()
                    return "Oscar"
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for k, v in button_rects.items():
                    if v.collidepoint(mouse_pos):
                        pilot = k
                        all_sprites.empty()
                        return pilot
                    
        all_sprites.update()
        screen.fill(black)
        draw_text(screen, "Choose Your Guy", "NeuePixelSans.ttf", 90, width/2 - 6, 100, colour=dark_grey)
        draw_text(screen, "Choose Your Guy", "NeuePixelSans.ttf", 90, width/2 - 3, 100, colour=grey)
        draw_text(screen, "Choose Your Guy", "NeuePixelSans.ttf", 90, width/2, 100)
        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2 - 6, 700, colour=dark_grey)
        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2 - 3, 700, colour=grey)
        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2, 700)
        #draw buttons for players
        for k, v in button_rects.items():
            draw_button(screen, v, text=k, font="NeuePixelSans.ttf")
        all_sprites.draw(screen)
        #draw moving rectangle animations
        for sprite in all_sprites:
            pg.draw.rect(screen, dark_grey, sprite.rect, 2)
        pg.display.flip()

def controls_screen():
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYUP:
                if event.key == K_ESCAPE:
                    waiting = False
        screen.fill(black)
        draw_text(screen, "Controls", "NeuePixelSans.ttf", 90, width/2 - 6, 100, colour=dark_grey)
        draw_text(screen, "Controls", "NeuePixelSans.ttf", 90, width/2 - 3, 100, colour=grey)
        draw_text(screen, "Controls", "NeuePixelSans.ttf", 90, width/2, 100)
        screen.blit(controls["up"], (220,220))
        screen.blit(controls["left"], (100,335))
        screen.blit(controls["down"], (220,335))
        screen.blit(controls["right"], (340,335))
        draw_text(screen, "Move Spaceship", "NeuePixelSans.ttf", 50, width/2 + 100, 375)
        screen.blit(controls["w"], (100,500))
        draw_text(screen, "Shoot Laser", "NeuePixelSans.ttf", 50, 400, 520)
        screen.blit(controls["space"], (620,500))
        draw_text(screen, "Shoot Missiles", "NeuePixelSans.ttf", 50, 950, 520)
        screen.blit(controls["a"], (100,640))
        screen.blit(controls["d"], (220,640))
        draw_text(screen, "Strafe Left and Right", "NeuePixelSans.ttf", 50, 620, 670)

        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2 - 6, 800, colour=dark_grey)
        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2 - 3, 800, colour=grey)
        draw_text(screen, "(Press Esc to Return to Menu)", "NeuePixelSans.ttf", 70, width/2, 800)
        pg.display.flip()

class Player(pg.sprite.Sprite):
    def __init__(self, pilot):
        pg.sprite.Sprite.__init__(self)
        self.pilot = pilot
        self.image = player_imgs[pilot]
        self.rect = self.image.get_rect()
        self.rect.center = (width/2,height - 85)
        self.lives = 3
        self.shield = 100
        self.score = 0
        self.missiles = 6
        self.coins = 0
        self.rapid_fire = False
        self.rapid_fire_timer = pg.time.get_ticks()
        self.shoot_delay = 225
        self.hidden = False
        self.hide_timer = 0
        self.hide_counter = 0
        self.last_shot  = pg.time.get_ticks()

    def reinit(self):
        """
        reinitialises player attributes on game over
        """
        self.lives = 3
        self.shield = 100
        self.score = 0
        self.missiles = 6
        self.coins = 0    

    def shoot(self):
        """
        shoots regular lasers
        """
        now = pg.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx,self.rect.top)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            bullets.add(bullet)
            player_shoot_sound.play()

    def shoot_missiles(self):
        """
        shoots right and left missiles
        """
        now = pg.time.get_ticks()
        if (now - self.last_shot >= self.shoot_delay) and self.missiles > 0:
            self.last_shot = now
            lmissile = LeftMissile(player)
            all_sprites.add(lmissile)
            player_bullets.add(lmissile)
            bullets.add(lmissile)
            rmissile = RightMissile(player)
            all_sprites.add(rmissile)
            player_bullets.add(rmissile)
            bullets.add(rmissile)
            self.missiles -= 2
            player_shoot_sound.play()

    def hide(self):
        """
        hides player off-screen
        """
        self.hide_timer = pg.time.get_ticks()
        self.hidden = True
        self.rect.center = (-width,height + 200)

    def powerup(self,powerup):
        """"
        implements powerups depending on powerup type
        """
        if powerup.selection == "coin":
            self.coins += 1
        elif powerup.selection == "life":
            self.lives += 1
            if self.lives > 5:
                self.lives = 5
        elif powerup.selection == "repair":
            self.shield += 50
            if self.shield > 100:
                self.shield = 100
        elif powerup.selection == "missile":
            self.missiles += 2
            if self.missiles > 8:
                self.missiles = 8
        elif powerup.selection == "rapid_fire":
            self.shoot_delay = 25
            self.rapid_fire = True
            self.rapid_fire_timer = pg.time.get_ticks()    

    def update(self):
        """
        updates to perform per gameloop
        """
        keystate = pg.key.get_pressed()
        if keystate[K_UP]:
            self.rect.y -= 5
        if keystate[K_DOWN]:
            self.rect.y += 5
        if keystate[K_RIGHT]:
            self.rect.x += 5
        if keystate[K_LEFT]:
            self.rect.x -= 5
        if keystate[K_w]:
            self.shoot()
        if keystate[K_a]:
            self.rect.x -= 10
        if keystate[K_d]:
            self.rect.x += 10
        if keystate[K_SPACE]:
            self.shoot_missiles()
        if self.rect.left > width:
            self.rect.right = 0
        if self.rect.right < 0 and not self.hidden:
            self.rect.left = width
        if self.rect.bottom > height and not self.hidden:
            self.rect.bottom = height
        if self.rect.top < 0:
            self.rect.top = 0
        if self.hidden and pg.time.get_ticks() - self.hide_timer >= 2000:
            warp = Warp()
            all_sprites.add(warp)
            if self.hide_counter == 4:
                self.rect.center = (width/2,height - 85)
                self.hide_counter = 0
                self.hidden = False
            else:    
                self.hide_counter += 1
        if self.rapid_fire and pg.time.get_ticks() - self.rapid_fire_timer >= 10000:
            self.shoot_delay = 225
            self.rapid_fire = False

class Rotator(pg.sprite.Sprite):
    def __init__(self, player_name, center):
        super().__init__()
        self.image = player_mini_imgs[player_name]
        self.image_orig = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.center = center
        self.angle = 0
        self.rad = self.rect.width / 2
        self.angle_increment = 4
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.angle = (self.angle + self.angle_increment) % 360
            new_image = pg.transform.rotate(self.image_orig, -self.angle)
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = self.center

    def update(self):
        self.rotate()

class Meteor(pg.sprite.Sprite):
    def __init__(self, cols, rows, fast=False):
        pg.sprite.Sprite.__init__(self)
        self.size = random.choice(["small","medium","large"])
        self.ssheet = asteroids[self.size]
        self.cols = cols
        self.rows = rows
        self.total_cell_count = cols * rows
        self.ssheet_rect = self.ssheet.get_rect()
        w = self.cell_width = self.ssheet_rect.width / cols
        h =self.cell_height = self.ssheet_rect.height / rows
        hw, hh = self.cell_centre = (self.cell_width/2, self.cell_height/2)
        self.cells = [(i%cols*w, i//cols*h, w, h) for i in range(self.total_cell_count)]
        self.explosive = random.choice([True,False,False])
        self.a = {False:[i for i in range(5)], True:[i for i in range(5,10)]}
        self.selection = self.a[self.explosive]
        self.surf = pg.Surface((self.cell_width, self.cell_height))
        self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[0]])
        self.image = self.surf
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, width - self.rect.width/5)
        self.rect.y = random.randrange(0 - self.rect.height/2,0)
        self.speedy = random.randrange(7,10) if fast else random.randrange(1,8)
        self.speedx = random.randrange(-5,5)
        self.counter = 1
        self.last_update = pg.time.get_ticks()

    def animate(self):
        now = pg.time.get_ticks()
        time_diff = now - self.last_update
        if time_diff >= 75:
            self.surf.fill(black)
            self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[self.counter]])
            self.image = self.surf
            self.image.set_colorkey(black)
            if self.counter == 4:
                self.counter = 0
            else:
                self.counter += 1
            self.last_update = pg.time.get_ticks()    
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.animate()
        if self.rect.top > height:
            self.kill()

class MeteorExplosion(pg.sprite.Sprite):
    def __init__(self, meteor):
        pg.sprite.Sprite.__init__(self)
        self.ssheet = asteroid_explosive_ss[meteor.explosive][meteor.size]
        self.cols = 12
        self.rows = 1
        self.total_cell_count = self.cols * self.rows
        self.ssheet_rect = self.ssheet.get_rect()
        w = self.cell_width = self.ssheet_rect.width / self.cols
        h =self.cell_height = self.ssheet_rect.height / self.rows
        hw, hh = self.cell_centre = (self.cell_width/2, self.cell_height/2)
        self.cells = [(i%self.cols*w, i//self.cols*h, w, h) for i in range(self.total_cell_count)]
        self.a = [i for i in range(12)]
        self.b = [i for i in range(5,12)]
        self.selection = self.a if meteor.a == meteor.selection else self.b
        self.surf = pg.Surface((self.cell_width, self.cell_height))
        self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[0]])
        self.image = self.surf
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = meteor.rect.x
        self.rect.y = meteor.rect.y
        self.counter = 1
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        time_diff = now - self.last_update
        if time_diff >= 75:
            self.surf.fill(black)
            self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[self.counter]])
            self.image = self.surf
            self.image.set_colorkey(black)
            if (self.selection == self.a and self.counter == 11) or (self.selection == self.b and self.counter == 6):
                self.counter = 0
                self.kill()
            else:
                self.counter += 1
            self.last_update = pg.time.get_ticks() 

class EnemyExplosion(pg.sprite.Sprite):
    def __init__(self, enemy):
        pg.sprite.Sprite.__init__(self)
        self.ssheet = l1_enemy_explosion
        self.cols = 4
        self.rows = 4
        self.total_cell_count = self.cols * self.rows
        self.ssheet_rect = self.ssheet.get_rect()
        w = self.cell_width = self.ssheet_rect.width / self.cols
        h =self.cell_height = self.ssheet_rect.height / self.rows
        hw, hh = self.cell_centre = (self.cell_width/2, self.cell_height/2)
        self.cells = [(i%self.cols*w, i//self.cols*h, w, h) for i in range(self.total_cell_count)]
        self.selection = [i for i in range(15,-1,-1)] + [i for i in range(16)]
        self.surf = pg.Surface((self.cell_width, self.cell_height))
        self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[0]])
        self.image = self.surf
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = enemy.rect.centerx
        self.rect.centery = enemy.rect.centery + 25
        self.counter = 1
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        time_diff = now - self.last_update
        if time_diff >= 25:
            self.surf.fill(black)
            self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.selection[self.counter]])
            self.image = self.surf
            self.image.set_colorkey(black)
            if (self.counter == 31):
                self.counter = 0
                self.kill()
            else:
                self.counter += 1
            self.last_update = pg.time.get_ticks() 

class PlayerExplosion(pg.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = player_explosion[1]
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.counter = 1
        self.sequence = [i for i in range(2,17)] + [i for i in range(16,0, -1)]
        self.last_update = pg.time.get_ticks()
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            self.image = player_explosion[self.sequence[self.counter]]
            self.image.set_colorkey(black)
            self.counter += 1
            if self.counter == 30:
                self.kill()
            else:
                self.counter += 1

class Warp(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.ssheet = warp_ss
        self.cols = 8 
        self.rows = 1
        self.total_cell_count = self.cols * self.rows
        self.ssheet_rect = self.ssheet.get_rect()
        w = self.cell_width = self.ssheet_rect.width / self.cols
        h =self.cell_height = self.ssheet_rect.height / self.rows
        hw, hh = self.cell_centre = (self.cell_width/2, self.cell_height/2)
        self.cells = [(i%self.cols*w, i//self.cols*h, w, h) for i in range(self.total_cell_count)]
        self.surf = pg.Surface((self.cell_width, self.cell_height))
        self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[0])
        self.image = self.surf
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = (width/2,height - 85)
        self.counter = 1
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        time_diff = now - self.last_update
        if time_diff >= 90:
            self.surf.blit(self.ssheet, (self.ssheet_rect.x , self.ssheet_rect.y), self.cells[self.counter])
            self.image = self.surf
            self.image.set_colorkey(black)
            if self.counter == 7:
                self.kill()
            else:
                self.counter += 1
            self.last_update = pg.time.get_ticks()     

class LevelOneMob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.level = 1
        self.image = random.choice(level_1_aliens)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, width - self.rect.width)
        self.rect.y = random.randrange(0 - self.rect.height*3.5,0)
        self.speedy = random.randrange(1,8)
        self.speedx = random.randrange(-5,5)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > height + 10:
            self.rect.x = random.randrange(0, width - self.rect.width)
            self.rect.y = random.randrange(0 - self.rect.height,0)
            self.speedy = random.randrange(1,8)
            self.speedx = random.randrange(1,4)
        if self.rect.centerx > (player.rect.x - 15) and self.rect.centerx < (player.rect.x + 25):
            if random.choice([True,True,True,False,False]):
                self.shoot()

    def shoot(self):
        """
        enemy pop dem bloodclart ting arf
        """
        bullet = Bullet(self.rect.centerx,self.rect.bottom, enemy=True)
        all_sprites.add(bullet)
        mob_bullets.add(bullet)
        bullets.add(bullet)
        enemy_shoot_sound.play()

class Bullet(pg.sprite.Sprite):
    def __init__(self,x,y,enemy=False):    
        pg.sprite.Sprite.__init__(self)
        self.enemy = "_enemy" if enemy else ""
        self.image = pg.image.load(os.path.join(img_dir, "FX",
                                       "muzzle_flash_1{}.png".format(self.enemy))).convert_alpha()
        self.rect = self.image.get_rect()
        self.radius = 12
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 12 if enemy else -12
        self.counter = 0

    def update(self):
        self.rect.y += self.speedy
        if self.counter == 8:
            x = self.rect.x
            y = self.rect.y
            self.image = pg.image.load(os.path.join(img_dir, "FX", "muzzle_flash_2{}.png".format(self.enemy))).convert_alpha()
            self.rect = self.image.get_rect()
            self.radius = 10
            self.rect.x = x
            self.rect.y = y
        if self.counter == 15:
            x = self.rect.x
            y = self.rect.y
            self.image = pg.image.load(os.path.join(img_dir, "FX", "muzzle_flash_3{}.png".format(self.enemy))).convert_alpha()
            self.rect = self.image.get_rect()
            self.radius = 10
            self.rect.x = x
            self.rect.y = y   
        if self.rect.bottom < 0:
            self.kill()
        self.counter += 1

class LeftMissile(pg.sprite.Sprite):
    def __init__(self, sprite):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = player_missile
        self.image = player_missile
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.left - 10
        self.rect.y = player.rect.top
        self.speed = -16
        self.counter = 0
        self.target = None
        self.parent = sprite

    def acquire_target(self):
        for mob in mobs:
            x_range = mob.rect.x < self.parent.rect.centerx
            y_range = mob.rect.y <= (self.parent.rect.top - 300)
            if x_range and y_range:
                return mob
        else:
            return None

    def update(self):
        if self.counter == 0:
            self.target = self.acquire_target()
        if self.target:
            # find normalized direction vector (dx, dy) between enemy and player
            dx, dy = self.rect.x - self.target.rect.x, self.rect.y - self.target.rect.y
            if dy and dx:
                dist = math.hypot(dx, dy)
                dx, dy = dx / dist, dy / dist
                # move along this normalized vector towards the player at current speed
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
                # rotate image to angle of trajectory
                degrees = math.degrees(math.atan2(dy,dx))
                self.image = pg.transform.rotate(self.image_orig, degrees)
            else:
                self.rect.y += self.speed
                self.taget = None
        else:
            self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
        self.counter += 1

class RightMissile(pg.sprite.Sprite):
    def __init__(self, sprite):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = player_missile
        self.image = player_missile
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.right -55
        self.rect.y = player.rect.top
        self.speed = -16
        self.counter = 0
        self.target = None
        self.parent = sprite

    def acquire_target(self):
        for mob in mobs:
            x_range = mob.rect.x > self.parent.rect.centerx
            y_range = mob.rect.y <= (self.parent.rect.top - 300)
            if x_range and y_range: 
                return mob
        else:
            return None

    def update(self):
        if self.counter == 0:
            self.target = self.acquire_target()
        if self.target:
            # find normalized direction vector (dx, dy) between enemy and player
            dx, dy = self.target.rect.x - self.rect.x, self.rect.y - self.target.rect.y
            if dy and dx:
                dist = math.hypot(dx, dy)
                dx, dy = dx / dist, dy / dist
                # move along this normalized vector towards the player at current speed
                self.rect.x += dx *  - self.speed
                self.rect.y += dy * self.speed
                # rotate image to angle of trajectory
                degrees =  360 - math.degrees(math.atan2(dy,dx))
                self.image = pg.transform.rotate(self.image_orig, degrees)
            else:
                self.rect.y += self.speed
                self.taget = None
        else:
            self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
        self.counter += 1        

class Powerup(pg.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.selection = np.random.choice(powerup_names, p=[0.3,0.3,0.1,0.1,0.2])
        self.image = powerup_imgs[self.selection]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 8

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > height:
            self.kill()

class Nebula(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = nebulae[random.choice([i for i in range(1,len(nebulae)+1)])]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, width)
        self.rect.bottom = -20
        self.speedy = 8

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > height:
            self.kill()

#INIT SPRITE GROUPS
mobs = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_bullets = pg.sprite.Group()
mob_bullets = pg.sprite.Group()
bullets = pg.sprite.Group()
meteors = pg.sprite.Group()
explosions = pg.sprite.Group()
nebulas = pg.sprite.Group()
powerups = pg.sprite.Group()
all_groups = [
              mobs, all_sprites, player_bullets, 
              mob_bullets, bullets, meteors,
              explosions, nebulas, powerups 
              ]

pilot = "Oscar"

active = True
menu = True

while active:
    #GAME MENU
    while menu:
        start_button = pg.rect.Rect(150,795,200,75)
        choose_pilot_button = pg.rect.Rect(500,795,200,75)
        controls_button = pg.rect.Rect(850,795,200,75)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    menu = False
                elif choose_pilot_button.collidepoint(mouse_pos):
                    pilot = choose_pilot_screen()
                elif controls_button.collidepoint(mouse_pos):
                    controls_screen()
                    
        screen.fill(black)
        draw_text(screen, "TFSpace","NeuePixelSans.ttf", 150, width/2 - 26, 25, colour=dark_grey)
        draw_text(screen, "TFSpace","NeuePixelSans.ttf", 150, width/2 - 23, 25, colour=grey)
        draw_text(screen, "TFSpace","NeuePixelSans.ttf", 150, width/2 - 20, 25)
        screen.blit(stars, stars_rect)
        draw_button(screen, start_button, text="Start",font="NeuePixelSans.ttf")
        draw_button(screen, choose_pilot_button, text="Pilot",font="NeuePixelSans.ttf")    
        draw_button(screen, controls_button, text="Controls",font="NeuePixelSans.ttf")
        screen.blit(menu_nebula, (100,190))
        pg.display.flip()


    #player = Player()
    warp = Warp()
    all_sprites.add(warp)

    x,y = (0,0)
    x1,y1 = (0, -stars_rect.height)

    intro = True
    start_time = pg.time.get_ticks()
    #Play background music
    pg.mixer.music.play(loops=-1)

    for i in range(20):
        meteor = Meteor(5,2)
        all_sprites.add(meteor)
        meteors.add(meteor)

    counter = 0
    #INTRO
    while intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        screen.fill(black)
        screen.blit(stars,(x,y))
        for meteor in meteors:
            if meteor.rect.y > height/2 -200:
                meteor.kill()
                explosion = MeteorExplosion(meteor)
                all_sprites.add(explosion)
        draw_text(screen, "LEVEL ONE", "PXFXshadow-3.ttf", 75, width/2, height/2)
        all_sprites.update()
        all_sprites.draw(screen)
        pg.display.flip()
        if counter == 4:
            player = Player(pilot)
            all_sprites.add(player)
        if pg.time.get_ticks() - start_time >= 7050:
            intro = False
            running = True
        counter += 1 

    #spawn mobs
    spawn_l1_mob(9)
    re_init = False
    running=True
    #MAIN GAME LOOP
    nebulae_timer = pg.time.get_ticks()
    while running:
        clock.tick(fps)
        if re_init:
            warp = Warp()
            all_sprites.add(warp)
            if re_init_counter == 3:
                player = Player(pilot)
                all_sprites.add(player)
                re_init = False

        asteroid = None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                pass

        #CHECKS WHETHER BULLET HITS MOB SPRITE
        hits = pg.sprite.groupcollide(mobs, player_bullets, True, True, pg.sprite.collide_circle)
        for hit in hits:
            player.score += 10
            random.choice(enemy_explosion_wavs).play()
            explosion = EnemyExplosion(hit)
            all_sprites.add(explosion)
            if np.random.choice([True,False], p=[0.08, 0.92]):
                powerup = Powerup(hit.rect.center)
                powerups.add(powerup)
                all_sprites.add(powerup)
            spawn_l1_mob(1)

        #CHECKS WHETHER EXPLOSION HITS MOB SPRITE
        hits = pg.sprite.groupcollide(mobs, explosions, True, True, pg.sprite.collide_circle)
        for hit in hits:
            random.choice(enemy_explosion_wavs).play()
            explosion = EnemyExplosion(hit)
            all_sprites.add(explosion)
            spawn_l1_mob(1)
        
        #CHECKS WHETHER BULLET HITS METEOR SPRITE
        hits = pg.sprite.groupcollide(meteors, bullets, True, True)
        if hits:
            for key in hits.keys():
                explosion = MeteorExplosion(key)
                all_sprites.add(explosion)
                explosions.add(explosion)

        #CHECKS WHETHER MOB HITS PLAYER
        hits = pg.sprite.spritecollide(player, mobs, True)
        if hits:
            player.shield -= 25
        for key in hits:
            explosion  = EnemyExplosion(key)
            all_sprites.add(explosion)

        #CHECKS WHETHER METEOR HITS PLAYER
        hits = pg.sprite.spritecollide(player, meteors, True)
        if hits:
            player.shield -= 25

        #CHECKS WHETHER MOB BULLET HITS PLAYER
        hits = pg.sprite.spritecollide(player, mob_bullets, True)
        if hits:
            player.shield -= 25

        #CHECKS WHETHER POWERUP HITS PLAYER
        hits = pg.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            player.powerup(hit)

        # GENERATES METEORS
        if random.choice([False] * 100 + [True]):
            meteor = Meteor(5, 2)
            all_sprites.add(meteor)
            meteors.add(meteor)

        #PLAYER HEALTH CHECKER
        if player.shield <= 0:
            dead_sound.play()
            player_explode = PlayerExplosion(player)
            all_sprites.add(player_explode)
            player.hide()
            player.lives -= 1
            player.shield = 100
        
        nebulas.update()
        all_sprites.update()

        #DRAW PART OF GAMELOOP
        screen.fill(black)
        if pg.time.get_ticks() - nebulae_timer > 15000:
            nebula = Nebula()
            all_sprites.add(nebula)
            nebulae_timer = pg.time.get_ticks()
        if y > stars_rect.height:
            y = -stars_rect.height
        if y1 > stars_rect.height:
            y1 = -stars_rect.height
        screen.blit(stars,(x,y))
        screen.blit(stars_copy,(x1,y1))
        y += 8
        y1 += 8
        if stars_rect.bottom > height:
            stars_rect.bottom = 0
        draw_text(screen, "SCORE: {}".format(str(player.score)),"NeuePixelSans.ttf", 28, width - 100, height - 100)
        draw_text(screen, "PILOT: {}".format(str(pilot)),"NeuePixelSans.ttf", 28, width - 100, 10)
        draw_shield_bar(screen, 10, 10, player.shield)
        draw_lives(screen, 120, 10, player.lives, player_lives_imgs[pilot ])
        nebulas.draw(screen)
        all_sprites.draw(screen)
        pg.display.flip()

        #if player died and resulting explosion finished
        if player.lives == 0:
            if not player_explode.alive():
                menu, running = game_over_screen()
        
pg.quit()


