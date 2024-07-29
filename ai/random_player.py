import random
import uuid
from datemi.carcassonne.game.player import Player
from datemi.carcassonne.shared.com.playertype import PlayerType
from datemi.carcassonne.shared.objects.actions.action import Action
from datemi.carcassonne.shared.objects.game_state.game_state import GameState

# Tis player is there for reference so you can play against it
class RandomPlayer(Player):
    def __init__(self, name, debug=False, core_number=1):
        id = uuid.uuid4()
        super().__init__(id, name, PlayerType.AI)