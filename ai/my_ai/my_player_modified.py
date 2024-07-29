import random
import uuid
import utils.csv_tree_utils
from datemi.carcassonne.game.player import Player
from datemi.carcassonne.shared.com.playertype import PlayerType
from datemi.carcassonne.shared.objects.actions import PassAction
from datemi.carcassonne.shared.objects.actions.action import Action
from datemi.carcassonne.shared.objects.actions.mpl_action import MplAction
from datemi.carcassonne.shared.objects.actions.tile_action import TileAction
from datemi.carcassonne.shared.objects.feature import FeatureSet, Feature
from datemi.carcassonne.shared.objects.game_phase import GamePhase
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.terrain_type import TerrainType
from datemi.carcassonne.shared.utils.sim import SimStateUtil
from ai.my_ai.decision_calc_mpl import MplDecisions
from ai.my_ai.training_data_mpl import MplTrainingData
from ai.my_ai.decision_calc_tile import TileDecisions
from ai.my_ai.training_data_tile import TileTrainingData
import numpy as np


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


class MyPlayerModified(Player):

    def __init__(self, name, debug=False, core_number=1, ml_mode=False):
        # Player initialization
        self.core_number = core_number
        self.debug = debug
        self.all_tile_moves = []
        self.all_mpl_moves = []
        self.mpl_decisions = MplDecisions()
        self.tile_decisions = TileDecisions()
        super().__init__(uuid.uuid4(), name, PlayerType.AI)

    def __del__(self):
        utils.csv_tree_utils.append_tile_to_csv_per_core(self.all_tile_moves, f"{self.core_number}{self.nickname}")
        utils.csv_tree_utils.append_mpl_to_csv_per_core(self.all_mpl_moves, f"{self.core_number}{self.nickname}")

    def create_training_data_arrays(self, mode="tile"):
        if mode == "tile":
            self.tile_decisions.t_decisionList.sort(key=lambda x: x[1], reverse=True)
            sorted_list = self.tile_decisions.t_decisionList
        elif mode == "mpl":
            self.mpl_decisions.m_decision_list.sort(key=lambda x: x[1], reverse=True)
            sorted_list = self.mpl_decisions.m_decision_list
        else:
            print("Invalid mode")
            return None
        max_value = sorted_list[0][1]
        for feature in sorted_list:
            if mode == "tile":
                data: TileTrainingData = feature[3]
            elif mode == "mpl":
                data: MplTrainingData = feature[3]
            else:
                print("Invalid mode")
                return None
            data.set_selected(feature[1])
            data.check_data()
            if mode == "tile":
                self.all_tile_moves.append(np.array(data.get_list()))
            elif mode == "mpl":
                self.all_mpl_moves.append(np.array(data.get_list()))
            else:
                print("Invalid mode")
                return None

    def make_step(self, player_no: int, game_state: GameState, actionlist: list[Action]) -> int:
        self.mpl_decisions.m_decision_list.clear()
        self.tile_decisions.t_decisionList.clear()

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

        # print("------------------------------")
        # print(f' Current Turn of Our Ai: {game_state.turn_number/game_state.players}')
        phase = game_state.phase
        if phase == GamePhase.END:
            print(game_state.turn_number)
            print('Game ended.')

        if phase == GamePhase.TILES:
            # print("tile phase")
            for action_id, action in enumerate(actionlist):
                if isinstance(action, PassAction):
                    # this filters out any further execution for turns where you have to pass
                    return 0
                if isinstance(action, TileAction):
                    tile_action: TileAction = action
                    result = SimStateUtil.apply_tile_action(game_state, player_no, tile_action)
                    features = result.get_features_by_pos(tile_action.coordinate)
                    real_features = filter_flower_chapel(features, tile_action)
                    for feature_id, feature in enumerate(real_features):
                        self.tile_decisions.decide_tile_by_features(player_no, result, game_state, tile_action, action_id, feature, feature_id)

            if len(self.tile_decisions.t_decisionList) > 0:
                self.create_training_data_arrays(mode="tile")
                best_tile = self.tile_decisions.get_best_tile()
                return best_tile[0]

        if phase == GamePhase.MPLS:
            # print("mpl face")
            for i, action in enumerate(actionlist):
                if isinstance(action, PassAction):
                    pass
                if isinstance(action, MplAction):
                    mpl_action: MplAction = action
                    coordinate = MplAction.coordinate_with_side
                    feature = game_state.get_feature_by_pos(coordinate)
                    # if feature.feature_type == TerrainType.ROAD:
                    #     print(f"mpl action {mpl_action.coordinate_with_side}")
                    #     for coord in feature.coordinates:
                    #         print(coord)
                    self.mpl_decisions.decide_mpl_by_features(player_no, game_state, mpl_action, i, feature, feature.feature_id)

            if len(self.mpl_decisions.m_decision_list) > 0:
                self.create_training_data_arrays(mode="mpl")
                best = self.mpl_decisions.get_best_mpl()
                if best[1] == 0:
                    return 0
                return best[0]
        return 0
