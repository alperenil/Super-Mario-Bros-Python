# Importierte Bibliotheken
import pygame
# import random
# import math
from os import listdir
from os.path import isfile, join

# initialisiert pygame
pygame.init()

# Definiert Fensternamen
pygame.display.set_caption("Mario Bros")

'''
Globale Variablen
'''
BACKGROUND_COLOR = 84, 140, 255
WINDOW_WIDTH, WINDOW_HEIGHT = 512, 512
FPS = 60
PLAYER_VEL = 6
GRAVITY = 1
ANIMATION_DELAY = 3

# Definiert Fenster in Variable window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

'''
Klassen, Methoden und Funktionen
'''


# Funktion dreht alle Sprites in X Richtung
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Funktion holt gewünschte Sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)  # Variable für den Pfad des gewünschten Sprites
    images = [f for f in listdir(path) if isfile(join(path, f))]  # Liste enthält alle Bilder aus dem Pfad

    all_sprites = {}

    for image in images:  # Für jedes Bild in images Array
        # Ladet alle Bilder in sprite_sheet Variable mit durchsichtigem hintergrund
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []

        # Teilt Bilder mit mehreren Sprites in einzelne Bilder auf
        for i in range(sprite_sheet.get_width() // width):  # Teilt Bilder auf
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  # Definiert grösse von einzelnen Bildern
            rect = pygame.Rect(i * width, 0, width, height)  # setzt grösse rect fest für die einzelnen Bilder
            surface.blit(sprite_sheet, (0, 0), rect)  # Zeichnet die einzelnen Bilder
            sprites.append(pygame.transform.scale2x(surface))  # Skaliert einzelne Bilder

        # Wenn eine Richtung gegeben ist, wird hier das ".png" aus dem Namen entfernt und die Richtung als suffix
        # angefügt. Schliesslich werden die Sprites je nach Richtung umgedreht und in die Variable hinzugefügt.
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    # Gibt die Gedrehten und umbenannten Sprites wieder zurück
    return all_sprites


# Funktion holt gewünschten Block
def get_block(x_image, y_image, size):
    path = join("assets", "Terrain", "Block.png")  # Definiert Pfad des gewünschten Blocks
    image = pygame.image.load(path).convert_alpha()  # Holt Bild aus dem Pfad und gibt durchsichtigen Hintergrund
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Erstellt Image mit der gegebenen Size
    rect = pygame.Rect(x_image, y_image, size, size)  # Holt die richtigen Pixel aus der Bilddatei
    surface.blit(image, (0, 0), rect)  # Zeichnet Block
    return pygame.transform.scale2x(surface)  # Skaliert Block


# Klasse für den Spieler
class Player(pygame.sprite.Sprite):
    # Ruft Funktion auf, um Charakter Sprites zu holen
    SPRITES = load_sprite_sheets("MainCharacters", "Mario", 32, 32, True)

    # Initialisierung des Spielers
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)  # Grösse und position des Spielers
        self.x_vel = 0  # Geschwindigkeit x-Achse
        self.y_vel = 0  # Geschwindigkeit y-Achse
        self.mask = None  # Maske für kollisionserkennung
        self.direction = "right"  # Richtung, in die der Spieler aktuell schaut
        self.animation_count = 0  # Counter für animationen
        self.fall_count = 0  # Counter für Fallzeit
        self.jump_count = 0  # Counter für Anzahl Sprünge

    # Methode sorgt für Sprung
    def jump(self):
        self.y_vel = -GRAVITY * 8  # Gibt Geschwindigkeit nach oben (Dynamisch mit Gravitation)
        self.animation_count = 0  # Setzt animations counter zurück
        self.jump_count += 1  # zähl Sprünge hoch
        if self.jump_count == 1:
            self.fall_count = 0

    # Methode bewegt Spieler (Für Gravitation und Kollisionserkennung)
    def move(self, dx, dy):
        self.rect.x += dx  # Bewegt Spieler in x Richtung
        self.rect.y += dy  # Bewegt Spieler in y Richtung

        # Setzt Sprung-counter zurück, wenn Spielen nicht am Boden ist
        if self.y_vel >= 1:
            self.jump_count = 1

    # Bewegt Spieler nach links (Für Auswirkungen von Inputs)
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":  # if Clause, damit Animationen nur zurückgesetzt werden, wenn man sich dreht
            self.direction = "left"
            self.animation_count = 0

    # Bewegt Spieler nach rechts (Für Auswirkungen von Inputs)
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":  # if Clause, damit Animationen nur zurückgesetzt werden, wenn man sich dreht
            self.direction = "right"
            self.animation_count = 0

    # Macht alles, was in jedem frame geprüft wird
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * GRAVITY)  # Gravitation * Sekunden = Fallgeschwindigkeit
        self.move(self.x_vel, self.y_vel)  # Bewegt Spieler in die Richtung seiner Geschwindigkeit

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

    # Passt Hit-box an Sprite an
    def update(self):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.mask = pygame.mask.from_surface(self.sprite)  # Sucht einzelne Pixel raus für Pixel perfekte Kollision

    # Zeichnet Spieler
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# Klasse für die Gegner
class Enemy(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height


# Child Class für Goomba Gegner
class Goomba(Enemy):
    # Ruft Funktion auf, um Charakter Sprites zu holen
    SPRITES = load_sprite_sheets("Enemies", "Goomba", 32, 32, True)

    def __init__(self, x, y):
        super().__init__(50, 50)
        self.rect = pygame.Rect(x, y, 50, 50)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0

    # Methode bewegt Gegner (Für Gravitation und Kollisionserkennung)
    def move(self, dx, dy):
        self.rect.x += dx  # Bewegt Gegner in x Richtung
        self.rect.y += dy  # Bewegt Gegner in y Richtung

    # Macht alles, was in jedem frame geprüft wird
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * GRAVITY)  # Gravitation * Sekunden = Fallgeschwindigkeit
        self.move(self.x_vel, self.y_vel) # Bewegt Spieler in die Richtung seiner Geschwindigkeit

        self.fall_count += 1  # Zählt bei jedem Frame hoch
        self.update_sprite()

    # Setzt Sprite
    def update_sprite(self):
        sprite_sheet = "walk"

        # Ändert Sprite nach SPRITE_DELAY
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # Passt Hit-box an Sprite an
    def update(self):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.mask = pygame.mask.from_surface(self.sprite)  # Sucht einzelne Pixel raus für Pixel perfekte Kollision

    # Zeichnet Goomba
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
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Klasse für Blöcke
class Block(Object):  # Child class von Object
    def __init__(self, x_image, y_image, x, y, width, height):
        super().__init__(x, y, width, height)
        block = get_block(x_image, y_image, width)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# Vertikale Kollision zwischen Spieler und objects
