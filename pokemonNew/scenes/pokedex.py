from engine.scene import Scene


class PokedexScene(Scene):
    blocks_update_below = True
    draws_below = True

    PAGE_SIZE = 6

    def on_enter(self, **kwargs):
        self.scroll = 0

    def handle_input(self, input_state):
        if input_state.was_pressed("CANCEL") or input_state.was_pressed("START"):
            self.app.scene_stack.pop()
        elif input_state.was_pressed("DOWN"):
            self.scroll += 1
        elif input_state.was_pressed("UP"):
            self.scroll = max(0, self.scroll - 1)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((245, 245, 235))
        font = self.app.assets.font(14)
        seen = sorted(self.app.state.pokedex_seen)
        caught = self.app.state.pokedex_caught
        header = f"Pokedex - Seen {len(seen)}, Caught {len(caught)}"
        surface.blit(font.render(header, True, (20, 20, 20)), (10, 6))

        try:
            from data.species import SPECIES
            by_dex = {s.dex_number: s for s in SPECIES.values()}
        except ImportError:
            by_dex = {}

        y = 26
        for dex_num in seen[self.scroll: self.scroll + self.PAGE_SIZE]:
            species = by_dex.get(dex_num)
            name = species.name if species else f"#{dex_num}"
            mark = "caught" if dex_num in caught else "seen"
            surface.blit(font.render(f"#{dex_num:03d} {name} ({mark})", True, (20, 20, 20)), (10, y))
            y += 16
