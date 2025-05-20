# %%
## Import modules
from gxr.envir import EnvirGame
from climate_game.event import LiveEventType
from climate_game.cube import CubeManager
from climate_game.game import Game
from climate_game.config import config, nicks_player_nr, wealth_objects, cubes_colors
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
    "guestxr.oculusc@gmail.com": "man_rich",
    "weronika.m.lewandowska@gmail.com": "woman_rich",
    "guestxr.oculusd@gmail.com": "man",
    "guestxroculusa@gmail.com": "woman_rich",
    "guestxrgogleb@gmail.com": "woman_rich",
}


# %%
def main() -> None:
    game = Game(
        client=Guest(),
        config_SpaceRoom=config,
        event=EventHandler,
        cube=CubeManager,
        live_event=LiveEventType,
        envir_game=EnvirGame,
        n_players=n_players,
        n_rounds=nr_rounds,
        nick_to_player_id=nicks_player_nr,
        h_rate=H_Rate_One_Shot,
        wealth_objects=wealth_objects,
        cubes_color=cubes_colors,
    )
    game.set_number_rounds(number_rounds=nr_rounds)
    game.set_sex(dct=sex_users)
    game.connect()
    game.play(file_name=file_name, interventions_active=False)


# %%
if __name__ in "__main__":
    main()
