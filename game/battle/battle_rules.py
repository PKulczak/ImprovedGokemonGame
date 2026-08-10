import random
from game.engine import balance

#pure damage formula - ATK vs DEF, minimum 1 damage. Doesn't touch any Pokemon/canvas object,
#so it can be tested with plain numbers, independent of rendering.
def damage_amount(attacker_atk, defender_def):
    if attacker_atk > defender_def:
        return attacker_atk - defender_def
    return 1

#rolls whether an escape attempt succeeds
def escape_succeeds():
    return random.randint(1, balance.ESCAPE_SUCCESS_ROLL_MAX) == 1

#rolls whether a catch attempt succeeds - trainer battles (is_npc_battle) can never be caught
def catch_succeeds(is_npc_battle):
    if is_npc_battle:
        return False
    return random.randint(1, balance.CATCH_SUCCESS_ROLL_MAX) == 1

#computes a pokemon's stats after leveling up to new_lvl, from its BASE (unscaled) stats -
#returns (atk, def, fullhp, max_exp, give_exp), same formula previously duplicated in
#Pokemon.__init__ and Fight.fight()'s level-up branch
def level_up_stats(base_atk, base_def, base_fullhp, new_lvl):
    atk = int(base_atk + (((base_atk * balance.ATK_GROWTH_RATE) * new_lvl) // 1))
    def_ = int(base_def + (((base_def * balance.DEF_GROWTH_RATE) * new_lvl) // 1))
    fullhp = int(base_fullhp + (((base_fullhp * balance.HP_GROWTH_RATE) * new_lvl) // 1))
    max_exp = int(balance.BASE_MAX_EXP + ((balance.MAX_EXP_PER_LEVEL * new_lvl) // 1))
    give_exp = int(balance.BASE_GIVE_EXP + ((balance.GIVE_EXP_PER_LEVEL * new_lvl) // 1))
    return atk, def_, fullhp, max_exp, give_exp
