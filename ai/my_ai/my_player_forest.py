import uuid

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from ai.my_ai.training_data_tile import TileTrainingData
from ai.my_ai.training_data_mpl import mplTrainingData
from ai.my_ai.universal_calc import less_open_edges, reigning_player, has_mpl_on_street, get_point_difference
from datemi.carcassonne.game.player import Player
from datemi.carcassonne.shared.com.playertype import PlayerType
from datemi.carcassonne.shared.objects.actions import PassAction
from datemi.carcassonne.shared.objects.actions.action import Action
from datemi.carcassonne.shared.objects.actions.mpl_action import mplAction
from datemi.carcassonne.shared.objects.actions.tile_action import TileAction
from datemi.carcassonne.shared.objects.game_phase import GamePhase
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.feature import Feature
import paths as env
import joblib as jb

from datemi.carcassonne.shared.utils.sim import SimStateUtil


class MyPlayerRandomForest(Player):
    def __init__(self, name, debug=False, core_number=1):
        # Player initialization
        self.debug = debug
        # Tile Tree loading
        #self.loaded_model_tile_entropy = jb.load(env.TILE_ENTROPY_FOREST_PATH)
        self.loaded_model_tile_gini = jb.load(env.TILE_GINI_FOREST_PATH)

        # mpl Tree loading
        #self.loaded_model_mpl_entropy = jb.load(env.mpl_ENTROPY_FOREST_PATH)
        self.loaded_model_mpl_gini = jb.load(env.MPL_GINI_FOREST_PATH)

        super().__init__(uuid.uuid4(), name, PlayerType.AI)

    def make_mpl_prediction(self, move_data: list, mode="gini"):
        if mode == "entropy":
            loaded_model: RandomForestClassifier = self.loaded_model_mpl_entropy
        elif mode == "gini":
            loaded_model: RandomForestClassifier = self.loaded_model_mpl_gini
        else:
            print("No Valid Mode or Model, Closing Program")
            return
        return loaded_model.predict([move_data])

    def make_tile_prediction(self, move_data: list, mode="gini"):
        if mode == "entropy":
            loaded_model: RandomForestClassifier = self.loaded_model_tile_entropy
        elif mode == "gini":
            loaded_model: RandomForestClassifier = self.loaded_model_tile_gini
        else:
            print("No Valid Mode or Model, Closing Program")
            return

        return loaded_model.predict([move_data])

    def make_step(self, player_no: int, game_state: GameState, actionlist: list[Action]) -> int:

        """
        This function is called by the game engine to ask the player for an action.
        :param player_no: The player number of the player who is asked for an action.
        :param game_state: The current game state.
        :param actionlist: A list of possible actions.
        :return: The index of the action in the actionlist that should be performed.
        """
        phase = game_state.phase
        predictions = []
        if phase == GamePhase.TILES:
            for i, action in enumerate(actionlist):
                if isinstance(action, PassAction):
                    predictions.append((i, 0))
                if isinstance(action, TileAction):
                    # do something here make_prediction
                    tile_action = action
                    result = SimStateUtil.apply_tile_action(game_state, player_no, tile_action)
                    features: [Feature] = result.get_features_by_pos(tile_action.coordinate)
                    endgame = (game_state.turn_number / game_state.players) + game_state.mpls[player_no] >= (102 / game_state.players)
                    for feature in features:
                        point_difference_var = 0
                        less_open_edges_var = 0
                        if reigning_player(player_no, feature):
                            point_difference_var = get_point_difference(game_state, result, feature)
                            less_open_edges_var = less_open_edges(game_state, result, feature)
                        data = {'remaining_mpl': int(result.mpls[player_no]),
                                'remaining_abbots': int(result.abbots[player_no]),
                                'feature_finished': int(feature.finished),
                                'terrain_type': int(feature.feature_type),
                                'reigning_player': int(reigning_player(player_no=player_no, feature=feature)),
                                'is_end_farmer_time': int(endgame),
                                'feature_mpl_points': int(max(feature.mpl_points)),
                                'feature_possible_points': int(feature.possible_points),
                                'feature_point_difference': int(point_difference_var),
                                'feature_less_open_edges': int(less_open_edges_var),
                                'feature_mpl_on_street': int(has_mpl_on_street(player_no=player_no, game_state=game_state))}
                        validate = TileTrainingData(data)
                        validate.check_data(True)
                        predictions.append((i, self.make_tile_prediction(validate.get_list_without_selected())))
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions[0][0]

        # implement mpl predictions here

        phase = game_state.phase
        if phase == GamePhase.mplS:
            for i, action in enumerate(actionlist):
                if isinstance(action, PassAction):
                    predictions.append((i, 0))
                    continue
                if isinstance(action, mplAction):
                    # do something here make_prediction
                    mpl_action = action
                    feature: Feature = game_state.get_feature_by_pos(mpl_action.coordinate_with_side)

                    endgame = (game_state.turn_number / game_state.players) + game_state.mpls[player_no] >= (102 / game_state.players)
                    data = {'remaining_mpl': int(game_state.mpls[player_no]),
                            'remaining_abbots': int(game_state.abbots[player_no]),
                            'feature_finished': int(feature.finished),
                            'terrain_type': int(feature.feature_type),
                            'is_end_farmer_time': int(endgame),
                            'feature_possible_points': int(feature.possible_points),
                            'feature_mpl_on_street': int(has_mpl_on_street(player_no=player_no, game_state=game_state))}
                    validate = mplTrainingData(data)
                    validate.check_data(True)
                    predictions.append((i, self.make_mpl_prediction(validate.get_list_without_selected())))
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions[0][0]
