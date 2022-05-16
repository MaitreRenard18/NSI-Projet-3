#Imports
from math import floor
import pygame
import random
from time import sleep
import os
import sys

#Initialisation
pygame.init()
screen = pygame.display.set_mode((1056, 832)) #Créer la fenêtre
pygame.display.set_caption('Terrario') #Renomme la fenêtre

#Chargement des textures
textures = {}
for file in os.listdir("{}\Textures".format(os.getcwd())): #Récupère toute les fichiers se trouvant dans le dossier textures
    if file.endswith(".png"): #Vérifie qu'il sagit d'un png
        file_name = file.replace(".png", "").lower() #Créer un nom en minuscule sans le png
        
        path = "{}\Textures\{}".format(os.getcwd(), file) #Récupère l'emplacement du ficher
        image = pygame.image.load(path) #Charge l'image

        textures[file_name] = image #Ajoute une l'image dans le dictionnaire texture

#Class carte
layers = {
    0: ["air"],
    1: ["grass"],
    2: ["dirt"],
    3: ["dirt", "dirt", "stone"],
    4: ["dirt", "stone"],
    5: ["stone"],
    8: ["stone" for _ in range(16)] + ["coal"], # Ici par exemple le charbon à une chance sur 17 de se générer de la coucge 8 à 11
    12: ["stone" for _ in range(32)] + ["coal", "coal", "iron"],
    64: ["stone" for _ in range(64)] + ["iron", "iron", "gold"],
    256: ["stone" for _ in range(128)] + ["gold", "gold", "diamond"],
    512: ["stone" for _ in range(128)] + ["diamond", "diamond", "ruby"]
} #Dictionaire ou les minerais et leur chance d'apparition sont stockés

class Map:
    def __init__(self, width, height): #Prend en paramètre une largeur et une hauter
        self.width = width
        self.height = height

        self.tiles = [] #Liste ou les "tuiles" sont stockées sous le format [x][y]
        self.generate() #Appelle la fonction generate qui genère la carte
    
    def generate(self):
        print("Génération des tuiles.")

        for x in range(self.width - 1):
            sys.stdout.write('\r') #Affiche la progression dans la console
            sys.stdout.write("{}%".format(floor((x / (self.width - 1)) * 100) + 1))
            sys.stdout.flush()

            self.tiles.append([]) #Ajoute un tableau dans "tiles" qui represente une colone

            for y in range(self.height): #Pour chaques lignes dans la colone, des tuiles sont générées en fonction du numéro de ligne
                keys = list(layers.keys())

                for layer_key in range(len(keys) - 1, -1, -1):
                    if y >= keys[layer_key]:
                        layer = layers[keys[layer_key]]
                        self.tiles[x].append(random.choice(layer))
                        break

        print("\nGénération des grottes.")
        for i in range(750): #Génère 750 grottes
            sys.stdout.write('\r') #Affiche la progression dans la console
            sys.stdout.write("{}%".format(floor((i / 750) * 100) + 1))
            sys.stdout.flush()

            max_size = random.randint(32, 64) #Prend une taille aléatoire en 32 et 64 tuiles
            self.dig((random.randint(0, self.width), random.randint(4, self.height)), max_size) #Appelle la fonction dig qui génère une grotte

        for x in range(self.width - 1):
            self.tiles[x][0] = "air" #Ajoute une couche d'air à la surface
            self.tiles[x][-3] = random.choice(["stone", "bedrock"]) #Génère de la "bedrock" au fond de la carte
            self.tiles[x][-2] = random.choice(["stone", "bedrock", "bedrock"])
            self.tiles[x][-1] = "bedrock"

        print("\nGénération terminée.")

    def dig(self, position, max_size, size = 0): #Prend en paramètre une position (tuple), une taille max, et une taille actuelle (Qui augmente de 1 à chaque appelle)
        x, y = position

        if size == max_size or x > len(self.tiles) - 1 or y > len(self.tiles[x]) - 1: #Si la grotte à attend sa taille max. ou que les bordure de la map ont été atteinte, arrêter la génération
            return

        size += 1 #Augmente la taille
        self.tiles[x][y] = "cave" #Met une tuille de "grotte" a l'emplacement x, y

        choises = [] #Initialise un tableau ou les possiblités d'extension de la grotte seront stocker
        if x + 1 < len(self.tiles) and self.tiles[x + 1][y] != "cave": #Verifie si la grotte peut s'éttendre à droite
            choises.append((x + 1, y))

        if x - 1 >= 0 and self.tiles[x - 1][y] != "cave": #A droite
            choises.append((x - 1, y))

        if y + 1 < len(self.tiles[x]) and self.tiles[x][y + 1] != "cave": #En bas
            choises.append((x, y + 1))

        if y - 1 >= 0 and self.tiles[x][y - 1] != "cave": #En haut
            choises.append((x, y - 1))
        
        if len(choises) == 0: #Vérifie que la grotte peut s'éttendre
            return

        branch = [1 for _ in range(9)]
        branch.append(2)
        branch = random.choice(branch) #Choisie en combien de "branches" la grotte va s'éttendre (1 chance sur 10 qu'il y ait 2 embranchements)

        for _ in range(branch): #Appelle plusieurs fois la fonction dig en fonction du nombre d'embranchements
            self.dig(random.choice(choises), max_size, size)

    def render(self, offset): #Fonction qui affiche la carte, en prennant en paramètre la position de la camera
        screen.fill((145, 226, 255)) #Met le fond en bleu pour simuler du ciel 

        screensize = screen.get_size() #Récupère la taille de l'écran pour regarder combien de tuiles peuvent être afficher en même temps
        x_tile_number = screensize[0] // 32 + (screensize[0] % 32 > 0) 
        y_tile_number = screensize[1] // 32 + (screensize[1] % 32 > 0)

        for x in range(offset[0], offset[0] + x_tile_number): #Pour chaques colones visibles sur l'écran
            for y in range(offset[1], offset[1] + y_tile_number): #Pour chaques lignes visibles sur l'écran
                x_index = None if x < 0 or x > len(self.tiles) - 1 else x #Vérifie que la colone existe
                y_index = None if y < 0 or y > len(self.tiles[0]) - 1 else y #Vérifie que la ligne existe
                
                if x_index != None and y_index != None: #Si la colone et la ligne existent
                    texture = textures[self.tiles[x_index][y_index]] #Récupère la texture dans "tiles"
                    screen.blit(pygame.transform.scale(texture, (32, 32)), (x * 32 - offset[0] * 32, y * 32 - offset[1] * 32)) #Et l'affiche sur l'écran

