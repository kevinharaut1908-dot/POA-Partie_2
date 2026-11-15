
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


# ------------------------------- 3 nouvelles stratégies ajoutées -------------------------------




def grim(mes_coups, coups_adverses, rng):
    """GRIM : coopère tant que l'adversaire n'a jamais trahi. Si elle est trahie, trahit jusqu'à la fin."""
    if "D" in coups_adverses:
        return "D"
    return "C"


def pavlov(mes_coups, coups_adverses, rng):
    """PAVLOV : coopère au premier tour.
    Si le score gagné du tour précédent est supérieur ou égal à 3, rejoue le même coup ; sinon change de coup."""
    if not mes_coups:
        return "C"

    mon_dernier = mes_coups[-1]
    if coups_adverses[-1] == "C":  
        return mon_dernier
    if mon_dernier == "C":
        return "D"
    return "C"

def all_c(mes_coups, coups_adverses, rng):
    """ALL-C : coopère toujours, quoi que fasse l'adversaire."""
    return "C"
