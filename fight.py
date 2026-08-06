try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import time
import random
import os
import json
from image_cache import load_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#loads each pokemon's base stats from Pokedex.json once, keyed by name
def _load_pokedex():
    with open('{}/Fight/Files/Pokedex.json'.format(BASE_DIR), "r") as file:
        return json.load(file)

POKEDEX = _load_pokedex()

#records a pokemon as seen in the player's Pokedex, if it isn't already
def _mark_pokemon_seen(name):
    path = '{}/Fight/Files/PlayerPokedex.json'.format(BASE_DIR)
    with open(path, "r") as file:
        seen = json.load(file)
    if name not in seen:
        seen.append(name)
        with open(path, "w") as file:
            json.dump(seen, file, indent=2)

class Fight:
    def __init__(self, monster_list, pokemon_list, keyboard, npc):
        self.mons_list = monster_list
        self.monster = monster_list[0]
        self.poke_list = pokemon_list
        self.pokemon = pokemon_list[0]
        self.count = 70
        self.attack = True
        self.kbd = keyboard
        self.npc = npc
        self.info = self.monster.name+" VS "+ self.pokemon.name
        self.image = load_image('{}/Fight/Other/fight_background.png'.format(BASE_DIR))
        self.col1 = "White"
        self.col2 = "Grey"
        self.col3 = "Grey"
        self.col4 = "Grey"
        self.inte = 1
        self.run = False
        self.bag = load_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        self.first = True
        self.change = False
        self.catch = False
        self.lost = False
        self.centre = [0,0]
        self.pos = [[(348,145),(348,265),(348,380)],[(598,145),(598,265),(598,380)]]
        self.end = False

    #responsible for drawing the fight
    def draw(self, canvas):
        if self.change:
            if not self.kbd.quit:
                if not self.kbd.select:
                    canvas.draw_image(self.bag, (375,250), (750,500), (400,240), (735,490))
                    if not self.first:
                        if self.kbd.left and self.centre[0] == 1:
                            self.centre[0] = 0
                            self.first = True
                        elif self.kbd.down and self.centre[1] < 2:
                            self.centre[1] += 1
                            self.first = True
                        elif self.kbd.right and self.centre[0] == 0:
                            self.centre[0] = 1
                            self.first = True
                        elif self.kbd.up and self.centre[1] > 0:
                            self.centre[1] -= 1
                            self.first = True
                    else:
                        if not(self.kbd.left or self.kbd.right or self.kbd.up or self.kbd.down):
                            self.first = False
                    canvas.draw_image(self.light, (116,45), (233,91), self.pos[self.centre[0]][self.centre[1]], (233,91))
                    for i in range(0,len(self.poke_list)):
                        if i<3:
                            canvas.draw_text(self.poke_list[i].name, (270, 130+(i*120)), 25, 'Black')
                            canvas.draw_text("HP:"+str(self.poke_list[i].HP), (350, 160+(i*120)), 25, 'Black')
                        else:
                            canvas.draw_text(self.poke_list[i].name, (520, 130+(i-3)*120), 25, 'Black')
                            canvas.draw_text("HP:"+str(self.poke_list[i].HP), (600, 160+(i-3)*120), 25, 'Black')
                else:
                    if self.centre[0] == 0 :
                        choice = self.centre[0]+self.centre[1]
                    else:
                        choice = self.centre[0]+self.centre[1]+2
                    if self.catch:
                        self.monster.pos = self.pokemon.pos
                        self.monster.pos1 = self.pokemon.pos1
                        self.poke_list[choice] = self.monster
                        self.mons_list.remove(self.monster)
                        if len(self.mons_list) == 0:
                            self.end = True
                        else:
                            self.monster = self.mons_list[0]
                        self.catch = False
                    else:
                        if len(self.poke_list)-1>=choice:
                            self.pokemon = self.poke_list[choice]
                            self.change = False
                        self.kbd.select = False
            else:
                self.change = False
                if self.catch:
                    self.info = "You release it again."
                    self.catch = False
        else:
            canvas.draw_image(self.image, (375,250), (750,500), (400,240), (735,490))
            canvas.draw_text(self.monster.name, (155, 80), 25, 'Black')
            canvas.draw_text("HP:"+str(self.monster.HP)+"   Lvl:"+str(self.monster.lvl), (190, 110), 25, 'Black')
            canvas.draw_text(self.pokemon.name, (530, 255), 25, 'Black')
            canvas.draw_text("HP:"+str(self.pokemon.HP)+"/"+str(self.pokemon.fullhp)+"  Lvl:"+str(self.pokemon.lvl), (530, 295), 25, 'Black')
            self.pokemon.draw(canvas)
            self.monster.draw(canvas)
            if self.run:
                canvas.draw_text(self.info, (120, 415), 25, 'White')
                self.count = self.count - 1
            elif self.count != 0:
                if not self.first:
                    if self.attack:
                        self.monster.draw_effect(canvas)
                    else:
                        self.pokemon.draw_effect(canvas)
                canvas.draw_text(self.info, (120, 415), 25, 'White')
                self.count = self.count - 1
            else:
                self.monster.frame_index1[1] = 0
                self.pokemon.frame_index1[1] = 0
                self.first = False
                if self.attack:
                    if not self.kbd.select:
                        self.inte = self.interact(self.inte, canvas)
                    else:
                        if self.inte <=3 :
                            self.fight(self.pokemon, self.monster, self.inte, canvas)
                            self.kbd.select = False
                            self.count = 130
                        elif self.inte == 4:
                            self.change = True
                            self.kbd.select = False
                else:
                    self.fight(self.pokemon, self.monster, self.inte, canvas)
                    self.count = 110

    #does all the calculations for the fight
    def fight(self, pokemon, monster, inte, canvas):
        if pokemon.HP > 0 and monster.HP > 0:
            if not self.attack:
                if monster.ATK>pokemon.DEF:
                    pokemon.HP = pokemon.HP-(monster.ATK - pokemon.DEF)
                else:
                    pokemon.HP = pokemon.HP-1
                if pokemon.HP < 0:
                    pokemon.HP = 0
                self.info = monster.name+" attack "+pokemon.name
                self.attack = True
            else:
                if inte == 1:
                    if pokemon.ATK>monster.DEF:
                        monster.HP = monster.HP-(pokemon.ATK - monster.DEF)
                    else:
                        monster.HP = monster.HP-1
                    if monster.HP<0:
                        monster.HP = 0
                    self.info = pokemon.name+" attack "+monster.name
                    self.attack = False
                elif inte == 2:
                    run = random.randint(1,4)
                    if run == 1:
                        self.info = "You escaped!"
                        self.run = True
                        self.count = 70
                        self.end = True
                    else:
                        self.info = "Escape failed!"
                        self.attack = False
                elif inte == 3:
                    if self.npc == True:
                        catch = 5
                    else:
                        catch = random.randint(1,5)
                    if catch == 1:
                        if len(self.poke_list) < 6:
                            self.info = "Catch succeed!"
                            self.monster.pos = self.pokemon.pos
                            self.monster.pos1 = self.pokemon.pos1
                            self.poke_list.append(monster)
                            self.mons_list.remove(self.monster)
                            _mark_pokemon_seen(monster.name)
                            if len(self.mons_list) == 0:
                                self.count = 0
                                self.end = True
                            else:
                                self.monster = self.mons_list[0]
                        else:
                            self.change = True
                            self.catch = True
                    else:
                        self.info = "Catch failed!"
                        self.attack = False
                                             
        else:
            if pokemon.HP > 0 and len(self.mons_list) == 0:
                self.info = "Fight end, you win!"
                self.end = True
            elif monster.HP >0:
                survive = False
                for i in range(0,len(self.poke_list)):
                    if self.poke_list[i].HP>0:
                        survive = True
                if survive:
                    self.change = True
                else:
                    self.info = "Fight end,You lose"
                    self.attack = False
                    self.count = 70
                    self.lost = True
                    self.end = True
            elif pokemon.HP > 0:
                pokemon.exp += monster.give_exp
                if pokemon.exp >= pokemon.max_exp:
                    if pokemon.lvl <= 25:
                        pokemon.lvl += 1
                        base_stats = POKEDEX[pokemon.name]
                        pokemon.ATK = base_stats["ATK"]
                        pokemon.DEF = base_stats["DEF"]
                        pokemon.fullhp = base_stats["fullhp"]
                        pokemon.max_exp = 100
                        pokemon.ATK = int(pokemon.ATK+(((pokemon.ATK*0.1)*pokemon.lvl)//1))
                        pokemon.DEF = int(pokemon.DEF+(((pokemon.DEF*0.01)*pokemon.lvl)//1))
                        pokemon.fullhp = int(pokemon.fullhp+(((pokemon.fullhp*0.1)*pokemon.lvl)//1))
                        pokemon.max_exp = int(100+((10*pokemon.lvl)//1))
                        pokemon.give_exp = int(30+((3*pokemon.lvl)//1))
                    pokemon.exp -= pokemon.max_exp
                    pokemon.HP = pokemon.fullhp

                _mark_pokemon_seen(monster.name)

                self.mons_list.remove(monster)
                if not(len(self.mons_list) == 0):
                    self.monster = self.mons_list[0]
                
    def interact(self, inte, canvas):
        canvas.draw_text("What will "+self.pokemon.name+" do?", (120, 415), 25, 'White')
        canvas.draw_text("Attack",(500,415), 25, self.col1)
        canvas.draw_text("Catch",(600,415), 25, self.col2)
        canvas.draw_text("Run",(560,450), 25, self.col3)
        canvas.draw_text("Bag",(560,380), 25, self.col4)
        if self.kbd.left:
            self.col1 = "White"
            self.col2 = self.col3 = self.col4 = "Grey"
            inte = 1
        elif self.kbd.down:
            self.col1 = self.col2 = self.col4 = "Grey"
            self.col3 = "White"
            inte = 2
        elif self.kbd.right:
            self.col1 = self.col3 = self.col4 = "Grey"
            self.col2 = "White"
            inte = 3
        elif self.kbd.up:
            self.col1 = self.col2 = self.col3 = "Grey"
            self.col4 = "White"
            inte = 4
        return inte
        
#An object for each pokemon            
class Pokemon:
    def __init__(self, name, HP, lvl, exp, pos, pos1):
        self.name = name
        base_stats = POKEDEX[self.name]
        self.ATK = base_stats["ATK"]
        self.DEF = base_stats["DEF"]
        self.fullhp = base_stats["fullhp"]
        effect_img = base_stats["effect_img"]
        row = base_stats["row"]
        self.count = 0

        #pokemon scaling
        self.lvl = lvl
        self.exp = exp
        self.max_exp = 100
        self.ATK = int(self.ATK+(((self.ATK*0.1)*self.lvl)//1))
        self.DEF = int(self.DEF+(((self.DEF*0.01)*self.lvl)//1))
        self.fullhp = int(self.fullhp+(((self.fullhp*0.1)*self.lvl)//1))
        self.max_exp = int(100+((10*self.lvl)//1))
        self.give_exp = int(30+((3*self.lvl)//1))
        if HP == -1:
            self.HP = self.fullhp
        else:
            self.HP = HP
        
        # pokemon image
        self.image = load_image(('{}/Fight/pokemon/'.format(BASE_DIR))+name+".png")
        width = self.image.get_width()
        frame_width = width//5
        height = self.image.get_height()
        frame_height = height//row
        self.pos = pos
        self.frame_center = [frame_width/2, frame_height/2]
        self.frame_dim = [frame_width, frame_height]
        self.frame_index = [0,0]
        self.row = row
        
        # attack effect image
        effect_row = {"water" : 3,
                      "fire" : 10,
                      "electric": 9,
                      "grass": 5,
                      "dark": 5,
                      "dragon": 3,
                      "fairy": 12,
                      "flying": 4,
                      "ice": 5,
                      "poison": 3,
                      "psychic": 2,
                      "rock": 2}
        self.effectimg = load_image(('{}/Fight/effects/'.format(BASE_DIR))+effect_img+".png")
        width = self.effectimg.get_width()
        frame_width = width//5
        height = self.effectimg.get_height()
        row1 = effect_row[effect_img]
        frame_height = height//row1
        
        self.pos1 = pos1
        self.frame_center1 = [frame_width/2, frame_height/2]
        self.frame_dim1 = [frame_width, frame_height]
        self.frame_index1 = [0,0]
        self.row1 = row1

    def draw(self, canvas):
            canvas.draw_image(self.image,
                              [self.frame_center[0] + self.frame_index[0] * self.frame_dim[0],
                               self.frame_center[1] + self.frame_index[1] * self.frame_dim[1]],
                              self.frame_dim, [self.pos[0], self.pos[1]],
                              [self.frame_dim[0]*3,self.frame_dim[1]*3])
            if self.count%10 == 0:
                self.next_frame()
            self.count +=1
    
    def next_frame(self):
        self.frame_index[0] += 1
        if self.frame_index[0] >= 5:
            self.frame_index[0] = 0
            self.frame_index[1] +=1
            if self.frame_index[1] >= self.row:
                self.frame_index[1] = 0
                
    def next_effect(self):
        self.frame_index1[0] += 1
        if self.frame_index1[0] >= 5:
            self.frame_index1[0] = 0
            self.frame_index1[1] +=1
            if self.frame_index1[1] >= self.row1:
                self.frame_index1[1] = 0
                
    def draw_effect(self, canvas):
        canvas.draw_image(self.effectimg,
                          [self.frame_center1[0] + self.frame_index1[0] * self.frame_dim1[0],
                           self.frame_center1[1] + self.frame_index1[1] * self.frame_dim1[1]],
                          self.frame_dim1, [self.pos1[0], self.pos1[1]],
                          [self.frame_dim1[0]+35,self.frame_dim1[1]+35])
        if self.count%4 == 0:
                self.next_effect()

#Sets up the keyboard handlers for fight and gokedex 
class Kbd:
    def __init__(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.select = False
        self.quit = False

    def keyDown(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.right = True
        if key == simplegui.KEY_MAP['left']:
            self.left = True
        if key == simplegui.KEY_MAP['up']:
            self.up = True
        if key == simplegui.KEY_MAP['down']:
            self.down = True
        if key == simplegui.KEY_MAP['q']:
            self.quit = True
        if key == simplegui.KEY_MAP['space']:
            self.select = True

    def keyUp(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.right = False
        if key == simplegui.KEY_MAP['left']:
            self.left = False
        if key == simplegui.KEY_MAP['up']:
            self.up = False
        if key == simplegui.KEY_MAP['down']:
            self.down = False
        if key == simplegui.KEY_MAP['q']:
            self.quit = False

    def KeyReset(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False

