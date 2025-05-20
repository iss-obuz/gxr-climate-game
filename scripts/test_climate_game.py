"""This scripts serves for interactive testing of the game."""

# %%
## Import modules
from gxr.envir import EnvirGame
from climate_game.cube import CubeManager
from climate_game.game import Game
from climate_game.event import LiveEventType
from climate_game.config import config, nicks_player_nr, wealth_objects, cubes_colors
import datetime
import pythonnet
import time

pythonnet.load("coreclr")
from enum import Enum, auto  ## noqa
from System import EventHandler  ## noqa
from KiinClient import Guest  ## noqa

# %%
## Define globals
n_players = 3  ## number of players plaing the game - not observersa
nr_rounds = 8  ## Number of rounds
test_round = 1  ## Starst from 0
test_value = True  ## Hardwire the equal_wealth
H_Rate_One_Shot = 0.1  ## How much the single shot takes of the resource
file_name = "test_" + datetime.datetime.now().strftime(
    "%Y_%m_%d_%H_%M"
)  ## Name of the file to write out.

## Sex of the users
sex_users = {
    "guestxr.oculusc@gmail.com": "woman",
    "weronika.m.lewandowska@gmail.com": "woman_rich",
    "guestxr.oculusd@gmail.com": "man",
    "guestxroculusa@gmail.com": "woman_rich",
    "guestxrgogleb@gmail.com": "woman_rich",
}

# %%
## Set up the game
game = Game(
    client=Guest(),
    config_SpaceRoom=config,
    event=EventHandler,
    cube=CubeManager,
    envir_game=EnvirGame,
    live_event=LiveEventType,
    n_players=3,
    n_rounds=8,
    nick_to_player_id=nicks_player_nr,
    h_rate=H_Rate_One_Shot,
    wealth_objects=wealth_objects,
    cubes_color=cubes_colors,
)
game.set_number_rounds(number_rounds=nr_rounds)
game.set_sex(dct=sex_users)

# %%
## Connect to the game
game.connect()

# %%
## Play a round
game.clinet.PushCommand("set_laser_pointer_active", "true")
time.sleep(1)
game.client.PushCommand("show_text", f'global_message "Runda{test_round}" 1.0')
game.gameStarted = True

game.play_round(file_name=file_name, ri=test_round)
game.i = 0
game.gameStarted = False
# %%
## Change the value for testing purposes.
game.set_eqaul_wealth(value=test_value)
game.interventions(ri=test_round)

# %%
## Play the intervention
game.play_intervention()
time.sleep(9)

# %%
## Set the color of the tree
game.set_tree()
game.change_tree()

# %%
## Set the color of the world
game.set_world()
game.change_tree()

# %%
## Activate the fog
game.set_fog()
game.activate_fog()

# %%
## Color the cubes
game.color_cubes()
