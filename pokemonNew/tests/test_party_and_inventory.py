from world.party_manager import PartyManager, MAX_PARTY_SIZE
from world.inventory import Inventory


class FakeMon:
    def __init__(self, name, fainted=False):
        self.name = name
        self._fainted = fainted

    def is_fainted(self):
        return self._fainted


def test_add_fills_party_first():
    pm = PartyManager()
    where, idx = pm.add(FakeMon("a"))
    assert where == "party"
    assert idx == 0
    assert len(pm.party) == 1


def test_add_overflows_to_box_when_party_full():
    pm = PartyManager()
    for i in range(MAX_PARTY_SIZE):
        pm.add(FakeMon(f"mon{i}"))
    assert len(pm.party) == MAX_PARTY_SIZE
    where, idx = pm.add(FakeMon("overflow"))
    assert where == "box"
    box_i, slot_i = idx
    assert pm.boxes[box_i][slot_i].name == "overflow"


def test_reorder_party():
    pm = PartyManager(party=[FakeMon("a"), FakeMon("b"), FakeMon("c")])
    assert pm.reorder(2, 0) is True
    assert [m.name for m in pm.party] == ["c", "a", "b"]


def test_reorder_out_of_range_fails():
    pm = PartyManager(party=[FakeMon("a")])
    assert pm.reorder(0, 5) is False


def test_first_healthy_index_skips_fainted():
    pm = PartyManager(party=[FakeMon("a", fainted=True), FakeMon("b", fainted=False)])
    assert pm.first_healthy_index() == 1


def test_all_fainted_true_when_every_mon_down():
    pm = PartyManager(party=[FakeMon("a", fainted=True), FakeMon("b", fainted=True)])
    assert pm.all_fainted() is True


def test_deposit_refuses_to_empty_the_party():
    pm = PartyManager(party=[FakeMon("only")])
    assert pm.deposit_to_box(0) is False


def test_withdraw_and_deposit_round_trip():
    pm = PartyManager(party=[FakeMon("a"), FakeMon("b")])
    assert pm.deposit_to_box(1) is True
    assert len(pm.party) == 1
    assert pm.withdraw_from_box(0, 0) is True
    assert len(pm.party) == 2


def test_inventory_add_use_has():
    inv = Inventory()
    inv.add("Potion", 3)
    assert inv.has("Potion", 3) is True
    assert inv.has("Potion", 4) is False
    assert inv.use("Potion", 1) is True
    assert inv.items["Potion"] == 2


def test_inventory_use_removes_key_at_zero():
    inv = Inventory()
    inv.add("Antidote", 1)
    inv.use("Antidote", 1)
    assert "Antidote" not in inv.items


def test_inventory_round_trip_dict():
    inv = Inventory({"Poke Ball": 5})
    restored = Inventory.from_dict(inv.to_dict())
    assert restored.has("Poke Ball", 5)
