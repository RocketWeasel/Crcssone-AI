from ai.random_player import RandomPlayer
# from datemi.carcassonne.game.carcassonne_local import CarcassonneLocal
from datemi.carcassonne.game.carcasonne_local_modified import CarcassonneLocalModified as CarcassonneLocal


def local_game(no_matches=10, core_number=1,
               visualize=False, average=False, ais=None, debug=False):
    averages = [0 for i in range(len(ais))]
    carcassonne: CarcassonneLocal
    game_no = 0
    while game_no < no_matches:
        carcassonne = CarcassonneLocal(str(f"{game_no}"), visualize, average=average, debug=debug)
        for i, ai in enumerate(ais):
            carcassonne.add_player(ai(f"{i + 1}", debug, core_number))

        averages = list(map(lambda a, b: a + b, averages, carcassonne.start_game()))
        game_no += 1

    for j in range(len(ais)):
        averages[j] /= no_matches

    return averages
