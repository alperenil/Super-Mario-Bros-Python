# Importierte Bibliotheken
import pygame
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

    for image in images:  # Für jedes Bild in images liste
        # Ladet alle Bilder in sprite_sheet mit durchsichtigem hintergrund
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
def get_block(size):
    path = join("assets", "Terrain", "Ground_Brown.png")  # Definiert Pfad des gewünschten Blocks
    image = pygame.image.load(path).convert_alpha()  # Holt Bild aus dem Pfad und gibt durchsichtigen Hintergrund
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Erstellt Image mit der gegebenen Size
    rect = pygame.Rect(0, 0, size, size)  # Holt die richtigen Pixel aus der Bilddatei
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

    # Bewegt Spieler nach links (Für Auswirkungen von Inputs)
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    # Bewegt Spieler nach rechts (Für Auswirkungen von Inputs)
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

    # Passt Hit-box an Sprite an
    def update(self):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.mask = pygame.mask.from_surface(self.sprite)  # Sucht einzelne Pixel raus für Pixel perfekte Kollision

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
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


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
                # Setzt untere Seite vom Spieler gleich mit oberer Seite von Objekt
                player.rect.bottom = obj.rect.top + 2
                player.landed()  # Ruft Methode landed auf
            elif dy < 0:  # Prüft, ob Spieler von unten kollidiert
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
def draw(win, player, objects, offset_x):
    win.fill(BACKGROUND_COLOR)

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
