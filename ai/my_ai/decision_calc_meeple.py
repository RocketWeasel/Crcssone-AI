from datemi.carcassonne.shared.objects import CoordinateWithSide
from datemi.carcassonne.shared.objects.feature import Feature
from datemi.carcassonne.shared.objects.actions.mpl_action import mplAction
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.terrain_type import TerrainType
import ai.my_ai.universal_calc as universal_calc
from ai.my_ai.training_data_mpl import mplTrainingData
from datemi.carcassonne.shared.objects.mpl_type import mplType

"""Decision class for the implementation of algorithms, for calculating the best decisions from a
     created decision list for mpl and tile moves:
 
 Args:
    t_decisionList (list): List with tuples from the received index and the value of the weighting calculated by us
    m_decisionList (list): Same list only for the mpl decision class
 """


class mplDecisions:

    def __init__(self):
        self.count = 0
        self.m_decision_list = []

    """Sorts by weighting and displays the top index with the highest weighting"""
    def get_best_mpl(self):
        self.m_decision_list.sort(key=lambda x: x[1], reverse=True)
        return self.m_decision_list[0]

    """class, which analyzes the features with the action from the actionlist and thus puts the best mpl moves 
        in front of the list:
        
        Args:
            player_no (int): Player number
            game_state (GameState): state of Game
            action (mplAction): the action we want to evaluate
            feature (Feature): Evaluation of the feature states, when placing the mpl
            index (int): the move index to which we assign the rating/weighting
    """
    def decide_mpl_by_features(self, player_no: int, game_state: GameState, action: mplAction,
                                  index: int, feature: Feature, feature_id: int):

        endgame = (game_state.turn_number / game_state.players) + game_state.mpls[player_no] >= (
                102 / game_state.players)
        remaining_mpl = game_state.mpls[player_no]
        remaining_abbots = game_state.abbots[player_no]
        feature_mpl_on_street = universal_calc.has_mpl_on_street(player_no, game_state)
        first_round = game_state.turn_number == 0
        weight = 0

        data_without_selected = mplTrainingData({
            'remaining_mpl': remaining_mpl,
            'remaining_abbots': remaining_abbots,
            'feature_finished': feature.finished,
            'terrain_type': feature.feature_type.to_dict(),
            'is_end_farmer_time': endgame,
            'feature_possible_points': feature.possible_points,
            'feature_mpl_on_street': feature_mpl_on_street
        })

         # Farm decisions
        if feature.feature_type == TerrainType.GRASS:
            if first_round:
                weight = 100
            # if endgame:
            #     weight = 20 + feature.possible_points


        # Finished
        if feature.finished:

            # City Finished
            if feature.feature_type == TerrainType.CITY:
                weight = 50 + feature.possible_points

            # Road finished
            elif feature.feature_type.ROAD:
                weight = 50 + feature.possible_points

            # Chapel finished
            elif feature.feature_type == TerrainType.CHAPEL:
                if game_state.abbots[player_no] == 1:
                    weight = 60
                else:
                    weight = 65

            # Flowers Finished
            elif feature.feature_type == TerrainType.FLOWERS:
                if game_state.abbots[player_no] == 1:
                    weight = 65

        # Not finished
        elif not feature.finished:

            if feature.possible_points > 5 and (feature.inn and len(feature.open_edges) == 1):
                weight = 30
            elif feature.possible_points > 5:
                weight = 30


            # City decisions
            if feature.feature_type == TerrainType.CITY:
                if game_state.mpls[player_no] > 3:
                    weight = 30 + feature.possible_points

            # Road
            elif feature.feature_type == TerrainType.ROAD:
                # for mpls in game_state.placed_mpls[player_no]:
                    # print(f'mpl: {game_state.get_feature_by_pos(mpls.to_dict().get("coordinate_with_side")).feature_type} in runde: {game_state.turn_number}')
                if not universal_calc.has_mpl_on_street(player_no, game_state) and not len(feature.open_edges) == 0:
                    weight = 10
                else:
                    weight = 0

            # Chapel
            elif feature.feature_type == TerrainType.CHAPEL:
                if action.mpl_type == mplType.ABBOT:
                    weight = 35 + feature.possible_points
                elif action.mpl_type == mplType.NORMAL:
                    weight = 40 + feature.possible_points

            # Flowers
            elif feature.feature_type == TerrainType.FLOWERS:
                if action.remove and feature.possible_points > 5:
                    weight = 1
                else:
                    weight = 40 + feature.possible_points

        self.m_decision_list.append((index, weight, feature_id, data_without_selected))
