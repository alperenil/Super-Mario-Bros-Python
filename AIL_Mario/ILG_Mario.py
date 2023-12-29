# Importierte Bibliotheken
import pygame
import os
# import random
# import math
from os import listdir
from os.path import isfile, join

# initialisiert pygam
pygame.init()

# Definiert Fensternamen
pygame.display.set_caption("Mario Bros")

'''
Globale Variablen
'''
BACKGROUND_COLOR = 84, 140, 255
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 600
FPS = 60
PLAYER_VEL = 5
GRAVITY = 1
ANIMATION_DELAY = 3

# Definiert Fenster
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

'''
Klassen, Methoden und Funktionen
'''


# Funktion dreht alle Sprites in X Richtung
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Funktion ladet Sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]  # Ladet alle Files in der Directory

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  # Ladet alle Bilder

        sprites = []
        for i in range(sprite_sheet.get_width() // width):  # Teilt Bilder auf
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))  # Skaliert einzelne Bilder

        if direction:  # Nimmt .png aus den Namen und gibt nach richtung anderen Namen
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


# Holt gewünschten Block
def get_block(size):
    path = join("assets", "Terrain", "Ground_Brown.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Erstellt Image mit der gegebenen Size
    rect = pygame.Rect(0, 0, size, size)  # Holt die richtigen Pixel aus der Bilddatei
    surface.blit(image, (0, 0), rect)  # Zeichnet Block
    return pygame.transform.scale2x(surface)  # Verdoppelt Grösse


# Klasse für den Spieler
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    SPRITES = load_sprite_sheets("MainCharacters", "Mario", 32, 32, True)

    # Initialisierung des Spielers
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    # Methode sorgt für Sprung
    def jump(self):
        self.y_vel = -GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    # Move funktion für die bewegung des Spielers
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # Bewegt Spieler nach Links
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    # Bewegt Spieler nach Rechts
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Macht alles, was in jedem frame geprüft wird
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * GRAVITY)  # Gravitation * Sekunden = Fallgeschwindigkeit
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1  # Zählt bei jedem Frame hoch
        self.update_sprite()

    # Methode macht alles, was beim Landen passieren soll
    def landed(self):
        self.fall_count = 0  # Setzt Fall counter zurück
        self.y_vel = 0  # Setzt vertikale Geschwindigkeit zurück
        self.jump_count = 0  # Setzt Sprung counter zurück

    # Methode macht alles, was beim Kopf anschlagen passieren soll
    def hit_head(self):
        self.fall_count = 0
        self.y_vel *= -1

    # Ändert Sprite je nach Situation
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.y_vel < 0 or self.jump_count == 1:
            sprite_sheet = "jump"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        # Ändert Sprite nach SPRITE_DELAY
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # Passt "Hitbox" an Sprite an
    def update(self):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.mask = pygame.mask.from_surface(self.sprite)  # Sucht einzelne Pixel raus für Pixelperfekte Kollision

    # Zeichnet Spieler
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# Klasse für alle Objekte
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    # Zeichnet Objekte
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Klasse für Blöcke
class Block(Object):  # Child class von Object
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# Vertikale Kollision zwischen Spieler und objects
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Kollision wird hier für alle Objekte berechnet mithilfe der maske
            if dy > 0:  # Prüft, ob Spieler von oben kollidiert
                player.rect.bottom = obj.rect.top + 2  # Setzt untere Seite vom Spieler gleich mit oberer Seite von Objekt
                player.landed()  # Ruft Methode landed auf
            elif dy < 0:  # Prüft, ob Spieler von unten kollidiert
                player.rect.top = obj.rect.bottom - 2  # Setzt obere Seite vom Spieler gleich mit unterer Seite von Objekt
                player.hit_head()  # Ruft Methode hit_head auf

        collided_objects.append(obj)  # Fügt Objekt zu collided_objects hinzu

    return collided_objects.append(obj)  # Gibt kollidierte Objekte zurück


# Prüft, ob Spieler kollidieren würde, wenn es sich horizontal bewegt
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()  # Updated Masken
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Setzt Collided object, wenn kollision entdetckt wird
            collided_object = obj
            break

    # Setzt Spieler an seinen Platz wieder zurück
    player.move(-dx, 0)
    player.update()
    return collided_object


# Funktion ruft Beweg-Methoden bei Knopfdruck auf
def handle_move(player, objects):
    keys = pygame.key.get_pressed()  # Setzt gedrückte Taste in Keys Variable

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    player.x_vel = 0  # Spieler bleibt stehen, wenn nichts gedrückt wird
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)  # Bewegt Spieler nach links beim Drücken von a
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)  # Bewegt Spieler nach rechts beim Drücken von d

    handle_vertical_collision(player, objects, player.y_vel)


# Funktion "zeichnet" Hintergrund und Spieler bei Aufruf
def draw(window, player, objects, offset_x):
    window.fill(BACKGROUND_COLOR)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()  # Updated das Fenster kontinuierlich


'''
Main Schleife
'''


def main(window):
    clock = pygame.time.Clock()

    block_size = 32  # Variable für Blockgrösse

    # Erstellt Spieler
    player = Player(100, 100, 50, 50)
    # Erstellt Boden
    ground = [Block(i * block_size, WINDOW_HEIGHT - block_size, block_size)
              for i in range(-WINDOW_WIDTH // block_size, (WINDOW_WIDTH * 2) // block_size)]
    objects = [*ground, Block(0, WINDOW_HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, WINDOW_HEIGHT - block_size * 6, block_size)]

    offset_x = 0  # Variable für die Kamera versetzung
    scroll_area_width = 300  # Variable definiert, wie weit man an den Rand gehen kann bevor die kamera scrollt

    game_is_running = True
    while game_is_running:
        clock.tick(FPS)  # setzt spiel tick

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Schliesst Spiel, wenn man auf X klickt
                game_is_running = False
                break
            # Ruft jump Methode auf beim Drücken von Space Taste
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 1:
                    player.jump()

        player.loop(FPS)  # Funktion loopt bewegung
        handle_move(player, objects)  # Funktion holt Knopfdruck und setzt Vel
        draw(window, player, objects, offset_x)  # Ruft draw Funktion auf und gibt das Fenster + den Spieler mit

        # Versetzt Kamera offset, je nach Spielerposition
        if (((player.rect.right - offset_x >= WINDOW_WIDTH - scroll_area_width) and player.x_vel > 0) or
                ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0)):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
