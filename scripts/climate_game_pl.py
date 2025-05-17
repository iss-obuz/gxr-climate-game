# %%
## Import modules
from gxr.envir import EnvirGame
import json
from climate_game.cube import CubeManager
from climate_game.game import Game
import datetime
import pythonnet

pythonnet.load("coreclr")
from enum import Enum, auto  ## noqa
from System import EventHandler  ## noqa
from KiinClient import Guest  ## noqa

# %%
## Define globals
n_players = 3  ## number of players plaing the game - not observersa
nr_rounds = 8  ## Number of rounds
H_Rate_One_Shot = 0.1  ## How much the single shot takes of the resource
file_name = datetime.datetime.now().strftime(
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


# %%
def main() -> None:
    config = None
    with open("SpaceRoom.json", "r") as file:
        config = json.load(file)

    game = Game(
        client=Guest(),
        config_SpaceRoom=config,
        event=EventHandler,
        cube=CubeManager,
        envir_game=EnvirGame,
        n_players=3,
        n_rounds=8,
        nick_to_player_id=NickNameToPlayerNR,
        h_rate=H_Rate_One_Shot,
        wealth_objects=wealth_objects,
    )
    game.set_number_rounds(number_rounds=nr_rounds)
    game.set_sex(dct=sex_users)
    game.connect()
    game.play(file_name=file_name)


# %%
if __name__ in "__main__":
    main()
