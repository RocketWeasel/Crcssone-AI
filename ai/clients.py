import time
from ai.my_ai.my_player import MyPlayer
from ai.my_ai.my_player_decisiontree import MyPlayerDecisionTree
from ai.my_ai.my_player_modified import MyPlayerModified
from ai.random_player import RandomPlayer
from datemi.carcassonne.client.carcassonne_client import CarcassonneClient
from datemi.carcassonne.game.carcassonne_local import CarcassonneLocal

from datemi.carcassonne.shared.com.playertype import PlayerType


def find_game(carcassonne: CarcassonneClient, player_per_match=4):
    carcassonne.clear_game()
    carcassonne.join_game("rand")
    if carcassonne.get_player_count() >= player_per_match:
        carcassonne.start_game()


def random_network(nickname="AI", address="ws://localhost:8765", no_matches=10, player_per_match=4):
    no_of_games = no_matches
    carcassonne = CarcassonneClient(MyPlayer(nickname))
    carcassonne.connect(address)
    carcassonne.join_game("rand")
    if carcassonne.get_player_count() >= player_per_match:
        carcassonne.start_game()
    no_of_games -= 1
    while no_of_games > 0:
        time.sleep(0.5)
        if carcassonne.is_finished() == True:
            find_game(carcassonne, player_per_match)
            no_of_games -= 1
    carcassonne.save_close()
    return "Client " + nickname + " finished " + str(no_matches) + " games."


def managed_network(nickname="AI", address="ws://localhost:8765", clients_per_thread=1):
    clients: list[CarcassonneClient] = []
    for _ in range(clients_per_thread):
        carcassonne = CarcassonneClient(MyPlayerDecisionTree(nickname))
        carcassonne.connect(address)
        carcassonne.register()
        clients.append(carcassonne)
    for c in clients:
        c.save_close()
    return "Client " + nickname + " finished."


def local_game(nickname="AI", gamename="game", no_matches=10, player_per_match=4, visualize=False, average=False, debug=False) -> \
list[float]:
    results = [0 for i in range(player_per_match)]
    carcassonne: CarcassonneLocal
    game_no = 0
    while game_no < no_matches:
        carcassonne = CarcassonneLocal(gamename + str(game_no), visualize, average=average)
        for i in range(player_per_match):
            if i == 0:
                carcassonne.add_player(MyPlayer(nickname + str(i)))
            else:
                carcassonne.add_player(RandomPlayer(f"Random{i}"))
        result = carcassonne.start_game()
        if (average):
            for j in range(player_per_match):
                results[j] += result[j]
        game_no += 1

    if average:
        for j in range(player_per_match):
            results[j] /= no_matches
        return results


def local_game_modified(nickname="Modified AI", gamename="game", no_matches=10, player_per_match=4, visualize=False,
                        average=False) -> list[float]:
    results = [0 for i in range(player_per_match)]
    carcassonne: CarcassonneLocal
    game_no = 0
    while game_no < no_matches:
        carcassonne = CarcassonneLocal("modified_" + gamename + str(game_no), visualize, average=average)
        for i in range(player_per_match):
            if i == 0:
                carcassonne.add_player(MyPlayerModified(nickname + str(i)))
            else:
                carcassonne.add_player(RandomPlayer(f"Random{i}"))

        result = carcassonne.start_game()
        if (average):
            for j in range(player_per_match):
                results[j] += result[j]
        game_no += 1

    if average:
        for j in range(player_per_match):
            results[j] /= no_matches
        return results
