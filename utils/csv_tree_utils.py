import csv
import os.path
import time
import pandas as pd
import polars
import paths as env
import joblib as jb

import utils.file_utils
from utils.file_utils import find_file_names
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from ai.my_ai.training_data_tile import TileTrainingData
from ai.my_ai.training_data_mpl import MplTrainingData

'''Tile Training Data Paths'''
tile_csv_per_core_path = env.TILE_CSV_PER_CORE_PATH
tile_combined_csv = env.COMBINED_TILE_CSV_PATH
tile_processed_csv = env.PROCESSED_TILE_CSV_PATH

'''mpl Training Data Paths'''
mpl_csv_per_core_path = env.MPL_CSV_PER_CORE_PATH
mpl_combined_csv = env.COMBINED_MPL_CSV_PATH
mpl_processed_csv = env.PROCESSED_MPL_CSV_PATH

tile_headers = TileTrainingData.HEADERS
mpl_headers = MplTrainingData.HEADERS



def test_if_exists(path):
    if os.path.isfile(path):
        return True
    else:
        return False


def csv_to_df(filename):
    return pd.read_csv(filename)


def init_csv(path, mode: str):
    # the header that should exist in the csvs
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        if mode == 't':
            writer.writerow(tile_headers)
        elif mode == 'm':
            writer.writerow(mpl_headers)
        else:
            print("Did not initialise csv because no mode specified")


def append_tile_to_csv_per_core(move_list, core_number):
    path = f"{tile_csv_per_core_path}{core_number}.csv"
    if not test_if_exists(path):
        init_csv(path, 't')
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for move_array in move_list:
            writer.writerow(move_array)


def append_mpl_to_csv_per_core(move_list, core_number):
    path = f"{mpl_csv_per_core_path}{core_number}.csv"
    if not test_if_exists(path):
        init_csv(path, 'm')
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for move_array in move_list:
            writer.writerow(move_array)


def generate_combined_csv():
    # load the csvs per core
    tile_csvs_file_names = find_file_names(tile_csv_per_core_path, ext="csv")
    mpl_csvs_file_names = find_file_names(mpl_csv_per_core_path, ext="csv")

    if not tile_csvs_file_names or not mpl_csvs_file_names:
        print("Can't combine nothing!")
        return

    # create a csv with header
    print(f"combining {len(tile_csvs_file_names)} tile training-files into one")
    print(f"combining {len(mpl_csvs_file_names)} mpl training-files into one")

    # add the tile data to it
    dataframes = [pd.read_csv(csv_file, header=0) for csv_file in tile_csvs_file_names]
    df = pd.concat(dataframes, ignore_index=True)
    print(f"tile-file is {len(df)} rows long")
    df.to_csv(tile_combined_csv, index=False)

    # add the mpl data to it
    dataframes = [pd.read_csv(csv_file, header=0) for csv_file in mpl_csvs_file_names]
    df = pd.concat(dataframes, ignore_index=True)
    print(f"mpl-file is {len(df)} rows long")
    df.to_csv(mpl_combined_csv, index=False)


def generate_combined_csv_polars(mode="tile"):
    match mode:
        case 'tile':
            path = tile_csv_per_core_path
            out_path = tile_combined_csv
        case 'mpl':
            path = mpl_csv_per_core_path
            out_path = mpl_combined_csv
        case _:
            print("Wrong move!")
            return

    # load the csvs per core
    csvs_file_names = find_file_names(path, ext="csv")

    if not csvs_file_names:
        print("Can't combine nothing!")
        return
    # create a csv with header
    print(f"combining {len(csvs_file_names)}-{mode} training-files into 1")

    # add the data to it
    # tile_dataframes = [polars.read_csv(csv_file).group_by(tile_headers).len(name="occurrence_count") for csv_file in tile_csvs_file_names]
    dataframes = [polars.read_csv(csv_file) for csv_file in csvs_file_names]
    df = polars.concat(dataframes)
    df.write_csv(out_path)
    # df = df.group_by(tile_headers).agg(polars.col("occurrence_count").sum())
    # df_sorted = df.sort(by='occurrence_count', descending=True)
    # print(f"new sorted {mode}-file is {len(df_sorted)} rows long")
    # df_sorted.write_csv(out_path)


def aggregate_labels():
    # aggregate for tile-files
    t_df = polars.read_csv(tile_combined_csv)

    print(f"Length of non-processed tile-file {len(t_df)}")
    t_df = t_df.unique(tile_headers[:-2], keep='first', maintain_order=True)
    t_df = t_df.drop('occurrence_count')
    t_df.write_csv(tile_processed_csv)
    print(f"Length of processed tile-file: {len(t_df)}")
    print(t_df)

    # aggregate for mpl files
    m_df = polars.read_csv(mpl_combined_csv)

    print(f"Length of non-processed mpl-file {len(m_df)}")
    m_df = m_df.unique(mpl_headers[:-2], keep='first', maintain_order=True)
    m_df = m_df.drop('occurrence_count')
    m_df.write_csv(mpl_processed_csv)
    print(f"Length of processed mpl-file: {len(m_df)}")
    print(m_df)


