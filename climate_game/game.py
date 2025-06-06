import time
import numpy as np
import datetime
from climate_game import DATA
import json


class Game:
    """Class that manages the whole game."""

    def __init__(
        self,
        client,
        config_SpaceRoom: dict,
        event,
        cube,
        envir_game,
        live_event,
        n_players: int,
        n_rounds: int,
        nick_to_player_id: dict,
        wealth_objects: dict,
        cubes_color: dict,
        h_rate: float = 0.1,
        n_observers: int = 0,
        tree: float = 0.5,
        world: float = 0.5,
        fog: float = 0.3,
    ):
        """Initilizes the game.

        Parameters
        ----------
        client : Guest
            the instance of Kiin client.
        config_SpaceRoom : dict
            the configuration of the experience. It should be a dict looking like the following.
            {
                "appId": "40a25e24-4d21-4269-bd18-ad58062199a6",
                "voiceAppId": "5c4f5759-7d52-4be8-b507-987ce5dd77f3",
                "region": "EU",
                "theRoomName": "guestxr_spaceroom"
            }
        event : EventHandler
            some class of Kiin
        live_event : climate_game.event.LiveEventType
            some class of Kiin
        cube : climate_game.CubeManager
            a class to manage cubes in the game
        envir_game : gxr.envir.EnvirGame
            a class to manage the environment
        n_players : int
            the number of players in the game
        n_rounds : int
            the number of rounds in the game
        nick_to_player_id : dict
            a dictionary with emails as keys and positions of the player as values. It should look like the following.
            {
                "guestxr.oculusc@gmail.com" : 2
            }
        wealth_objects : list, optional
            a dict with ranges of each object activation as keys. Values are dicts that say which object should be displayed or not with a given range. It should look like the following.
            {
                (2,4) : {"enable" : "commons_one_coin", "disable" : "commons_three_coins"}
            }
        h_rate : float, optional
            a float defining how much should one shot take from the resource. It is divided by the number of players, by default .1
        n_observers : int, optional
            the number of additional non-playing characters, by default 0
        tree : float, optional
            the EnviCondtion's value below which the tree should turn red.
        world : float, optional
            the EnviCondtion's value below which the outside world should turn red.
        fog : float, optional
            the EnviCondtion's value below which the red fog should be activated.
        cubes_color : dict
            the dictionary where keys are values of the EnviCondition above which the color of the cubes should change. The keys are hex colors. For example.
            {
                "#40982f" : .5
            }
        """
        self.client = client
        self.config_SpaceRoom = config_SpaceRoom
        time.sleep(2)
        print("adding event handler")
        self.client.liveEventCallback = event(self.handler)
        self.LiveEventType = live_event
        self.UserIdToPlayerIndex = {}
        self.cube_manager = cube(self.client)
        self.isSyncPhase = True
        self.playersInSync = set()
        self.resourceSize = self.cube_manager.size**3
        self.gameStarted = False
        self.connectedusers = {}  # to synchronize the starting moment
        self.NickNameToPlayerIndex = {}
        self.PlayerIndexToPlayerNr = {}
        self.n_players = n_players
        self.n_observers = n_observers
        # Initialize a game object from config dictionary
        self.game = envir_game.from_config(
            n_agents=n_players, K=self.resourceSize, no_behavior=True, noise=0
        )  # T=5 # T regeneracja od 5 do 95% stan srodowiska. T najlepiej nie ruszac
        self.T = 30  # duration of one round
        self.NR = n_rounds  # number of rounds
        self.i = 0  # number of steps so far in one round
        self.H = np.zeros(self.game.n_agents)
        # self.RLb = np.loadtxt("RL_bias.txt", delimiter=" ") # RL learned bias compensation
        self.backFromHell = False
        self.playersWealthDistribution = [
            0
        ] * self.game.n_agents  # poziomy bogactwa graczy
        self.sex_users = {}
        self._wealth_dct = {}
        self._eqaul_wealth = True
        self.NickNameToPlayerNR = nick_to_player_id
        self.H_Rate_One_Shot = h_rate / n_players
        self.wealth_objects = wealth_objects
        self._wealth_objects_lst = [
            item["enable"] for item in self.wealth_objects.values() if "enable" in item
        ]
        self.EnviCondition, self.EnviCondition_start = 1, 1
        self.intervention = ""
        self.tree = tree
        self.world = world
        self.fog = fog
        self.cubes_color = cubes_color
        self._user_niks = []

    def set_equal_wealth(self, value: bool):
        """Sets the value of self._equal_wealth

        Parameters:
        -----------
        value : bool
            a value which should be set to self._equal_wealth
        """
        self._eqaul_wealth = value

    def _compute_equality(self):
        """Computes equality in wealth. And set self._equality_wealth to either True or False."""
        min_wealth = abs(min(self._wealth_dct.values()))
        max_wealth = abs(max(self._wealth_dct.values()))

        if max_wealth - min_wealth < 4:
            self.set_equal_wealth(True)
        else:
            self.set_equal_wealth(False)

    def _set_avatars(self) -> None:
        """Sets the sex of avatars.

        Parameters
        ----------
        dct : dict, optional
            a dictionary that maps the emails to desired avatar's sex, by default sex_users
        """
        look_up = {
            "man": "47f0f240-5e4a-4ad8-90b5-4a49563a08fc",
            "male": "47f0f240-5e4a-4ad8-90b5-4a49563a08fc",
            "m": "47f0f240-5e4a-4ad8-90b5-4a49563a08fc",
            "man_rich": "b6b2c370-e228-40ef-b7e8-f5f331d77275",
            "man_poor": "82c95958-3b63-4eea-9ef8-814000fb80b6",
            "woman": "0f9d8310-48a1-4043-82f0-de73363ee0f3",
            "female": "0f9d8310-48a1-4043-82f0-de73363ee0f3",
            "f": "0f9d8310-48a1-4043-82f0-de73363ee0f3",
            "woman_rich": "df3acd8e-7c3a-4461-82ec-ed15ae3f1a88",
            "woman_poor": "beff84fc-983d-4fa0-baf4-b0f22da3706c",
        }
        dct = {key: look_up[value] for key, value in self.sex_users.items()}
        for player in self.client.GetPlayersList():
            if player.NickName != "The_Guest":
                self.client.SetNewAvatar(player.UserId, dct[player.NickName])
                print(
                    f"Change {player.NickName} avatar to {self.sex_users[player.NickName]}"
                )

    def set_number_rounds(self, number_rounds: int = 8) -> None:
        """Sets the number of rounds in the game.

        Parameters
        ----------
        number_rounds : int, optional
            The number of rounds in the game.
        """
        self.NR = number_rounds
        print(f"The number of rounds is {self.NR}")

    def set_sex(self, dct: dict) -> None:
        """Sets the dictionary with avatars sex.

        Parameters
        ----------
        dct : dict, optional
            _description_, by default sex_users
        """
        self.sex_users = dct

    def get_index_from_cube_id(self, cube_id):
        x = int(cube_id[len(cube_id) - 3]) - 1
        y = int(cube_id[len(cube_id) - 2]) - 1
        z = int(cube_id[len(cube_id) - 1]) - 1
        return x, y, z

    def createLookupDictionary(self):
        user_ids_for_expected_players = []
        for player in self.client.GetPlayersList():
            if player.NickName in self.NickNameToPlayerNR.keys():
                user_ids_for_expected_players.append(player.UserId)  # player_id
            if (
                player.NickName != "The_Guest"
                and player.NickName in self.NickNameToPlayerNR.keys()
            ):
                self._user_niks.append(player.NickName)
        self.UserIdToPlayerIndex = {
            user_id: index
            for index, user_id in enumerate(user_ids_for_expected_players)
        }
        self.NickNameToPlayerIndex = {
            user_nik: index for index, user_nik in enumerate(self._user_niks)
        }
        self.PlayerIndexToPlayerNr = {
            index: self.NickNameToPlayerNR[user_nik]
            for index, user_nik in enumerate(self._user_niks)
        }

    def lookup_place_nick(self, place: str) -> str:
        """Returns the nickname of the player sitting in a given place.

        Parameters
        ----------
        place : str
            the place where the player is sitting.
        Returns
        -------
        str
            the nickname of the player.
        """
        look_up = {
            value: key
            for key, value in self.NickNameToPlayerNR.items()
            if key in self._user_niks
        }
        return look_up[place]

    def NickNamefromPlayerId(self, PlayerID):
        playerlist = self.client.GetPlayersList()
        nickname = None
        for player in playerlist:
            if player.UserId in PlayerID:
                nickname = player.NickName
                break
        return nickname

    def print_player_list(self):
        for player in self.client.GetPlayersList():
            print(f"nik: {player.NickName} id: {player.UserId}")

    def player_id_from_nick_name(self, nickname):
        player_id = None
        for player in self.client.GetPlayersList():
            if nickname in player.NickName:
                player_id = player.UserId
        return player_id

    def prepare_wealth(self):
        # Coins 1, 3, 5, stack on place 1, rest on 2,3,4,5
        for i in range(1, 6):
            for obj_i, wealth_object in enumerate(self._wealth_objects_lst):
                self.client.PushCommand(
                    "spawn_object",
                    # spawn_object commons_scooter participant3_commons_scooter resource_participant3_object1
                    f"{wealth_object} participant{i}_{wealth_object} resource_participant{i}_object{1 if obj_i < 4 else obj_i - 2}",
                )
            for wealth_object in self._wealth_objects_lst:
                self.client.PushCommand(
                    "disable_object", f"participant{i}_{wealth_object}"
                )

    def update_wealth(self, player_i: int, player_n: int):
        """Updates the wealth of a player.

        Parameters
        ----------
        player_i : int
            player index

        player_n : int
            player number
        """
        pUr = self.game.U[player_i]  # player Utility
        for key, value in self.wealth_objects.items():
            if pUr > key[0] and pUr <= key[1]:
                for k, v in value.items():
                    self.client.PushCommand(f"{k}_object", f"participant{player_n}_{v}")

    def handler(self, source, args):
        # to synchronize the starting moment
        if args.data["type"] == 7:
            xx_x = args.data["extraData"]["userId"]
            print(f"custom event received, userId: {xx_x}")
            playerId = args.data["extraData"]["userId"].strip()

            if playerId in self.NickNameToPlayerNR.keys():
                self.connectedusers[playerId] = datetime.datetime.now()
            else:
                print(
                    f"playerid:{playerId} nicktoPlayerNR:{self.NickNameToPlayerNR.keys()}"
                )

        if (
            args.data["type"] == self.LiveEventType.ButtonPress.value
            and self.isSyncPhase
        ):
            self.playersInSync.add(
                self.NickNameToPlayerNR[args.data["source_client_id"]]
            )
            print(self.NickNameToPlayerNR[args.data["source_client_id"]])
            print(f"playersInSync set: {self.playersInSync}")
            if len(self.playersInSync) >= self.game.n_agents:
                self.isSyncPhase = False

        elif (
            args.data["type"] == self.LiveEventType.ButtonPress.value
            and self.gameStarted
        ):
            cube_id = args.data["extraData"]["pressable_object"]
            player_i = self.NickNameToPlayerIndex[args.data["source_client_id"]]

            # value added here and sleep in the game loop determine harvesting rate
            self.H[player_i] += self.H_Rate_One_Shot

            # scaling down the cube after each shot
            if cube_id in self.cube_manager.cubeScale:
                self.cube_manager.cubeScale[cube_id] *= 0.9
            else:
                self.cube_manager.cubeScale[cube_id] = (
                    0.09  # instead of 0.1 there is 0.09 to distinguish such just shot from just reborn
                )
            scl = self.cube_manager.cubeScale[cube_id]
            self.client.PushCommand(
                "set_object_scale", f"{cube_id} {scl},{scl},{scl} 0.2"
            )

            # cube hit signal
            self.client.SendGenericCommand(
                "play_audio_clip", "friend_request.ogg source 0.1 0.0 false"
            )

    def connect(self):
        """Connect to the Kiin environment, set everything up and let the players in."""
        ## Send config to Kiin
        self.client.StartClient(self.config_SpaceRoom["appId"], "1_2.40")
        time.sleep(5)
        self.client.JoinRoom(self.config_SpaceRoom["theRoomName"], 5)

        print(
            f"waiting for {self.game.n_agents} players to join {self.config_SpaceRoom['theRoomName']}"
        )
        # make this + 1 +2 if you want an obverver or +3 for 2 observers etc
        while (
            self.client.GetPlayersList().Count
            < self.game.n_agents + 1 + self.n_observers
        ):  # +1 because GuestXR is counted (although it is a meta pleyer)
            self.client.PushCommand(
                "fade_out",
                f"0.3 'Please wait.\
                                    \nThe game is about to start.\
                                    \nWaiting for {self.game.n_agents - self.client.GetPlayersList().Count + 1} player(s) to join.'",
            )
            print(".", end="", flush=True)
            time.sleep(2)

        print(
            f"Users connected (including GuestXR): {self.client.GetPlayersList().Count}"
        )
        self.print_player_list()
        time.sleep(5)

        # synchronization of the start time from Bernhard
        self.customEventTime = datetime.datetime.now
        while len(self.connectedusers) < self.game.n_agents:
            time.sleep(2)
            self.client.PushCommand("send_event", "connected")
            print(
                f"synchronizet users n: {len(self.connectedusers)} are: {self.connectedusers}"
            )

        ## Prepare wealth -- display and disappear it quickly.
        self.prepare_wealth()

        ## Prepare fog.
        self.client.PushCommand(
            "spawn_object", "commons_fog ParticleSystem commons_fog_anchor"
        )
        time.sleep(1)
        self.client.PushCommand("disable_object", "ParticleSystem")

        ## Set the global message.
        self.client.PushCommand("show_text", 'global_message "Cześć!" 1.0')

        ## Set the sex of avatars.
        self._set_avatars()

        ## Wait till all the changes happen.
        time.sleep(2)

        ## Show the room to players.
        self.client.PushCommand("fade_in", "1.0")
        # All players are in the room, but they cannot play yet. Their lasers are inactive.

        ## Disable the lasers.
        self.client.PushCommand(
            "set_laser_pointer_active", "false"
        )  # SendGenericCommand
        time.sleep(1)

        ## Spawn the cubes.
        self.cube_manager.spawn_all_objects()
        time.sleep(1)

        ## Create the look-up dictionary.
        self.createLookupDictionary()

        ## Print information about players that joined.
        print(f"{self.client.GetPlayersList().Count} players joined.")
        print(self.UserIdToPlayerIndex)
        print(self.NickNameToPlayerIndex)
        print(self.PlayerIndexToPlayerNr)
        self.print_player_list()

        ## Playe birds sound in a loop.
        self.client.PushCommand(
            "play_audio_clip", "birds.ogg ambientNoise 0.2 1.0 true"
        )

    def instructions(self):
        """Play the initial instructions."""
        ## Change the string on the players display.
        for i in range(1, 6):
            self.client.PushCommand(
                "show_text",
                f'participant{i}_score_text "Proszę skup się teraz na instrukcji" 1.0',
            )

        ## Instruction 1
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_01")
        print("Take 01 ......")
        ## Wait for the clip to end
        time.sleep(52.062041666666666)

        ## Instruciton 2
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_02")
        print("Take 02 ......")
        ## Wait for the clip to end
        time.sleep(60.9959375)
        ## Activate the laser.
        self.client.PushCommand("set_laser_pointer_active", "true")
        time.sleep(2)

        ## Instruction 3 -- Synchronization
        waitTimeN = 0
        ## Waiting till everyone uses their lasers.
        while self.isSyncPhase:
            time.sleep(0.1)
            waitTimeN += 1
            if waitTimeN % 100 == 0:
                self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_03")
                print("Take 03 ......")
                ## Wait for the clip to end
                time.sleep(13.5575625)

        ## Make the cobes green
        self.cube_manager.set_color_all_objects("#40982f")
        ## Deactivate the laser
        self.client.PushCommand("set_laser_pointer_active", "false")
        time.sleep(2)
        print("Synchronization completed.\n Lasers inactive.")

        ## Instruction 4
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_04")
        print("Take 04 ......")
        ## Wait for the clip to end
        time.sleep(4.5191875)

        ## Instruction 5
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_05")
        print("Take 05 ......")
        ## Wait for the clip to end
        time.sleep(138.266125)

        ## Instruciton 6
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_06")
        print("Take 06 ......")
        ## Wait for the clip to end
        time.sleep(17.893895833333332)

        ## Instruction 7
        self.client.PushCommand(
            "play_take", "ClimateChange_Instruct_pl_07"
        )  # zawiera ping
        print("Take 07 ......")
        ## Wait for the clip to end
        time.sleep(22.360833333333332)

        # Disable Instructor.
        self.client.PushCommand("disable_object", "instructor")

    def no_instructions(self):
        """Play the initial instructions."""
        ## Change the string on the players display.
        for i in range(1, 6):
            self.client.PushCommand(
                "show_text",
                f'participant{i}_score_text "Proszę skup się teraz na instrukcji" 1.0',
            )

        ## Instruction 1
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_noinv_01")
        print("Take 01 ......")
        ## Wait for the clip to end
        time.sleep(56)

        ## Instruciton 2
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_noinv_02")
        print("Take 02 ......")
        ## Wait for the clip to end
        time.sleep(44)
        ## Activate the laser.
        self.client.PushCommand("set_laser_pointer_active", "true")
        time.sleep(2)

        ## Instruction 3 -- Synchronization
        waitTimeN = 0
        ## Waiting till everyone uses their lasers.
        while self.isSyncPhase:
            time.sleep(0.1)
            waitTimeN += 1
            if waitTimeN % 100 == 0:
                self.client.PushCommand(
                    "play_take", "ClimateChange_Instruct_pl_noinv_03"
                )
                print("Take 03 ......")
                ## Wait for the clip to end
                time.sleep(16)

        ## Make the cobes green
        self.cube_manager.set_color_all_objects("#40982f")
        ## Deactivate the laser
        self.client.PushCommand("set_laser_pointer_active", "false")
        time.sleep(2)
        print("Synchronization completed.\n Lasers inactive.")

        ## Instruction 4
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_noinv_04")
        print("Take 04 ......")
        ## Wait for the clip to end
        time.sleep(4)

        ## Instruction 5
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_noinv_05")
        print("Take 05 ......")
        ## Wait for the clip to end
        time.sleep(115)

        ## Instruciton 6
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_noinv_06")
        print("Take 06 ......")
        ## Wait for the clip to end
        time.sleep(3)

        ## Instruction 7
        self.client.PushCommand(
            "play_take", "ClimateChange_Instruct_pl_noinv_07"
        )  # zawiera ping
        print("Take 07 ......")
        ## Wait for the clip to end
        time.sleep(22)

        # Disable Instructor.
        self.client.PushCommand("disable_object", "instructor")

    def play_round(self, file_name: str, ri: int):
        """Play a single round of the game.

        Parameters
        ----------
        file_name : int
            the name of the file to which the results will be saved.
        ri : _type_
            the number of the round.
        """
        with open(DATA / f"{file_name}_round_{ri}.jsonl", "w") as file:
            while self.i < self.T:  # Duration of a game round: 30s
                self.H = np.zeros(self.game.n_agents)
                time.sleep(
                    1.0
                )  # every 1s the state of the game and the environment is updated
                # attention! it affects the duration of the round

                print(self.H)
                self.game.H = self.H
                self.game.dynamics.run(
                    1 / (self.T * self.NR)
                )  # 1/self.T is an entire epoch in one round,
                # because the “run” for 1 is an entire epoch, i.e., a full restoration of the environment
                self.i = self.i + 1
                self.cube_manager.scale_all_objects()  # to reverse the scaling effect when the cursor goes off the object

                envE = max(0, self.game.model.E / self.game.n_agents)
                envK = self.game.model.envir.K / self.game.n_agents
                self.cube_manager.sync_with_Et(envE, envK)

                print(
                    f"Et:EK:rQ:aQ:Et/EK: {envE} : {envK} : {len(self.cube_manager.removed_cubes)} : {len(self.cube_manager.avaliable_cubes)} : {envE / envK}"
                )

                for p_i in range(self.game.n_agents):
                    player_n = self.PlayerIndexToPlayerNr[p_i]
                    score_str = f'participant{player_n}_score_text "Posiadane zasoby: {round(self.game.U[p_i], 2)}" 1'
                    self.client.SendGenericCommand("show_text", score_str)
                    self.update_wealth(p_i, player_n)
                    self._wealth_dct[player_n] = round(self.game.U[p_i], 2)

                tmp = {
                    "Et": envE,
                    "EK": envK,
                    "rQ": len(self.cube_manager.removed_cubes),
                    "aQ": len(self.cube_manager.avaliable_cubes),
                    "Enviornment Condition": envE / envK,
                    **{
                        self.lookup_place_nick(key): value
                        for key, value in self._wealth_dct.items()
                    },
                }
                file.write(json.dumps(tmp) + "\n")

    def interventions(self, ri: int):
        """Selects the intervention to be played.

        Parameters
        ----------
        ri : int
            the number of the round
        """
        self.intervnetion = ""
        if ri == 0:
            if self.EnviCondition > 0.5:
                self.intervention = "Audio_7_TPP_pl"

            else:
                self.intervention = "Audio_7_TPN_pl"

        elif ri == 1:
            if self.EnviCondition > 0.5:
                self.intervention = "Audio_6_TPP_pl"

            else:
                self.intervention = "Audio_6_TPN_pl"

        elif ri == 2:
            if self.EnviCondition > 0.5:
                self.intervention = "Audio_6_TPP_pl"

            elif self.EnviCondition < 0.3:
                self.intervention = "Audio_6_TPN_pl"

        elif ri == 3:
            if self._eqaul_wealth:
                self.intervention = "Audio_12_SP_pl"
            else:
                self.intervention = "Audio_12_SN_pl"
        elif ri == 4:
            if (
                self.EnviCondition - self.EnviCondition_start > 0.2
                and self.EnviCondition > 0.3
            ):
                self.intervention = "Audio_1_EP_pl"
            elif self.EnviCondition_start - self.EnviCondition > 0.2:
                self.intervention = "Audio_1_EN_pl"
            else:
                self.intervention = ""
        elif ri == 5:
            if self.EnviCondition > 0.4:
                self.intervention = "Audio_3_EP_pl"
            else:
                self.intervention = "Audio_3_EN_pl"

        elif ri == 6:
            if self._eqaul_wealth:
                self.intervention = "Audio_9_SP_pl"
            else:
                self.intervention = "Audio_9_SN_pl"
        else:
            self.intervention = ""

    def play_intervention(self):
        """Plays the intervention audio and prints its name to the screen."""
        if self.intervention:
            print(f"play_audio clip:: {self.intervention}.opus")
            self.client.PushCommand(
                "play_audio_clip",
                f"{self.intervention}.opus ambientNoise 1.0 1.0 false",
            )
        else:
            print("No intervention")

    def set_tree(self, value: float = 0.5):
        """Set the value of self.tree.

        Parameters
        ----------
        value : float, optional
            the EvniCondition value below which tree turns red, by default .5
        """
        self.tree = value

    def change_tree(self):
        """Changes the color of the tree."""
        if self.EnviCondition < self.tree:
            self.client.PushCommand("set_object_color", "---tree-- #FF0011 2.0")
        else:
            self.client.PushCommand("set_object_color", "---tree-- #FFFFFF 2.0")

    def set_world(self, value: float = 0.5):
        """Set the value of self.world.

        Parameters
        ----------
        value : float, optional
            the EvniCondition value below which the outside world turns red, by default .5
        """
        self.world = value

    def change_world(self):
        """Changes the color of the outside world."""
        if self.EnviCondition < self.world:
            self.client.PushCommand("fade_skybox_tint", "#FF0011 5")
        else:
            self.client.PushCommand("fade_skybox_tint", "#FFFFFF 5")
            self.client.PushCommand(
                "play_audio_clip", "birds.ogg ambientNoise 0.2 1.0 true"
            )

    def set_fog(self, value: float = 0.3):
        """Set the value of self.fog.

        Parameters
        ----------
        value : float, optional
            the EvniCondition value below which the red fog is activate, by default .3
        """
        self.fog = value

    def activate_fog(self):
        """Activates the red fog."""
        if self.EnviCondition <= self.fog:
            self.backFromHell = True
            self.client.PushCommand("enable_object", "ParticleSystem")
            self.client.PushCommand("fade_fog_color", "red 0.5")
            self.client.PushCommand("fade_fog_intensity", "0.5 0.5")
            self.client.PushCommand(
                "play_audio_clip",
                "Sound_5_Industrial.opus ambientNoise 0.2 1.0 true",
            )
        elif self.backFromHell:
            self.backFromHell = False
            self.client.PushCommand("disable_object", "ParticleSystem")

    def color_cubes(self):
        """Colors the cubes depending on the environment state."""
        for key, value in self.cubes_color.items():
            if value < self.EnviCondition:
                color = key
        self.cube_manager.set_color_all_objects(color)

    def play(self, file_name: str, interventions_active: bool = True):
        """Play the whole game.

        Parameters
        ----------
        file_name : str
            the name of the file to which the results will be stored.
        """
        ## Play Instructions
        if interventions_active:
            self.instructions()
        else:
            self.no_instructions()

        ## Disable Audio
        for userID in self.UserIdToPlayerIndex.keys():
            self.client.PushCommand("set_character_audio_volume", f"{userID} 0.0 0.5")

        ## Wait for the change to have the effect
        time.sleep(1)

        ## Activate the lasers
        self.client.PushCommand("set_laser_pointer_active", "true")
        print("laser active")
        ## Wait for the change to have the effect
        time.sleep(1)
        ## Show the first round message
        self.client.PushCommand("show_text", 'global_message "Runda 1" 1.0')
        ## Wait for the change to have the effect
        time.sleep(1)
        ## Start the game
        self.gameStarted = True

        for ri in range(self.NR):
            self.client.PushCommand("fade_in", "1.0")
            if ri != 0:
                self.client.PushCommand(
                    "show_text", f'global_message "Runda {ri + 1}" 1.0'
                )

            ## Play a round of the game
            self.play_round(file_name=file_name, ri=ri)

            ## What happens in the pause
            self.i = 0  # round time reset
            ## Disable the lasers.
            self.client.PushCommand("set_laser_pointer_active", "false")
            print("laser inactive")
            ## Play the sound of the end of the round
            self.client.SendGenericCommand(
                "play_audio_clip", "signal.opus source 0.5 0.0 false"
            )
            ## Change the global message
            self.client.PushCommand("show_text", 'global_message "Przerwa" 1.0')

            ## Change the color of cubes to gray.
            self.cube_manager.set_color_all_objects("#777777")
            ## Wait for the changes to take effect.
            time.sleep(2)

            ## Compute the state of the Environment
            envE = max(0, self.game.model.E / self.game.n_agents)
            envK = self.game.model.envir.K / self.game.n_agents
            self.EnviCondition = envE / envK
            print(f"EnviCondition: {self.EnviCondition}")

            ## Compute the wealth equality
            self._compute_equality()

            ## Select the intervention
            if interventions_active:
                self.interventions(ri=ri)

            ## Play the intervention
            self.play_intervention()

            ## Wait till intervention to end.
            time.sleep(9)

            if interventions_active:
                ## Change the color of the tree
                self.change_tree()

                ## Change the color of the outside world
                self.change_world()

                ## Activate the red fog
                self.activate_fog()

            ## Wait for changes to take effect
            time.sleep(3)

            ## Change the color of the cubes.
            self.color_cubes()

            ## Wait for the changes ot take the effect
            time.sleep(2)

            ## Play sound of the end of the round
            self.client.SendGenericCommand(
                "play_audio_clip", "signal.opus source 0.5 0.0 false"
            )
            if (ri + 1) == self.NR:
                self.client.PushCommand("set_laser_pointer_active", "false")
                ## Change the color of cubes to gray.
                self.cube_manager.set_color_all_objects("#777777")
                time.sleep(2)
                break
            ## Activate the lasers
            self.client.PushCommand("set_laser_pointer_active", "true")
            print("laser active")
            ## Wait for the changes to take the effect
            time.sleep(1)
            self.EnviCondition_start = self.EnviCondition

        # koniec gry #############################################################

        ## Display the Instructor
        self.client.PushCommand("enable_object", "instructor")

        ## Instruction 8
        self.client.PushCommand(
            "play_take", "ClimateChange_Instruct_pl_08"
        )  # waiting for the end of the clip
        print("Take 08 ......")
        time.sleep(16.404916666666665)
