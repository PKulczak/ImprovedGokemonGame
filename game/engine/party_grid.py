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
        else:
            if not (kbd.left or kbd.right or kbd.up or kbd.down):
                first = False
        return first

    def draw_highlight(self, canvas, bag_image, light_image):
        canvas.draw_image(bag_image, (375,250), (750,500), (400,240), (735,490))
        canvas.draw_image(light_image, (116,45), (233,91), self.POSITIONS[self.centre[0]][self.centre[1]], (233,91))
