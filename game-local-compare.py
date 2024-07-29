#! /bin/python3
import concurrent.futures
import csv
import datetime
import math
import os
import time

import utils.file_utils
from ai.clients_modified import local_game
from ai.my_ai.my_player_modified import MyPlayerModified
from ai.my_ai.my_player_decisiontree import MyPlayerDecisionTree
from ai.my_ai.my_player_forest import MyPlayerRandomForest
from ai.random_player import RandomPlayer

#test change for commit and push

NO_GAMES = 10
DEBUG = True
AIS = [MyPlayerDecisionTree, RandomPlayer]
PLAYER_PER_MATCH = len(AIS)


def main():
    cpus = os.cpu_count()
    utils.file_utils.setup_directories()
    if cpus is None:
        cpus = 1
    if cpus > 2:  # Don't use Hyperthreading
        cpus = cpus // 2
    games_per_process = math.ceil(NO_GAMES / cpus)
    averages = True
    if DEBUG:
        print(local_game(no_matches=1, average=averages, ais=AIS, debug=DEBUG))
        return

    # run_game(cpus, games_per_process, averages=averages,
    #          ai_str=["Previous AI", "Random", "Random", "Random", "Random"],
    #          ais=[MyPlayer, RandomPlayer, RandomPlayer, RandomPlayer, RandomPlayer])

    run_game(cpus, games_per_process, averages=averages, ais=AIS)

    # run_game(cpus, games_per_process, averages=averages,
    #          ai_str=["Modified AI", "Random", "Random", "Random", "Random"],
    #          ais=[MyPlayerModified, MyPlayerModified, MyPlayerModified, MyPlayerModified, MyPlayerModified])


def run_game(cpus: int, games_per_process: int,  averages=True, ais=None):
    print(f"Testing the ai, with {games_per_process} games_per_process on {cpus} cpus")
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpus) as executor:
        # noinspection PyTypeChecker
        futures = [
            executor.submit(local_game, no_matches=games_per_process, core_number=i,
                            visualize=False, average=averages, ais=ais, debug=False)
            for i in range(cpus)]

    if averages:
        average_result = get_average_from_futures(futures)
        print(average_result)

    end = time.time()
    print("runtime was: " + str(end - start))


def get_average_from_futures(futures) -> list[float]:
    cpus = os.cpu_count() // 2
    sum_list = [0 for _ in range(PLAYER_PER_MATCH)]

    for future in concurrent.futures.as_completed(futures):
        sum_list = [future.result()[i] + sum_list[i] for i in range(PLAYER_PER_MATCH)]

    return [round(sum_list[i] / cpus, 2) for i in range(PLAYER_PER_MATCH)]


"""
 Function that stores the average points of the modified AI into a csv,
 in order to easily compare the performance, after having changes done to the algorithm.
"""


def store_ai_data_in_file(results):
    if not os.path.exists('AI-Data.csv'):
        create_and_initialize_or_reset_csv()
    date_time = datetime.datetime.now()
    dataline = [str(results[0])+':', str(NO_GAMES)+':', str(date_time.strftime("%d.%m.%Y"))+':', str(date_time.strftime("%H.%M.%S"))+':']
    with open('AI-Data.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(dataline)


"""
Use This function to reset the CSV 'AI-Data' or just delete the file
"""


def create_and_initialize_or_reset_csv():
    with open('AI-Data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Score: #ofGames: Date: Time:'])


if __name__ == '__main__':
    main()
