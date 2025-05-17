"""This scripts serves for interactive testing of the game."""

# %%
## Import modules
from gxr.envir import EnvirGame
import json
from climate_game.cube import CubeManager
from climate_game.game import Game
from climate_game.event import LiveEventType
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
test_round = 1
test_value = True
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

## Emails to sits (locations around the table.
NickNameToPlayerNR = {  # this number indicates to which position the user has been assigned
    "guestxr.oculusc@gmail.com": 2,  # Gogle C
    "guestxr.oculusd@gmail.com": 5,  # Gogle D
    "guestxroculusa@gmail.com": 1,  # Gogle A
    "guestxrgogleb@gmail.com": 3,  # Gogle B
    "guestxruw@gmail.com": 5,  # participant5   oculus B p2
    "guestxr2@gmail.com": 3,  # participant3   oculus A
    "andrzejn232@gmail.com": 2,  # participant2
    "weronika.m.lewandowska@gmail.com": 4,  # participant4   Weronika oculus private p3 a wyplata na p5
    "manuelzurera@virtualbodyworks.com": 1,
    "bernhard@kiin.tech": 5,
    "elena@kiin.tech": 4,
}

wealth_objects = {
    (0, 2): {"disable": "commons_one_coin"},
    (2, 4): {"enable": "commons_one_coin", "disable": "commons_three_coins"},
    (4, 6): {"enable": "commons_three_coins", "disable": "commons_five_coins"},
    (6, 8): {"enable": "commons_five_coins", "disable": "commons_pile"},
    (8, 10): {"enable": "commons_pile", "disable": "commons_bike"},
    (10, 12): {"enable": "commons_bike", "disable": "commons_scooter"},
    (12, 14): {"enable": "commons_scooter", "disable": "commons_car"},
    (14, 16): {"enable": "commons_car", "disable": "commons_house"},
    (16, 18): {
        "enable": "commons_house",
    },
}

cubes_colors = {
    "#40982f": 0.5,  ## green
    "#af9410": 0.3,  ## orange
    "#af1010": 0,  ## red
}

# %%
## Load config of the Kiin
config = None
with open("SpaceRoom.json", "r") as file:
    config = json.load(file)

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
    nick_to_player_id=NickNameToPlayerNR,
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
game.play_round(file_name=file_name, ri=test_round)

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