def handle_vertical_collision(player, objects, player_dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Kollision wird hier für alle Objekte berechnet mithilfe der maske
            if player_dy > 0:  # Prüft, ob Spieler von oben kollidiert
                # Setzt untere Seite vom Spieler gleich mit oberer Seite von Objekt
                player.rect.bottom = obj.rect.top + 2
                player.landed()  # Ruft Methode landed auf
            elif player_dy < 0:  # Prüft, ob Spieler von unten kollidiert
                # Setzt obere Seite vom Spieler gleich mit unterer Seite von Objekt
                player.rect.top = obj.rect.bottom - 2
                player.hit_head()  # Ruft Methode hit_head auf

        collided_objects.append(obj)  # Fügt Objekt zu collided_objects hinzu

    return collided_objects.append(obj)  # Gibt kollidierte Objekte zurück


# Prüft, ob Spieler kollidieren würde, wenn es sich horizontal bewegt
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()  # Updated Masken
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Setzt Collided object, wenn kollision entdeckt wird
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
def draw(win, player, objects, enemies, offset_x):
    win.fill(BACKGROUND_COLOR)  # Füllt Hintergrund mit Hintergrundfarbe

    for obj in objects:
        obj.draw(window, offset_x)  # Zeichnet alle objekte

    for enemy in enemies:
        enemy.draw(window, offset_x)  # Zeichnet alle Gegner

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

    # Erstellt Goomba
    goomba = Goomba(200, 200)

    # Setzt gegner in eine Liste
    enemies = [goomba]

    # Erstellt Rohre
    pipe_1 = [Block(0, 16, (32 * 29), WINDOW_HEIGHT - block_size * 4, 64, 64)]
    pipe_2 = [Block(0, 16, (32 * 39), WINDOW_HEIGHT - block_size * 5, 64, 96)]
    pipe_3 = [Block(0, 16, (32 * 47), WINDOW_HEIGHT - block_size * 6, 64, 128)]
    pipe_4 = [Block(0, 16, (32 * 58), WINDOW_HEIGHT - block_size * 6, 64, 128)]
    pipe_5 = [Block(0, 16, (32 * 164), WINDOW_HEIGHT - block_size * 4, 64, 64)]
    pipe_6 = [Block(0, 16, (32 * 180), WINDOW_HEIGHT - block_size * 4, 64, 64)]
    pipes = [*pipe_1, *pipe_2, *pipe_3, *pipe_4, *pipe_5, *pipe_6]

    # Erstellt Boden
    ground_1 = [Block(0, 0, i * block_size, WINDOW_HEIGHT - m * block_size, block_size, block_size)
                for i in range(-WINDOW_WIDTH // block_size, (32 * 70) // block_size)
                for m in range(1, 3)]
    ground_2 = [Block(0, 0, i * block_size, WINDOW_HEIGHT - m * block_size, block_size, block_size)
                for i in range((32 * 72) // block_size, (32 * 87) // block_size)
                for m in range(1, 3)]
    ground_3 = [Block(0, 0, i * block_size, WINDOW_HEIGHT - m * block_size, block_size, block_size)
                for i in range((32 * 89) // block_size, (32 * 154) // block_size)
                for m in range(1, 3)]
    ground_4 = [Block(0, 0, i * block_size, WINDOW_HEIGHT - m * block_size, block_size, block_size)
                for i in range((32 * 156) // block_size, (32 * 226) // block_size)
                for m in range(1, 3)]
    grounds = [*ground_1, *ground_2, *ground_3, *ground_4]

    # Erstellt Pyramiden
    pyramid = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 3 * block_size, block_size, block_size)
               for i in range((32 * 135) // block_size, ((32 * 136) + (32 * 3)) // block_size)]
    pyramid_1 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 4 * block_size, block_size, block_size)
                 for i in range(((32 * 135) + (32 * 1)) // block_size, ((32 * 136) + (32 * 3)) // block_size)]
    pyramid_2 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 5 * block_size, block_size, block_size)
                 for i in range(((32 * 135) + (32 * 2)) // block_size, ((32 * 136) + (32 * 3)) // block_size)]
    pyramid_3 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 6 * block_size, block_size, block_size)
                 for i in range(((32 * 135) + (32 * 3)) // block_size, ((32 * 136) + (32 * 3)) // block_size)]

    pyramid_4 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 3 * block_size, block_size, block_size)
                 for i in range((32 * 141) // block_size, ((32 * 142) + (32 * 3)) // block_size)]
    pyramid_5 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 4 * block_size, block_size, block_size)
                 for i in range(((32 * 141) + (32 * 0)) // block_size, ((32 * 142) + (32 * 2)) // block_size)]
    pyramid_6 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 5 * block_size, block_size, block_size)
                 for i in range(((32 * 141) + (32 * 0)) // block_size, ((32 * 142) + (32 * 1)) // block_size)]
    pyramid_7 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 6 * block_size, block_size, block_size)
                 for i in range(((32 * 141) + (32 * 0)) // block_size, ((32 * 142) + (32 * 0)) // block_size)]

    pyramid_8 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 3 * block_size, block_size, block_size)
                 for i in range((32 * 149) // block_size, ((32 * 150) + (32 * 4)) // block_size)]
    pyramid_9 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 4 * block_size, block_size, block_size)
                 for i in range(((32 * 149) + (32 * 1)) // block_size, ((32 * 150) + (32 * 4)) // block_size)]
    pyramid_10 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 5 * block_size, block_size, block_size)
                  for i in range(((32 * 149) + (32 * 2)) // block_size, ((32 * 150) + (32 * 4)) // block_size)]
    pyramid_11 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 6 * block_size, block_size, block_size)
                  for i in range(((32 * 149) + (32 * 3)) // block_size, ((32 * 150) + (32 * 4)) // block_size)]

    pyramid_12 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 3 * block_size, block_size, block_size)
                  for i in range((32 * 156) // block_size, ((32 * 157) + (32 * 3)) // block_size)]
    pyramid_13 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 4 * block_size, block_size, block_size)
                  for i in range(((32 * 156) + (32 * 0)) // block_size, ((32 * 157) + (32 * 2)) // block_size)]
    pyramid_14 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 5 * block_size, block_size, block_size)
                  for i in range(((32 * 156) + (32 * 0)) // block_size, ((32 * 157) + (32 * 1)) // block_size)]
    pyramid_15 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 6 * block_size, block_size, block_size)
                  for i in range(((32 * 156) + (32 * 0)) // block_size, ((32 * 157) + (32 * 0)) // block_size)]

    pyramid_16 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 3 * block_size, block_size, block_size)
                  for i in range((32 * 182) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_17 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 4 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 1)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_18 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 5 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 2)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_19 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 6 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 3)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_20 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 7 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 4)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_21 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 8 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 5)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_22 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 9 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 6)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]
    pyramid_23 = [Block(16, 0, i * block_size, WINDOW_HEIGHT - 10 * block_size, block_size, block_size)
                  for i in range(((32 * 182) + (32 * 7)) // block_size, ((32 * 183) + (32 * 8)) // block_size)]

    pyramids = [*pyramid, *pyramid_1, *pyramid_2, *pyramid_3, *pyramid_4, *pyramid_5, *pyramid_6, *pyramid_7,
                *pyramid_8, *pyramid_9, *pyramid_10, *pyramid_11, *pyramid_12, *pyramid_13, *pyramid_14, *pyramid_15,
                *pyramid_16, *pyramid_17, *pyramid_18, *pyramid_19, *pyramid_20, *pyramid_21, *pyramid_22, *pyramid_23]

    objects = [*grounds, *pyramids, *pipes]

    offset_x = 0  # Variable für die Kamera versetzung
    scroll_area_width = 250  # Variable definiert, wie weit man an den Rand gehen kann bevor die kamera scrollt

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

        # Funktion loopt bewegung
        player.loop(FPS)
        goomba.loop(FPS)

        handle_move(player, objects)  # Funktion holt Knopfdruck und setzt Vel
        # Ruft draw Funktion auf und gibt das Fenster + den Spieler mit
        draw(window, player, objects, enemies, offset_x)

        # Versetzt Kamera offset, je nach Spielerposition
        if (((player.rect.right - offset_x >= WINDOW_WIDTH - scroll_area_width) and player.x_vel > 0) or
                ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0)):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
