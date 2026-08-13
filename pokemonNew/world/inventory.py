class Inventory:
    """Bag quantity bookkeeping. Item EFFECTS are the battle package's concern
    (battle.items.ITEM_HANDLERS) — this just tracks what's held and how many."""

    def __init__(self, items=None):
        self.items = dict(items or {})

    def add(self, item_name, quantity=1):
        self.items[item_name] = self.items.get(item_name, 0) + quantity

    def has(self, item_name, quantity=1):
        return self.items.get(item_name, 0) >= quantity

    def use(self, item_name, quantity=1):
        if not self.has(item_name, quantity):
            return False
        self.items[item_name] -= quantity
        if self.items[item_name] <= 0:
            del self.items[item_name]
        return True

    def to_dict(self):
        return dict(self.items)

    @classmethod
    def from_dict(cls, data):
        return cls(data)
