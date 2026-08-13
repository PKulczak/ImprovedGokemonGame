"""Party/PC-box bookkeeping. Operates on opaque Pokemon-instance objects
(duck-typed: only needs .is_fainted()) so it has zero dependency on the
battle-mechanics package."""

MAX_PARTY_SIZE = 6


class PartyManager:
    def __init__(self, party=None, boxes=None, box_size=30, box_count=8):
        self.party = list(party or [])
        self.boxes = boxes if boxes is not None else [[None] * box_size for _ in range(box_count)]

    def add(self, pokemon):
        """Adds to the party if there's room, else the first free PC box slot.
        Returns ("party", index) | ("box", (box_i, slot_i)) | (None, None) if totally full."""
        if len(self.party) < MAX_PARTY_SIZE:
            self.party.append(pokemon)
            return ("party", len(self.party) - 1)
        for box_index, box in enumerate(self.boxes):
            for slot_index, slot in enumerate(box):
                if slot is None:
                    box[slot_index] = pokemon
                    return ("box", (box_index, slot_index))
        return (None, None)

    def reorder(self, from_index, to_index):
        if not (0 <= from_index < len(self.party)) or not (0 <= to_index < len(self.party)):
            return False
        mon = self.party.pop(from_index)
        self.party.insert(to_index, mon)
        return True

    def withdraw_from_box(self, box_index, slot_index):
        if len(self.party) >= MAX_PARTY_SIZE:
            return False
        mon = self.boxes[box_index][slot_index]
        if mon is None:
            return False
        self.boxes[box_index][slot_index] = None
        self.party.append(mon)
        return True

    def deposit_to_box(self, party_index):
        if len(self.party) <= 1:
            return False  # never allow an empty party
        if not (0 <= party_index < len(self.party)):
            return False
        mon = self.party[party_index]
        for box in self.boxes:
            for slot_index, slot in enumerate(box):
                if slot is None:
                    box[slot_index] = mon
                    self.party.pop(party_index)
                    return True
        return False

    def first_healthy_index(self):
        for i, mon in enumerate(self.party):
            if not mon.is_fainted():
                return i
        return None

    def all_fainted(self):
        return all(mon.is_fainted() for mon in self.party) if self.party else True