#Class joueur
ores_values = {
    "coal": 1,
    "iron": 2,
    "gold": 4,
    "diamond": 8,
    "ruby": 15
} #Dictionnaire contenant l'or donné pour chaque minerai

class Player:
    def __init__(self, position, map):
        self.position = position #Prend en paramètre la position du joueur 
        self.direction = ["right", (1, 0)] #Défini la direction vers laquelle le drill va

        self.speed = 1 #Le montant qui défini la vitesse du joueur, maximum 10, sinon le drill se téléporte
        self.moving_cooldown = 0
        self.falling_cooldown = 0

        self.gold = 0 #Le montant qui défini l'argent
        self.fuel_max = 50 #Le montant qui défini le fuel max, modifiable par le shop
        self.fuel = self.fuel_max #ça c'est pour définir le fuel durant le jeu
        
        self.map = map #Prend en paramètre la class map, pour avoir accès à ses informations

    def get_camera_offset(self):
        screensize = screen.get_size()
        x = floor(self.position[0]) - (screensize[0] // 32) // 2
        y = floor(self.position[1]) - (screensize[1] // 32) // 2

        return (x, y)

    def mine(self):
        x, y = self.position
        ore = self.map.tiles[x][y] #Variable qui regarde le bloc où que le joueur est en train de miner

        if ore in ores_values: #Si le joueur mine un bloc qui se trouve dans le dictionnaire des minerais
            self.gold += ores_values[ore] #Le gold augmente selon la valeur attribuée au minerai cassé

        self.map.tiles[x][y] = "cave" #De plus, on affiche une texture de cave pour préciser que le bloc est miné

    def tick(self):
        screensize = screen.get_size()

        drill_base_texture = pygame.transform.scale(textures["drill_base_{}".format(self.direction[0])], (32, 32))
        drill_base_position = (screensize[0] // 2 - 16, screensize[1] // 2)
        screen.blit(drill_base_texture, drill_base_position)

        drill_texture = pygame.transform.scale(textures["drill_{}".format(self.direction[0])], (32, 32))
        drill_position = (drill_base_position[0] + self.direction[1][0] * 32, drill_base_position[1] + self.direction[1][1] * 32)
        screen.blit(drill_texture, drill_position)

        x, y = self.position

        if not self.map.tiles[x][y] in ["scaffolding", "cave", "air"]: #si le bloc sur lequel on veut aller n'est pas un échaffaudage/une cave/de l'air
            self.mine() #Le joueur peut le miner
        
        if self.map.tiles[x][y + 1] == "cave": #Si le bloc en dessous du joueur est une cave
            parachue_texture = pygame.transform.scale(textures["parachute"], (32, 32))
            screen.blit(parachue_texture, (screensize[0] // 2 - 16, screensize[1] // 2 - 32)) #On affiche l'image de parachute au dessus du drill

            if self.falling_cooldown > 0:
                self.falling_cooldown -= .25
                return
            
            self.position = (x, self.position[1] + 1) #Le drill descend d'un bloc, pour simuler de la gravité
            self.falling_cooldown = 1

            return

        if self.moving_cooldown > 0:
            self.moving_cooldown -= self.speed * .1
            return

        if self.fuel < 0: #Si le drill ne contient plus de fuel
            self.position = (self.map.width // 2, 0) #Il revient à sa position originale
            screen.blit(textures["nofuel"], (348,348)) #On affiche la fenetre indiquant qu'il n'y a plus de fuel
            pygame.display.flip()
            sleep(2) #On attend 2 secondes que le joueur perçoit bien la fenetre
            self.fuel = self.fuel_max #On réeinitialise le fuel
            return

        keys = pygame.key.get_pressed() #On stock le touche pressée dans la variable keys
        if keys[pygame.K_RIGHT] and self.map.tiles[x + 1][y] != "bedrock": #Si la touche préssée est droite, et qu'il n'y a pas de bedrock à droite
            self.position = (x + 1, y) #La position du joueur augmente, vers la droite
            self.direction = ["right", (1, 0)] #La direction est mise vers la droite
            self.fuel -= 1 #Et on décrémente le fuel car le joueur vient de bouger

            self.moving_cooldown = 1
            return

        if keys[pygame.K_LEFT] and self.map.tiles[x - 1][y] != "bedrock": #Si la touche préssée est gauche, et qu'il n'y a pas de bedrock à gauche
            self.position = (x - 1, y) #La position du joueur diminue, pour aller à gauche
            self.direction = ["left", (-1, 0)] #La direction est mise vers la gauche
            self.fuel -= 1 #Et on décrémente le fuel car le joueur vient de bouger

            self.moving_cooldown = 1
            return

        if keys[pygame.K_UP] and self.map.tiles[x][y - 1] != "bedrock" and y > 0: #Si la touche préssée est haut, et qu'il n'y a pas de bedrock en haut
            self.position = (x, y - 1) #La position du joueur diminue, pour aller en haut
            self.direction = ["up", (0, -1)] #La direction est mise vers le haut
            self.fuel -= 1 #Et on décrémente le fuel car le joueur vient de bouger

            self.map.tiles[x][y] = "scaffolding" #En plus, on affiche la texture d'échafaudage, pour éviter que le joueur soit soumis à la gravité
            
            self.moving_cooldown = 1
            return

        if keys[pygame.K_DOWN] and self.map.tiles[x][y + 1] != "bedrock": #Si la touche préssée est bas, et qu'il n'y a pas de bedrock en dessous
            self.position = (x, y + 1) #La position du joueur augmente, pour aller en bas
            self.direction = ["down", (0, 1)] #La direction est mise vers le bas
            self.fuel -= 1 #Et on décrémente le fuel car le joueur vient de bouger

            self.moving_cooldown = 1
            return
        
#Interface
class Interface:
    def __init__(self, player): #Prend en paramètre la class Player, pour avoir accès à ses variables
        self.player = player
        
    def render(self): #La fonction qui affiche toute les textures de barres/compteurs
        screen.blit(textures["fuelrod"], (20, 20)) #J'affiche la barre de fuel
        fuel_amount = int(self.player.fuel/self.player.fuel_max*100) #Je converti le fuel en pourcentage, pour adapter ma barre selon le fuel max
        for i in range(0,fuel_amount*2): #J'affiche la quantité de fuel selon le pourcentage
            screen.blit(textures["fuelp"], (86+i, 32))

        screen.blit(textures["goldbackground"], (855, 23)) #J'affiche le fond pour l'affichage du compteur de gold
        screen.blit(textures["coin"], (970, 15)) #J'affiche l'icone de pièce, pour spécifier que c'est l'argent
        gold = [int(v) for v in list(str(self.player.gold))]
        for w in range(len(gold)):
            screen.blit(textures[str(gold[w])], (860+28*w, 27))
            pygame.display.flip()

#Shop
def affichage(): #C'est ma fonction qui affiche le shop de base, sans l'animation des boutons ou autre
        screen.blit(textures["background"], (0,0)) #J'affiche le fond beige
        screen.blit(textures["shop"], (70,50)) #J'affiche l'interface
        pygame.display.flip()

class Button:
    def __init__(self, image, position, price, func, player): #Qui prend en paramètre une image, sa position, le prix de l'amélioration, une fonction pour augmenter/décrémenter selon le bouton, et la class Player (pour avoir accès au fuel et au gold)
        self.image = image
        self.position = position
        self.price = price
        self.func = func
        self.player = player

    def click(self):
        for event in pygame.event.get(): 
            if event.type == pygame.MOUSEBUTTONUP: #Si le joueur clique sur le bouton
                self.func(self) #On effectue la fonction qui est définie sur le bouton cliqué
                    
    def animation(self): #ça sert à afficher les boutons animés, par dessus l'interface
        mouse = pygame.mouse.get_pos() #On stock la position de la souris dans la variable mouse
        while self.position[0]<mouse[0]<self.position[0] + self.image.get_width() and self.position[1]<mouse[1]<self.position[1] + self.image.get_height(): #Si la position de la souris se trouve entre la position du bouton, et le coin du bouton (opposé à la position de base du coup, pour faire une zone rectangulaire)
            screen.blit(self.image, (self.position[0], self.position[1])) #On affiche l'animation du bouton correspondant
            pygame.display.flip()
            mouse = pygame.mouse.get_pos() #Je reprend la position de la souris, pour vérifier si elle est toujours sur le bouton ou non (donc pour sortir du while)
            self.click() #J'appelle click, pour vérifier si le bouton est cliqué ou non
        affichage() #En sortant du while (donc si la souris n'est plus sur le bouton), on réenitialise l'affichage du shop (pour enlever les potentielles animations affichées)
    
def speed_button(self): #Fonction qui augmente la vitesse du joueur et le prix de l'amélioration qui vient d'être achetée
    self.player.speed += 0.2
    self.price += 20
def fuel_button(self): #Fonction qui augmente le fuel maximum et le prix de l'amélioration qui vient d'être achetée
    self.player.fuel_max += 10
    self.price += 20
def skin_button(self): #Fonction qui change le skin du joueur
    print("owo")
def exit_button(self): #Fonction définie pour le bouton exit, pour sortir du shop, et retourner sur la map
    global bool_shop
    bool_shop = False

#Class batiment
class ShopBuilding:
    def __init__(self, position, map):
        self.position = position
        self.map = map

        self.falling_cooldown = 0


    def tick(self):
        x, y = self.position

        floor_underneath = False
        for i in range(5):
            if not self.map.tiles[x + i][y + 1] in ["cave", "scaffolding"]:
                floor_underneath = True
                self.falling_cooldown = 1

        if self.falling_cooldown > 0:
                self.falling_cooldown -= .25
        else:
            if not floor_underneath:
                self.position = (x, y + 1)
                self.falling_cooldown = 1

        offset = drill.get_camera_offset()
        screensize = screen.get_size()

        if offset[0] <= x + 4 and offset[0] + screensize[0] // 32 > x and offset[1] < y + 1:
            texture = textures["garage"]
            screen.blit(pygame.transform.scale(texture, (160, 80)), (x * 32 - offset[0] * 32, y * 32 - offset[1] * 32 - 48))

            if not floor_underneath:
                parachute_texture = textures["shop_parachute"]
                screen.blit(pygame.transform.scale(parachute_texture, (160, 160)), (x * 32 - offset[0] * 32, y * 32 - offset[1] * 32 - 208))

#Boucle principal
clock = pygame.time.Clock() #Créer une "clock" qui permet de limiter la vitesse d'excution maximal grace à la fonction tick()

level = Map(1024, 1024) #Créer une carte de 1024 * 1024
drill = Player((level.width // 2, 0), level) #Créer le joueur ayant comme paramètre la carte
hud = Interface(drill) #Créer une interface avec différentes barres (comme) le fuel) et compteurs (comme le gold)

boutons = [
    Button(textures["buy"], [103, 632], 20, speed_button, drill),
    Button(textures["buy"], [391, 632], 20, fuel_button, drill),
    Button(textures["buy"], [679, 632], 500, skin_button, drill),
    Button(textures["exit"], [426, 691], 0, exit_button, drill),
] #Tableau contenant chaque paramètres de chaque boutons
shop = ShopBuilding((level.width // 2, 0), level)

bool_shop = True #Faut changer ça, selon ce que tu veux (être dans le shop, ou sur la map princiaple)
running = True
while running: #Boucle principal qui execute toutes les fonctions à chaques frames
    clock.tick(60) 

    if bool_shop:
        for i in range(len(boutons)):
            boutons[i].animation()
    else:
        level.render(drill.get_camera_offset()) #Affiche la carte avec une position de camera obtenue grace à fonction get_camera_offset()
        shop.tick() #"Met a jour" la shop
        drill.tick() #"Met a jour" la foreuse
        hud.render() #"Met a jour" l'interface

    pygame.display.flip() #Met à jour l'affichage

    for event in pygame.event.get(): #Permet d'arrêter la boucle (Et donc le jeu si la fenêtre est fermée)
        if event.type == pygame.QUIT:
            running = False

#Lignes par Lucas: 170
#Lignes par Ugo: 80
