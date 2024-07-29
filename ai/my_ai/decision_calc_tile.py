from ai.my_ai.training_data_tile import TileTrainingData
from datemi.carcassonne.shared.objects import CoordinateWithSide, Side
from datemi.carcassonne.shared.objects.feature import Feature
from datemi.carcassonne.shared.objects.actions.tile_action import TileAction
from datemi.carcassonne.shared.objects.game_state.game_state import GameState
from datemi.carcassonne.shared.objects.terrain_type import TerrainType
import ai.my_ai.universal_calc as universal_calc


def get_edge_coordinates_with_side(open_edge: CoordinateWithSide) -> (CoordinateWithSide, CoordinateWithSide):
    if open_edge.side == Side.LEFT:
        return (CoordinateWithSide(open_edge.row + 1, open_edge.column - 1, Side.TOP),
                CoordinateWithSide(open_edge.row - 1, open_edge.column - 1, Side.BOTTOM))

    elif open_edge.side == Side.TOP:
        return (CoordinateWithSide(open_edge.row + 1, open_edge.column - 1, Side.RIGHT),
                CoordinateWithSide(open_edge.row + 1, open_edge.column + 1, Side.LEFT))

    elif open_edge.side == Side.RIGHT:
        return (CoordinateWithSide(open_edge.row + 1, open_edge.column + 1, Side.TOP),
                CoordinateWithSide(open_edge.row - 1, open_edge.column + 1, Side.BOTTOM))

    else:
        return (CoordinateWithSide(open_edge.row - 1, open_edge.column + 1, Side.LEFT),
                CoordinateWithSide(open_edge.row - 1, open_edge.column - 1, Side.RIGHT))


"""Checks, if the feature we are looking at has the same feature on corner tile or not"""


def feature_on_edge_tiles(self, feature: Feature, game_state: GameState, action: TileAction) -> Feature | None:
    edges: list[CoordinateWithSide] = []

    for edge in feature.open_edges:
        if (edge.row == action.coordinate.row
                and edge.column == action.coordinate.column
                and edge.side in [Side.TOP, Side.BOTTOM, Side.LEFT, Side.RIGHT]):
            edges.append(edge)

    if edges.__len__() == 0:
        return None
    else:
        for edge in edges:
            edge_tile_tuple = get_edge_coordinates_with_side(edge)
            coord1 = edge_tile_tuple[0]
            coord2 = edge_tile_tuple[1]

            if (game_state.get_tile(coord1.row, coord1.column)) is not None:
                return game_state.get_feature_by_pos(coord1)

            if game_state.get_tile(coord2.row, coord2.column) is not None:
                return game_state.get_feature_by_pos(coord2)

        return None


class TileDecisions:

    def __init__(self):
        self.t_decisionList = []

    """Sorts by weighting and displays the top index with the highest weighting"""

    def get_best_tile(self):
        sorted_decisions = sorted(self.t_decisionList, key=lambda x: x[1], reverse=True)
        # print(sorted_decisions)
        # print(f'Tile:{sorted(cls.t_decisionList, key=lambda x: x[1], reverse=True)}')
        self.t_decisionList.clear()
        return sorted_decisions[0]

    """class, which analyzes the featurues with the action from the actionlist and thus puts the best tile move 
        into the list:

        Args:
            player_no (int): Player number
            game_state (GameState): game state of the game
            action (TileAction): the action we want to evaluate
            feature (Feature): Evaluation of the feature states, when placing the tile
            index (int): the move index to which we assign the rating/weighting
    """

    def decide_tile_by_features(self, player_no: int, result: GameState, game_state: GameState, action: TileAction,
                                index: int, feature: Feature, feature_id: int) -> None:
        endgame = (game_state.turn_number / game_state.players) + game_state.mpls[player_no] >= (102 / game_state.players)
        reigning_player = universal_calc.reigning_player(player_no, feature)
        point_difference = 0
        less_open_edges = 0
        if reigning_player:
            point_difference = universal_calc.get_point_difference(game_state, result, feature)
            less_open_edges = universal_calc.less_open_edges(game_state, result, feature)
        mpl_on_street = universal_calc.has_mpl_on_street(player_no, game_state)
        remaining_mpl = game_state.mpls[player_no]
        remaining_abbots = game_state.abbots[player_no]
        weight = 0
        # Finished Features
        if (feature.finished and
                (feature.feature_type in [TerrainType.CITY, TerrainType.ROAD, TerrainType.FLOWERS, TerrainType.CHAPEL])):

            if remaining_mpl == 0 and reigning_player:
                if feature.cathedral:
                    weight = 100 + feature.possible_points
                else:
                    weight = 60 + feature.possible_points

            elif reigning_player:
                if feature.cathedral:
                    weight = 100 + feature.possible_points
                else:
                    weight = 50 + feature.possible_points

            elif max(feature.mpl_points) == 0:
                if feature.cathedral:
                    weight = 100 + feature.possible_points
                else:
                    weight = 50 + feature.possible_points

        # Not Finished Features
        elif not feature.finished:

            # City
            if feature.feature_type == TerrainType.CITY:

                if max(feature.mpl_points) == 0:
                    weight = 35 + feature.possible_points
                elif reigning_player:
                    if less_open_edges:
                        if feature.cathedral:
                            weight = 50 + point_difference
                    else:
                        weight = 30 + point_difference

            # Road
            elif feature.feature_type == TerrainType.ROAD:
                if max(feature.mpl_points) == 0:
                    if not mpl_on_street:
                        weight = 35 + feature.possible_points
                elif reigning_player:
                    weight = 35 + point_difference

            # Flowers
            elif feature.feature_type in [TerrainType.FLOWERS]:
                if remaining_abbots == 0:
                    return
                weight = 35 + feature.possible_points

            # Chapel
            elif feature.feature_type in [TerrainType.CHAPEL]:
                weight = 35 + feature.possible_points

            # Grass
            elif feature.feature_type == TerrainType.GRASS:
                if max(feature.mpl_points) == 0:
                    if (game_state.turn_number / game_state.players) + game_state.mpls[player_no] >= (102 / game_state.players) and feature.possible_points >= 3:
                        weight = 35 + feature.possible_points

        data_without_selected = TileTrainingData({'remaining_mpl': remaining_mpl, 'remaining_abbots': remaining_abbots,
                                              'feature_finished': feature.finished, 'terrain_type': feature.feature_type.to_dict(),
                                              'reigning_player': reigning_player, 'is_end_farmer_time': endgame,
                                              'feature_mpl_points': max(feature.mpl_points), 'feature_possible_points': feature.possible_points,
                                              'feature_point_difference': point_difference, 'feature_less_open_edges': less_open_edges,
                                              'feature_mpl_on_street': mpl_on_street})

        self.t_decisionList.append((index, weight, feature_id, data_without_selected))
