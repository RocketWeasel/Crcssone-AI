import random
import uuid
from datemi.carcassonne.game.player import Player
from datemi.carcassonne.shared.com.playertype import PlayerType
from datemi.carcassonne.shared.objects import side
from datemi.carcassonne.shared.objects.actions.action import Action
from datemi.carcassonne.shared.objects.actions.mpl_action import MplAction
from datemi.carcassonne.shared.objects.actions.tile_action import TileAction
from datemi.carcassonne.shared.objects.actions.pass_action import PassAction
from datemi.carcassonne.shared.objects.game_phase import GamePhase
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.terrain_type import TerrainType
from datemi.carcassonne.shared.utils.sim import SimStateUtil, SimFeatureUtil, SimFeatureMplUtil


class MyPlayer(Player):
    def __init__(self, name):
        # Player initialization
        id = uuid.uuid4()
        super().__init__(id, name, PlayerType.AI)
        # Add your own initialization code here

        """
        our own make step function
        :param player_no: The player number of the player who is asked for an action.
        :param game_state: The current game state.
        :param actionlist: A list of possible actions.
        :return: The index of the action in the actionlist that should be performed.
        """
    "def make_step(self, player_no: int, game_state: GameState, actionlist: list[Action]) -> int:"


    def make_step(self, player_no: int, game_state: GameState, actionlist: list[Action]) -> int:
        """
        This function is called by the game engine to ask the player for an action.
        :param player_no: The player number of the player who is asked for an action.
        :param game_state: The current game state.
        :param actionlist: A list of possible actions.
        :return: The index of the action in the actionlist that should be performed.
        """

        phase = game_state.phase
        if phase == GamePhase.TILES:
            for i, action in enumerate(actionlist):
                if isinstance(action, TileAction):
                    tile_action: TileAction = action
                    result = SimStateUtil.apply_tile_action(game_state, player_no, tile_action)
                    features = result.get_features_by_pos(tile_action.coordinate)
                    for feature in features:
                        if feature.finished and feature.feature_type in [TerrainType.CITY, TerrainType.ROAD, TerrainType.CHAPEL]:
                            if max(feature.mpl_points) == 0:
                                return i


        if phase == GamePhase.MPLS:
            for i, action in enumerate(actionlist):
                if isinstance(action, MplAction):
                    mpl_action: MplAction = action
                    coordinate = mpl_action.coordinate_with_side
                    features = game_state.get_features_by_pos(coordinate)
                    for feature in features:
                        if feature.finished and not feature.scored:
                            if coordinate in feature.coordinates:
                                return i


        selected = random.randint(0, len(actionlist)-1)
        return selected