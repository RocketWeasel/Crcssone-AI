# Carcassonne

## Game Rules
https://wikicarpedia.com/car/Main_Page or in the Tips.md File for a short overview.

## HowTo's

### Programming
- Should work on every OS and Python version >= 3.10.
- Most of the functions have type annotations. You can turn on the type checker to get hints of what data they expect.
- Evverything you need from the game is handed to the make_step function in the ai/my_ai folder. The classes are for your managing the AI model.

### Logs
There are 3 Types of Logs: 

- Python logs (in the log folder). Here Client server Communication and errors are logged. Those should not be neccessary to debug AI code.
- Game logs (in the gamelog folder). Here Every turn done in a game is logged so it can be used to replay the game and learn offline.
- Game errorlogs (in the log folder). Every turn done until the game crashed. The Errors in the AI functions should not crash the game so either the game was interrupted (ctrl + C ) or some error in the main code occurred, please notify us in case of an error.

### Debugging:
profile_local.py can be used to execute the game single threaded. For visual reference, you can set visualize in the local_game call can be set to True.

Errors in AI code are caught by default and an error message is displayed. For easier debugging you can disable the try catch blocks in the carcassonne.py file(s) there is one for local game and one for the client.

### Local execution
game-local.py executes the game locally on a set number of cores. It can be used to play many games fast to either generate data for the AI to learn or to check if there are some rare errors.(Check for errorlogs afterward)

### Playing over the network
#### Server
For testing, just start lobby-carcassonne.py. To really play over the network, set the server hostname to the PC's name, so it listens to on the right interface.

#### Client Standalone
set the hostname of the server and start client-carcassonne.py. It will join and when the desired number of clients is in a match, try to start. When more clients try to join, it is possible that more players than expected are in a match. Most suited for quick debugging or as a single AI to play against.

#### Client Managed
- Start the lobby.
- Then connect one managed-controller to Set game mode. The controller will also get information about stats during the games.
- Connect managed-clients
- When every client is connected, start the games with the controller

#### Reading & Visualizing Logs
- visualize_logs.py can visualize already played games. This can be used to figure out if reasonable turns were made.
- readlogs.py can be used to read log files and create a summary. You can also use that to get the game state at every point of the played game to assemble them as input data for an AI model. If you use it for debugging set the number of cpus to 1. Debugging with only 1 Thread is much easier.
- When using readlogs.py, to read many games, check if replay and test_simulation are disabled. Those are slow tests to check for game integrity.

#### Playing against the AI
The game is mostly designed to be Played by AI so keep that in mind in terms of usability. You are welcome to improve the Human Interface if you like.

- Start a Server
- Start AI clients with client-carcassonne.py and set the number of Players per match higher than the number of clients.
- Start humanPlayer.py select human in the first dropdown menu on the right.
- Select a game that has not started yet from the second dropdown (gameid | Started) e.g. 0|False
- Start the game by pushing the button

- The game proposes Tile Placements. Select one by clicking on the red mark.
- You can then select the orientation in the top-left corner by entering the option number (starting from 0)
- For Meeple Turns you get placements suggested again select one by clicking and choose the meeple Type in the top-left corner. Or pass option 0