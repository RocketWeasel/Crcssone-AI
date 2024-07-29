import env

# Path to all Training Data
TRAINING_DATA_PATH = env.ABSOLUTE_PATH_TO_PROJECT + "training_data/"

# Path to CVS-Data
CSV_TILE = TRAINING_DATA_PATH + "csv/tile/"
PROCESSED_TILE_CSV_PATH = CSV_TILE + "processed.csv"
COMBINED_TILE_CSV_PATH = CSV_TILE + "combined_data.csv"
TILE_CSV_PER_CORE_PATH = CSV_TILE + "csv_per_core/"

CSV_MPL = TRAINING_DATA_PATH + "csv/mpl/"
PROCESSED_MPL_CSV_PATH = CSV_MPL + "processed.csv"
COMBINED_MPL_CSV_PATH = CSV_MPL + "combined_data.csv"
MPL_CSV_PER_CORE_PATH = CSV_MPL + "csv_per_core/"


# Path to Model Data
TREE_FOLDER_PATH = TRAINING_DATA_PATH + "ai/my_ai/tree_models/"
FOREST_FOLDER_PATH = TRAINING_DATA_PATH + "ai/my_ai/forest_models/"


TILE_TREE_PATH = TREE_FOLDER_PATH + "tile/"
TILE_ENTROPY_TREE_PATH = TILE_TREE_PATH + "entropy_decision_tree_model.jb"
TILE_GINI_TREE_PATH = TILE_TREE_PATH + "gini_decision_tree_model.jb"

MPL_TREE_PATH = TREE_FOLDER_PATH + "mpl/"
MPL_ENTROPY_TREE_PATH = MPL_TREE_PATH + "entropy_decision_tree_model.jb"
MPL_GINI_TREE_PATH = MPL_TREE_PATH + "gini_decision_tree_model.jb"


TILE_FOREST_PATH = FOREST_FOLDER_PATH + "tile/"
TILE_ENTROPY_FOREST_PATH = TILE_FOREST_PATH + "entropy_decision_forest_model.jb"
TILE_GINI_FOREST_PATH = TILE_FOREST_PATH + "gini_decision_forest_model.jb"

MPL_FOREST_PATH = FOREST_FOLDER_PATH + "mpl/"
MPL_ENTROPY_FOREST_PATH = MPL_FOREST_PATH + "entropy_decision_forest_model.jb"
MPL_GINI_FOREST_PATH = MPL_FOREST_PATH + "gini_decision_forest_model.jb"


