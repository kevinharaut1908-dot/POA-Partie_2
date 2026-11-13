"""Stratégies du dilemme du prisonnier itéré.

Signature commune : strategie(mes_coups, coups_adverses, rng) -> "C" ou "D"
"""


def all_d(mes_coups, coups_adverses, rng):
    """ALL-D : trahit toujours."""
    return "D"


def random_strat(mes_coups, coups_adverses, rng):
    """RANDOM : coopère ou trahit avec une probabilité 1/2, sans regarder l'historique."""
    return "C" if rng.random() < 0.5 else "D"


def tit_for_tat(mes_coups, coups_adverses, rng):
    """TIT-FOR-TAT : coopère au premier tour, puis copie le dernier coup adverse."""
    if not coups_adverses:
        return "C"
    return coups_adverses[-1]


PROBA_TRAHISON_JOSS = 0.1


def joss(mes_coups, coups_adverses, rng):
    """JOSS : comme TFT mais si il coopère il y a 10% de chance de trahir au final"""
    coup = tit_for_tat(mes_coups, coups_adverses, rng)
    if coup == "C" and rng.random() < PROBA_TRAHISON_JOSS:
        return "D"
    return coup


def tester(mes_coups, coups_adverses, rng):
    """TESTER : D au premier tour
    - Si l'adversaire a deja joue D -> joue TIT-FOR-TAT
    - Sinon repete le motif C, C, D"""
    tour = len(mes_coups)  # numéro du tour, en partant de 0

    if tour == 0:
        return "D"

    if "D" in coups_adverses:
        return tit_for_tat(mes_coups, coups_adverses, rng)

    # L'adversaire n'a jamais D : C, C, D en boucle
    return "D" if tour % 3 == 0 else "C"
