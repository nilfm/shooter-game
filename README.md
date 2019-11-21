# shooter-game

### Requirements and installation

This game requires Python 3.6 or newer.

You will also need Pygame. If you don't have it installed, you can execute:

`pip3 install -r requirements.txt`

To launch the game, execute:

`python3 player_vs_ai.py`

To watch a game between two AIs, execute:

`python3 ai_vs_ai.py`


### How to play

If you chose the "Player vs AI" mode, the controls are very simple:

* WASD to move up, left, down and right.
* Hold space bar to close the aim, and release to shoot.

Observations:

* There is a short cooldown between shots.
* When you shoot, the bullet can go in any direction that is inside the aim range, which is delimited by the two lines on your character. The probability distribution is triangular, with the center being the most likely.
* If you close the aim for too long, you will lose the shot and will have to wait for the cooldown period to shoot again.

### To do

[ ] Clean up repeated code

[ ] I would like to offer a good API to program your own AI with and try it vs other players. Possibly with a ranking system, etc.  
