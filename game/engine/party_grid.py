from game.engine import sound

#the 2-column/3-row party cursor grid shared by Fight's bag-browse menu and Pokedex - both used
#to hand-roll the same centre/first debounce bookkeeping and the same six screen positions
class PartyGrid:
    POSITIONS = [[(348,145),(348,265),(348,380)],[(598,145),(598,265),(598,380)]]

    #on_page(direction), if given, is called with +1 when down is pressed at the bottom row or
    #-1 when up is pressed at the top row - Pokedex uses it to turn to the next/previous page of
    #6; left as None, those two inputs simply do nothing at the grid edge, matching Fight (no pages)
    def __init__(self, on_page=None):
        self.centre = [0, 0]
        self.on_page = on_page

    #advances centre from kbd input, debounced by first (True = wait for keys to release before
    #the next move counts); returns the new first value rather than owning it, since some callers
    #(Fight) reuse the same first flag for other state outside the grid
    def update(self, kbd, first):
        if not first:
            if kbd.left and self.centre[0] == 1:
                self.centre[0] = 0
                first = True
            elif kbd.down and self.centre[1] < 2:
                self.centre[1] += 1
                first = True
            elif self.on_page and kbd.down and self.centre[1] == 2:
                self.on_page(1)
                first = True
            elif self.on_page and kbd.up and self.centre[1] == 0:
                self.on_page(-1)
                first = True
            elif kbd.right and self.centre[0] == 0:
                self.centre[0] = 1
                first = True
            elif kbd.up and self.centre[1] > 0:
                self.centre[1] -= 1
                first = True
            if first:
                sound.play_sfx("menu_move")
        else:
            if not (kbd.left or kbd.right or kbd.up or kbd.down):
                first = False
        return first

    #flattens centre (col, row) into a single 0-5 index - left column first (0-2), then right
    #column (3-5) - matching the reading order every grid-based list in this project draws in
    def selected_index(self):
        if self.centre[0] == 0:
            return self.centre[1]
        return self.centre[1] + 3

    def draw_highlight(self, canvas, bag_image, light_image):
        canvas.draw_image(bag_image, (375,250), (750,500), (400,240), (735,490))
        canvas.draw_image(light_image, (116,45), (233,91), self.POSITIONS[self.centre[0]][self.centre[1]], (233,91))

#a species' idle frame is always exactly 50x50 regardless of species (see Pokemon.__init__,
#fight.py) - scaled down to this so it lines up vertically with a name rendered at SLOT_NAME_FONT
SLOT_SPRITE_SIZE = 30
SLOT_NAME_FONT = 26

#one party slot's info - species icon, name (top-left, big), level (top-right, same row), HP
#(below the name, smaller) - shared by the battle Bag menu (fight.py's _draw_bag_browse) and
#the overworld party-reorder screen (ui.py's TeamOrder) so the two don't drift out of sync.
#colour is the caller's own choice (Fight uses DarkRed for fainted, TeamOrder uses Yellow for
#a picked-up slot); the icon greys itself out on a fainted (HP<=0) Pokemon regardless of colour
def draw_party_slot(canvas, mon, name_x, row_y, colour):
    fainted = mon.HP <= 0
    #-size/4 centers it on draw_text's own vertical anchor (point_y - height*3/4, see
    #Canvas.draw_text) for a name rendered at exactly SLOT_SPRITE_SIZE tall; -21 sits it in the
    #box's own left margin (the gap bag.png already leaves before name_x) rather than pushing
    #name/level rightward and crowding the level position
    sprite_centre = (name_x-21, row_y-SLOT_SPRITE_SIZE/4)
    canvas.draw_image(mon.image, mon.frame_center, mon.frame_dim,
                       sprite_centre, (SLOT_SPRITE_SIZE, SLOT_SPRITE_SIZE), grayscale=fainted)
    canvas.draw_text(mon.name, (name_x, row_y), SLOT_NAME_FONT, colour)
    #+140 is wide enough that even this roster's widest rendered name at this font size
    #("Charmander", 130px) doesn't run into the level
    canvas.draw_text("Lv."+str(mon.lvl), (name_x+140, row_y), 20, colour)
    canvas.draw_text("HP:"+str(mon.HP)+"/"+str(mon.fullhp), (name_x, row_y+34), 20, colour)
