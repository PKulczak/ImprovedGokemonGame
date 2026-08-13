"""An open flag dict (rather than dozens of named booleans) so new story
beats are just new string keys, without ever needing a save-schema change."""


class StoryFlags:
    def __init__(self, data=None):
        self.flags = dict(data or {})

    def get(self, key, default=None):
        return self.flags.get(key, default)

    def set(self, key, value):
        self.flags[key] = value

    def increment(self, key, by=1, default=0):
        self.flags[key] = self.flags.get(key, default) + by
        return self.flags[key]

    def to_dict(self):
        return dict(self.flags)

    @classmethod
    def from_dict(cls, data):
        return cls(data)


def evaluate_condition(condition, flags: StoryFlags):
    """condition: {"flag": "badges", "op": ">=", "value": 3} or None (always true).
    The one mechanism behind conditional NPC spawns, rival appearances, and
    gym/League gating."""
    if condition is None:
        return True
    flag_value = flags.get(condition["flag"])
    op = condition.get("op", "==")
    value = condition["value"]
    if op == "==":
        return flag_value == value
    if op == "!=":
        return flag_value != value
    if op == ">=":
        return (flag_value or 0) >= value
    if op == "<=":
        return (flag_value or 0) <= value
    if op == ">":
        return (flag_value or 0) > value
    if op == "<":
        return (flag_value or 0) < value
    if op == "in":
        return flag_value in value
    raise ValueError(f"unknown condition op: {op!r}")
