import os

import paths as env

env_paths = [env.TILE_TREE_PATH, env.MPL_TREE_PATH, env.TILE_CSV_PER_CORE_PATH,
             env.MPL_CSV_PER_CORE_PATH, env.CSV_TILE, env.CSV_MPL, env.TILE_FOREST_PATH, env.MPL_FOREST_PATH]


def setup_directories():
    for path in env_paths:
        create_directory_if_not_exists(path)


def create_directory_if_not_exists(directory) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def find_files(path, ext):
    files_in_path = os.listdir(path)
    print(files_in_path)
    if path.endswith("/"):
        path = path[:-1]
    filtered_files = []
    dirs = [path]
    while len(dirs) > 0:
        directory = dirs.pop()
        for filename in files_in_path:
            if os.path.isdir(f"{path}/{filename}"):
                dirs.append(f"{path}/{filename}")
            elif ext is None or filename.endswith("."+ext) or filename.endswith("."+ext+".gz"):
                filtered_files.append(os.path.join(directory, filename))
            else:
                print(filename, os.path.isdir(f"{directory}/{filename}"), os.path.isfile(f"{directory}/{filename}"))
    return filtered_files


def find_file_names(path, ext) -> list:
    files_in_path = os.listdir(path)
    if path.endswith("/"):
        path = path[:-1]
    file_names = []
    for filename in files_in_path:
        if filename.endswith("." + ext):
            file_names.append(f"{path}/{filename}")
    return file_names


def reset():
    for path in env_paths:
        if os.path.exists(path):
            for filename in os.listdir(path):
                os.remove(f"{path}/{filename}")
            os.removedirs(path)
    setup_directories()


if __name__ == '__main__':
    print("resetting env path folders")
    reset()
