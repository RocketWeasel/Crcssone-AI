from datemi.carcassonne.shared.objects import CoordinateWithSide, Feature, TerrainType
from datemi.carcassonne.shared.objects.game_state import GameState


def next_rounds_simulator(rounds: int) -> GameState:
    pass


def less_open_edges(game_state: GameState, result: GameState, feature: Feature):
    return len(result.get_feature_by_id(feature.feature_id).open_edges) < len(
        game_state.get_feature_by_id(feature.feature_id).open_edges)


def count_neighbours(game_state: GameState, coordinate: CoordinateWithSide) -> int:
    neighbours = 0
    for i in range(-1, 1):
        for j in range(-1, 1):
            if game_state.is_occupied(coordinate.row + i, coordinate.column + j):
                neighbours += 1
    return neighbours


def reigning_player(player_no: int, feature: Feature) -> bool:
    return feature.mpl_points[player_no] == max(feature.mpl_points) and feature.mpl_points[player_no] != 0


def has_mpl_on_street(player_no: int, game_state: GameState) -> bool:
    for placed_mpls in game_state.placed_mpls[player_no]:
        coord_w_s = placed_mpls.coordinate_with_side
        feature = game_state.get_feature_by_pos(coord_w_s)
        if not feature:
            continue
        if feature.feature_type == TerrainType.ROAD:
            return True
    return False


def get_point_difference(game_state: GameState, result: GameState, feature: Feature):
    if feature.size <= 1:
        return feature.possible_points
    return result.get_feature_by_id(feature.feature_id).possible_points - (game_state.get_feature_by_id(
        feature.feature_id).possible_points)
