"""Stratégies du dilemme du prisonnier itéré.

Signature commune : strategie(mes_coups, coups_adverses, rng) -> "C" ou "D"
"""


def all_d(mes_coups, coups_adverses, rng):
    """ALL-D : trahit toujours."""
    return "D"


def tit_for_tat(mes_coups, coups_adverses, rng):
    """TIT-FOR-TAT : coopère au premier tour, puis copie le dernier coup adverse."""
    if not coups_adverses:
        return "C"
    return coups_adverses[-1]
