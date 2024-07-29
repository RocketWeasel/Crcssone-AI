import random
import uuid
from datemi.carcassonne.game.player import Player
from datemi.carcassonne.shared.com.playertype import PlayerType
from datemi.carcassonne.shared.objects import mplType, Coordinate, Tile
from datemi.carcassonne.shared.objects.actions import PassAction
from datemi.carcassonne.shared.objects.actions.action import Action
from datemi.carcassonne.shared.objects.actions.mpl_action import mplAction
from datemi.carcassonne.shared.objects.actions.tile_action import TileAction
from datemi.carcassonne.shared.objects.feature import FeatureSet
from datemi.carcassonne.shared.objects.game_phase import GamePhase
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.terrain_type import TerrainType
from datemi.carcassonne.shared.utils.sim import SimStateUtil, SimFeatureUtil, SimFeaturemplUtil
from ai.my_ai.decision_calc_mpl import mplDecisions
from ai.my_ai.decision_calc_tile import TileDecisions


def filter_flower_chapel(features: FeatureSet, tile_action: TileAction) -> FeatureSet:
    coord = tile_action.coordinate
    chapel_flowers = []
    res: FeatureSet = FeatureSet()
    for feature in features:
        if feature.feature_type == TerrainType.CHAPEL or feature.feature_type == TerrainType.FLOWERS:
            chapel_flowers.append(feature)
        else:
            res.append(feature)
    for x in chapel_flowers:
        xy_coord = x.coordinates[0].to_coordinate()
        if coord.__eq__(xy_coord):
            res.append(x)
    return res


class MyPlayer(Player):
    def __init__(self, name, debug=False):
        # Player initialization
        id = uuid.uuid4()
        self.debug = debug
        super().__init__(id, name, PlayerType.AI)
        # Add your own initialization code here

    def make_step(self, player_no: int, game_state: GameState, actionlist: list[Action]) -> int:
        """
        This function is called by the game engine to ask the player for an action.
        :param player_no: The player number of the player who is asked for an action.
        :param game_state: The current game state.
        :param actionlist: A list of possible actions.
        :return: The index of the action in the actionlist that should be performed.
        """
        # if self.debug:
        #     print(f'mpls in der Hand: {game_state.mpls[player_no]} '
        #           f'Abbots in Hand: {game_state.abbots[player_no]} '
        #           f'Biggies in Hand: {game_state.big_mpls[player_no]} '
        #           f'mpls im Spiel:{len(game_state.placed_mpls[player_no])}')

        #print("------------------------------")
        #print(f' Current Turn of Our Ai: {game_state.turn_number/game_state.players}')
        phase = game_state.phase
        if phase == GamePhase.TILES:
            #print("tile phase")
            for i, action in enumerate(actionlist):
                if isinstance(action, TileAction):
                    tile_action: TileAction = action
                    result = SimStateUtil.apply_tile_action(game_state, player_no, tile_action)
                    features = result.get_features_by_pos(tile_action.coordinate)
                    real_features = filter_flower_chapel(features, tile_action)
                    for feature in real_features:
                        TileDecisions.decide_tile_by_features(player_no, result, game_state, tile_action, i, feature)

            if len(TileDecisions.t_decisionList) > 0:
                return TileDecisions.get_best_tile()

        pass_index = 0
        if phase == GamePhase.mplS:
            str_list = []
            #print("mpl face")
            for i, action in enumerate(actionlist):
                if isinstance(action, PassAction):
                    pass_index = i
                if isinstance(action, mplAction):
                    str_list.append(action.mpl_type)
                    mpl_action: mplAction = action
                    coordinate = mpl_action.coordinate_with_side
                    features = game_state.get_features_by_pos(coordinate)
                    for feature in features:
                        mplDecisions.decide_mpl_by_features(player_no, game_state, mpl_action, i, feature,
                                                                  coordinate)
            #print(str_list)

            if len(mplDecisions.m_decisionList) > 0:
                return mplDecisions.get_best_mpl()
            return pass_index

        selected = random.randint(0, len(actionlist) - 1)
        return selected