def tree_and_forest_creation(mode):
    match mode:
        case 'tile':
            path = tile_combined_csv
            out_path_tree_entropy = env.TILE_ENTROPY_TREE_PATH
            out_path_tree_gini = env.TILE_GINI_TREE_PATH

            out_path_forest_entropy = env.TILE_ENTROPY_FOREST_PATH
            out_path_forest_gini = env.TILE_GINI_FOREST_PATH

        case 'mpl':
            path = mpl_combined_csv
            out_path_tree_entropy = env.MPL_ENTROPY_TREE_PATH
            out_path_tree_gini = env.MPL_GINI_TREE_PATH

            out_path_forest_entropy = env.MPL_ENTROPY_FOREST_PATH
            out_path_forest_gini = env.MPL_GINI_FOREST_PATH
        case _:
            print("Wrong move!")
            return

    cropped_file = pd.read_csv(path, sep=',', header=0)

    #train tile-Data tree
    print(f'Train {mode}-Tree with {len(cropped_file)}')
    print(cropped_file.info)
    X = cropped_file.values[:, 0:-1]
    Y = cropped_file.values[:, -1]

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=100)

    # Gini_Tree
    tree_with_gini = DecisionTreeClassifier(criterion='gini', random_state=100)
    tree_with_gini.fit(x_train, y_train)
    jb.dump(tree_with_gini, out_path_tree_gini)
    tree_gini_predictions = tree_with_gini.predict(x_test)
    accuracy_tree_gini = accuracy_score(y_test, tree_gini_predictions) * 100

    # Entropy Tree_Tree
    tree_with_entropy = DecisionTreeClassifier(criterion='entropy', random_state=100)
    tree_with_entropy.fit(x_train, y_train)
    jb.dump(tree_with_entropy, out_path_tree_entropy)
    tree_entropy_predictions = tree_with_entropy.predict(x_test)
    accuracy_tree_entropy = accuracy_score(y_test, tree_entropy_predictions) * 100

     # Gini_Forest
    forest_with_gini = RandomForestClassifier(criterion='gini', random_state=100)
    forest_with_gini.fit(x_train, y_train)
    jb.dump(forest_with_gini, out_path_forest_gini)
    forest_gini_predictions = forest_with_gini.predict(x_test)
    accuracy_forest_gini = accuracy_score(y_test, forest_gini_predictions) * 100

    # Entropy_Forest
    forest_with_entropy = RandomForestClassifier(criterion='entropy', random_state=100)
    forest_with_entropy.fit(x_train, y_train)
    jb.dump(forest_with_entropy, out_path_forest_entropy)
    forest_entropy_predictions = forest_with_entropy.predict(x_test)
    accuracy_forest_entropy = accuracy_score(y_test, forest_entropy_predictions) * 100

    print(f"{mode}-Accuracy with Entropy Tree:", accuracy_tree_entropy)
    print(f"{mode}-Accuracy with Gini Tree:", accuracy_tree_gini)
    print("-------------------------------------------------------")
    print(f"{mode}-Accuracy with Entropy Forest:", accuracy_forest_entropy)
    print(f"{mode}-Accuracy with Gini Forest:", accuracy_forest_gini)



def full():
    print("combining the csvs:")
    generate_combined_csv_polars(mode='tile')
    generate_combined_csv_polars(mode='mpl')
    # print("handling the data")
    # aggregate_labels()
    print("creating the tree models")
    tree_and_forest_creation(mode='tile')
    tree_and_forest_creation(mode='mpl')
    print("finished. Good Work!")


def main():
    utils.file_utils.setup_directories()
    read_input = input("select a mode: ")
    match read_input:
        case "full":
            full()
        case "agg":
            aggregate_labels()
        case "polars":
            print("polars mode")
            start = time.time()
            generate_combined_csv_polars()
            print("runtime was: " + str(time.time() - start))
        case "d":
            print("Deleting contents of csv_per_core")
            for file in find_file_names(tile_csv_per_core_path, ext="csv"):
                os.remove(file)
            for file in find_file_names(mpl_csv_per_core_path, ext="csv"):
                os.remove(file)
        case "p":
            print("Processing all into one file")
            generate_combined_csv()

        # ab hier noch keine ausgabe für mpl cvs's
        case "compare l":
            print("polars mode")
            start = time.time()
            print(f"Length {len(polars.read_csv(tile_combined_csv))}")
            print("runtime was: " + str(time.time() - start))
            print("pandas mode")
            start = time.time()
            print(f"Length {len(pd.read_csv(tile_combined_csv))}")
            print("runtime was: " + str(time.time() - start))
        case "panda l":
            print(f"Length {len(pd.read_csv(tile_combined_csv))}")
        case "polars l":
            print(f"Length {len(polars.read_csv(tile_combined_csv))}")
        case _:
            print("Not a valid selection! Executing FULL MUHAHAHAHHAHA")
            full()


if __name__ == "__main__":
    main()
