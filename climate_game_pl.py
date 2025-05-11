# %%
## Import modules
import numpy as np
from gxr.envir import EnvirGame
import json
from pathlib import Path
import os

import datetime

import random
from collections import deque

import pythonnet
pythonnet.load("coreclr")
from enum import Enum, auto

import time
#import clr, System
from System import EventHandler

from KiinClient import Guest #, AnimationMode

# %%
## Define globals
ROOT = Path(__file__).absolute().parent
DATA = ROOT / "data"
if not os.path.exists(DATA):
    os.makedirs(DATA)
n_obververs = 0 # number of additional non playing observers
n_players = 3 # number of players plaing the game - not observers
H_Rate_One_Shot = 0.1 / n_players # 0.2
file_name =  datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")

sex_users = {
    
}


###### interwencje GuestXR ######
#################################

intervention_EP = {
    "Audio_3_EP_pl",
    "Audio_4_EP_pl",
    "Audio_1_EP_pl"               
}
intervention_EN = {
    "Audio_1_EN_pl",
    "Audio_3_EN_pl",
    "Audio_4_EN_pl"
}
intervention_TPP = {
    "Audio_6_TPP_pl",
    "Audio_7_TPP_pl"               
}
intervention_TPN = {
    "Audio_6_TPN_pl",
    "Audio_7_TPN_pl"
}
intervention_SN = {
    "Audio_9_SN_pl",
    "Audio_12_SN_pl"
}
intervention_SP = {
    "Audio_9_SP_pl",
    "Audio_12_SP_pl"
}

intervention_set =  intervention_EN | intervention_EP | intervention_TPP | intervention_TPN | intervention_SN | intervention_SP


NickNameToPlayerNR = { # this number indicates to which position the user has been assigned
    "guestxr.oculusc@gmail.com": 2,         # Gogle C
    "guestxr.oculusd@gmail.com": 5,         # Gogle D
    "guestxroculusa@gmail.com": 3,          # Gogle A
    "guestxrgogleb@gmail.com": 4,           # Gogle B 
    "guestxruw@gmail.com": 5,               # participant5   oculus B p2

    "guestxr2@gmail.com": 3,                # participant3   oculus A

    "andrzejn232@gmail.com": 2,             # participant2
    "weronika.m.lewandowska@gmail.com": 4,  # participant4   Weronika oculus private p3 a wyplata na p5

    "manuelzurera@virtualbodyworks.com": 1,
    "bernhard@kiin.tech": 5,
    "elena@kiin.tech": 4
}

wealth_objects= [
    'commons_one_coin',
    'commons_three_coins',
    'commons_five_coins',
    'commons_pile',
    'commons_bike',
    'commons_scooter',
    'commons_car',
    'commons_house'
]

# %%
## Define classes and functions
class LiveEventType(Enum):
    ButtonPress = 0
    VoiceActivity = auto()
    LookAtParticipant = auto()


class CubeManager:
    def __init__(self, client):
        self.client=client
        self.size = 5  # The size of the grid
        self.removed_cubes = deque([])
        self.avaliable_cubes = []
        self.cubeScale = {}
      
    def _get_anchor_name(self, x, y, z):
        return f"commons_resource_anchor{x}{y}{z}"

    def _get_object_name(self, x, y, z):
        return f"commons_resource{x}{y}{z}"
    
    def disable_object(self, x,y,z):
        self.client.PushCommand("disable_object", self._get_object_name(x, y, z))

    def spawn_all_objects(self):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.spawn_object(x, y, z)
             
    def scale_all_objects(self):
        d = self.cubeScale.copy() 
        for k, v in d.items():
            if k not in self.removed_cubes and v < 0.1:
                self.client.PushCommand("set_object_scale", f"{k} {v},{v},{v} 0.1")

    def set_color_all_objects(self, color):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.set_object_color(x, y, z, color, "0.1")
                    
    def spawn_object(self, x, y, z):
        anchor_name = self._get_anchor_name(x, y, z)
        object_name = self._get_object_name(x, y, z)
        self.client.PushCommand("spawn_object", f"commons_resource {object_name} {anchor_name}") 
        self.client.PushCommand("enable_object", object_name) 
        self.client.PushCommand("set_object_color", f"{object_name} #777777 0.0") 
        self.avaliable_cubes.append(object_name)

    def set_object_color(self, x, y, z, color, transition_time=2.0):
        object_name = self._get_object_name(x, y, z)
        self.client.PushCommand("set_object_color", f"{object_name} {color} {transition_time}") 

    def create_wave_pattern(self, color, wave_interval=0.1, transition_time=2.0):
        for i in range(1, self.size * 2):  # Creating a wave that moves through the grid
            for x in range(1, self.size + 1):
                for y in range(1, self.size + 1):
                    for z in range(1, self.size + 1):
                        if x + y + z == i:
                            self.set_object_color(x, y, z, color, transition_time)
            time.sleep(wave_interval)

 
    def random_flash_pattern(self, flash_count=10, transition_time=0.5):
        for _ in range(flash_count):
            x = random.randint(1, self.size)
            y = random.randint(1, self.size)
            z = random.randint(1, self.size)
            # Generates a shade of blue, transitioning to white
            shade = random.randint(0, 255)
            color = f"#{shade:02X}{shade:02X}FF"
            self.set_object_color(x, y, z, color, transition_time)


    def disable_all_objects(self):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.disable_object(x, y, z)
                    
    def sync_with_Et(self, Et, EK):
        d = self.cubeScale.copy() 
        #to remove from smalest to higest
        for k, v in sorted(d.items(), key=lambda x:x[1]):
            if Et < EK - len(self.removed_cubes) and v < 0.1 and k not in self.removed_cubes: #
                self.client.PushCommand("disable_object", k)
                self.removed_cubes.append(k)
                self.avaliable_cubes.remove(k)
            else: 
                # When regenerating the environment, it can also be so that more than one cube is renewed at once
                while Et > EK - len(self.removed_cubes) and len(self.removed_cubes) > 0:
                    q = self.removed_cubes.popleft()
                    self.avaliable_cubes.append(q)
                    scl = 0.1
                    self.cubeScale[q] = scl
                    self.client.PushCommand("enable_object", q)
                    self.client.PushCommand("set_object_scale", f"{q} {scl},{scl},{scl} 0.1")
        # Note that any shot can exhaust more than one cube, so if you run out of hits, then randomly take the missed ones as well
        while Et < EK - len(self.removed_cubes) :
            rand_k = random.choice(self.avaliable_cubes) 
            self.client.PushCommand("disable_object", rand_k)
            self.removed_cubes.append(rand_k)
            self.avaliable_cubes.remove(rand_k)

                    

class Application:
    def __init__(self, config_SpaceRoom):
        self.client = Guest()
        self.config_SpaceRoom = config_SpaceRoom
        time.sleep(2)
        print("adding event handler")
        self.client.liveEventCallback = EventHandler(self.handler)
        self.UserIdToPlayerIndex = {}
        self.cube_manager=CubeManager(self.client)
        self.isSyncPhase = True
        self.playersInSync = set()
        self.resourceSize = self.cube_manager.size**3
        self.gameStarted = False
        self.connectedusers={} # to synchronize the starting moment   
        self.NickNameToPlayerIndex = {}
        self.PlayerIndexToPlayerNr = {}
        # Initialize a game object from config dictionary
        self.game = EnvirGame.from_config(n_agents=n_players, K=self.resourceSize, no_behavior=True, noise=0) #T=5 # T regeneracja od 5 do 95% stan srodowiska. T najlepiej nie ruszac 
        self.T = 30 # duration of one round
        self.NR = 8 # number of rounds
        self.i = 0 # number of steps so far in one round
        self.H = np.zeros(self.game.n_agents)
        # self.RLb = np.loadtxt("RL_bias.txt", delimiter=" ") # RL learned bias compensation
        self.backFromHell = False
        self.playersWealthDistribution = [0]*self.game.n_agents # poziomy bogactwa graczy
 

    def get_index_from_cube_id(self, cube_id):
        x = int(cube_id[len(cube_id)-3])-1
        y = int(cube_id[len(cube_id)-2])-1
        z = int(cube_id[len(cube_id)-1])-1
        return x, y, z

    def createLookupDictionary(self):
        user_ids_for_expected_players=[]
        user_niks=[]
        for player in self.client.GetPlayersList():
            if player.NickName in NickNameToPlayerNR.keys():
                user_ids_for_expected_players.append(player.UserId) # player_id
            if player.NickName!="The_Guest" and player.NickName in NickNameToPlayerNR.keys() : 
                user_niks.append(player.NickName)
        self.UserIdToPlayerIndex = {user_id: index for index, user_id in enumerate(user_ids_for_expected_players)}
        self.NickNameToPlayerIndex = {user_nik: index for index, user_nik in enumerate(user_niks)}
        self.PlayerIndexToPlayerNr = {index: NickNameToPlayerNR[user_nik] for index, user_nik in enumerate(user_niks)}
        
    def NickNamefromPlayerId(self,PlayerID):
        playerlist=self.client.GetPlayersList()
        nickname = None
        for player in playerlist:
            if player.UserId in PlayerID:
                nickname=player.NickName
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
        for i in range(1,6): 
            for obj_i, wealth_object in enumerate(wealth_objects):
                self.client.PushCommand("spawn_object", 
                    # spawn_object commons_scooter participant3_commons_scooter resource_participant3_object1
                    f"{wealth_object} participant{i}_{wealth_object} resource_participant{i}_object{1 if obj_i<4 else obj_i-2}") 
            for wealth_object in wealth_objects:
                self.client.PushCommand("disable_object", f"participant{i}_{wealth_object}") 

    def update_wealth(self, player_i, player_n):
        z = 2.5
        pUr = self.game.U[player_i] # player Utility  
        if pUr <= 5/z:
            self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[0]}") 
            self.playersWealthDistribution[player_i] = 0 # Wealth level 0
        elif pUr>5/z and pUr <=10/z:
            self.client.PushCommand("enable_object", f"participant{player_n}_{wealth_objects[0]}") 
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[1]}") 
            self.playersWealthDistribution[player_i] = 1 # Wealth level 
        elif pUr>10/z and pUr <=15/z:
            self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[0]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[1]}") 
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[2]}")  
            self.playersWealthDistribution[player_i] = 2 # Wealth level 
        elif pUr>15/z and pUr <=20/z:
            self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[1]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[2]}")  
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[3]}") 
            self.playersWealthDistribution[player_i] = 3 # Wealth level 
        elif pUr>20/z and pUr <=25/z:
            self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[2]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[3]}")  
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[4]}") 
            self.playersWealthDistribution[player_i] = 4 # Wealth level 
        elif pUr>25/z and pUr <=30/z:
            #self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[3]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[4]}")  
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[5]}") 
            self.playersWealthDistribution[player_i] = 5 # Wealth level 
        elif pUr>30/z and pUr <=35/z:
            #self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[4]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[5]}")  
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[6]}") 
            self.playersWealthDistribution[player_i] = 6 # Wealth level 
        elif pUr>35/z and pUr <=40/z:
            #self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[5]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[6]}")  
            self.client.PushCommand("disable_object",  f"participant{player_n}_{wealth_objects[7]}") 
            self.playersWealthDistribution[player_i] = 7 # Wealth level 
        elif pUr>40/z:
            #self.client.PushCommand("disable_object", f"participant{player_n}_{wealth_objects[6]}")
            self.client.PushCommand("enable_object",  f"participant{player_n}_{wealth_objects[7]}") 
            self.playersWealthDistribution[player_i] = 8 # Wealth level 
    
    def handler(self, source, args):
        
        # to synchronize the starting moment        
        if args.data["type"] == 7:
            xx_x = args.data["extraData"]["userId"]
            print(f"custom event received, userId: {xx_x}")
            playerId = args.data["extraData"]["userId"].strip()

            if playerId in NickNameToPlayerNR.keys():
                self.connectedusers[playerId]=datetime.datetime.now()
            else:
                print(f"playerid:{playerId} nicktoPlayerNR:{NickNameToPlayerNR.keys()}")

        if args.data["type"] == LiveEventType.ButtonPress.value and self.isSyncPhase:
            self.playersInSync.add(NickNameToPlayerNR[args.data["source_client_id"]])
            print(NickNameToPlayerNR[args.data["source_client_id"]])
            print(f"playersInSync set: {self.playersInSync}" )
            if len(self.playersInSync) >= self.game.n_agents : self.isSyncPhase = False
            
        elif args.data["type"] == LiveEventType.ButtonPress.value and self.gameStarted:
            cube_id = args.data["extraData"]["pressable_object"]
            player_i = self.NickNameToPlayerIndex[args.data["source_client_id"]]
            
            # value added here and sleep in the game loop determine harvesting rate
            self.H[player_i] += H_Rate_One_Shot

            # scaling down the cube after each shot
            if cube_id in self.cube_manager.cubeScale:
                self.cube_manager.cubeScale[cube_id] *= 0.9
            else:
                self.cube_manager.cubeScale[cube_id] = 0.09 # instead of 0.1 there is 0.09 to distinguish such just shot from just reborn 
            scl = self.cube_manager.cubeScale[cube_id]
            self.client.PushCommand("set_object_scale", f"{cube_id} {scl},{scl},{scl} 0.2")

            # cube hit signal
            self.client.SendGenericCommand("play_audio_clip", "friend_request.ogg source 0.1 0.0 false")


    def connect(self):
        global intervention_set
        global intervention_EN, intervention_EP, intervention_SN, intervention_SP, intervention_TPN, intervention_TPP
        self.client.StartClient(self.config_SpaceRoom['appId'], "1_2.40")   
        time.sleep(5)
        self.client.JoinRoom(self.config_SpaceRoom['theRoomName'], 5)

        print(f"waiting for {self.game.n_agents} players to join {self.config_SpaceRoom['theRoomName']}")
#make this + 1 +2 if you want an obverver or +3 for 2 observers etc
        while self.client.GetPlayersList().Count < self.game.n_agents + 1 + n_obververs: # +1 because GuestXR is counted (although it is a meta pleyer)
            self.client.PushCommand("fade_out", 
                                    f"0.3 'Please wait.\
                                    \nThe game is about to start.\
                                    \nWaiting for {self.game.n_agents - self.client.GetPlayersList().Count+1} players to join.'")
            print(".", end="", flush=True)
            time.sleep(2)

        print(f"Users connected (including GuestXR): {self.client.GetPlayersList().Count}")
        self.print_player_list()
        time.sleep(5)

        # synchronization of the start time from Bernhard
        self.customEventTime=datetime.datetime.now
        while len(self.connectedusers)<self.game.n_agents:
            time.sleep(2)
            self.client.PushCommand("send_event", "connected")
            print(f"synchronizet users n: {len(self.connectedusers)} are: {self.connectedusers}")

        # preparing signs of wealth for use afterwards 
        self.prepare_wealth()        
        
        # prepare fog
        self.client.PushCommand("spawn_object", "commons_fog ParticleSystem commons_fog_anchor")
        time.sleep(1)   
        self.client.PushCommand("disable_object", "ParticleSystem")

        self.client.PushCommand("show_text", "global_message \"Cześć!\" 1.0") 
        ## df3acd8e-7c3a-4461-82ec-ed15ae3f1a88 - woman_rich
        ## beff84fc-983d-4fa0-baf4-b0f22da3706c - woman_poor
        ## 0f9d8310-48a1-4043-82f0-de73363ee0f3 - woman_medium
        ## b6b2c370-e228-40ef-b7e8-f5f331d77275 - man_rich
        ## 82c95958-3b63-4eea-9ef8-814000fb80b6 - man_poor
        ## 47f0f240-5e4a-4ad8-90b5-4a49563a08fc - man_medium
        for userID in self.UserIdToPlayerIndex.keys():
            self.client.SetNewAvatar(userID,"df3acd8e-7c3a-4461-82ec-ed15ae3f1a88")

# After all the players appear, the text disappears, the room becomes visible. 
# An instructor (instructor or instruction_agent?) is also present in the room.
        time.sleep(1)
        self.client.PushCommand("fade_in", "1.0")      
# All players are in the room, but they cannot play yet. Their lasers are inactive. 
        self.client.PushCommand("set_laser_pointer_active", "false") # SendGenericCommand
        time.sleep(1)        
# Common resource that is, the cubes on the table are gray (inactive).
        self.cube_manager.spawn_all_objects() # I changed that they are gray by default
        time.sleep(1)

                                                
        print (f"{self.client.GetPlayersList().Count} players joined.")
        self.createLookupDictionary()
        print(self.UserIdToPlayerIndex)
        print(self.NickNameToPlayerIndex)
        print(self.PlayerIndexToPlayerNr)
        
        self.print_player_list()

# Birds can be heard – Play Audio Clip, birds.ogg
        self.client.PushCommand("play_audio_clip", "birds.ogg ambientNoise 0.2 1.0 true")
       
# The instructor starts giving instructions about 12 seconds after everyone in the room appears 
        for i in range(1, 6) :     
            self.client.PushCommand("show_text", f"participant{i}_score_text \"Proszę skup się teraz na instrukcji\" 1.0") 

        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_01")
        ## print("Take 01 ......")
        ## time.sleep(52.062041666666666) # waiting for the end of the clip

        print(1, self.isSyncPhase)
# Synchronization
        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_02") # zawira ping
        ## print("Take 02 ......")
        ## time.sleep(60.9959375) # waiting for the end of the clip
# Play instruciotn sound - is now part of the recording
# sound of the round, then everyone has to press the laser. And all the cubes will be activated.
        self.client.PushCommand("set_laser_pointer_active", "true")  

        waitTimeN = 0
        while self.isSyncPhase: # is waiting for everyone to use the laser
            time.sleep(0.1)
            waitTimeN += 1
            if waitTimeN % 100 == 0 :
                # try again
                self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_03") # zawira ping
                print("Take 03 ......") # waiting for the end of the clip
                time.sleep(13.5575625)
        self.cube_manager.set_color_all_objects("#40982f") # the color of the cubes becomes green
        self.client.PushCommand("set_laser_pointer_active", "false")     
        print("laser inactive")
        time.sleep(2)
        print(2, self.isSyncPhase)
      
# ClimateChange_Instruct_pl_04 succeeded
        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_04") 
        ## print("Take 04 ......")
        ## time.sleep(4.5191875)  # waiting for the end of the clip
     
# ClimateChange_Instruct_pl_05
        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_05")
        ## print("Take 05 ......")
        ## time.sleep(138.266125)  # waiting for the end of the clip
        
# ClimateChange_Instruct_pl_06
        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_06")
        ## print("Take 06 ......")
        ## time.sleep(17.893895833333332)  # waiting for the end of the clip
        
# ClimateChange_Instruct_pl_07 
        ## self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_07") # zawiera ping
        ## print("Take 07 ......")
        ## time.sleep(22.360833333333332)  # waiting for the end of the clip

        self.gameStarted = True

# The game begins. The instructor's avatar disappears. Lasers are active.
        self.client.PushCommand("disable_object", "instructor") # "instruction_agent")  # instructor The_Guest ?? How to disable instruction_agent???
        for i in range(1, 6) :     
            self.client.PushCommand("show_text", f"participant{i}_score_text \"p{i} Zasoby: 0\" 1.0") 

# Disabling verbal communication between players – they should not be able to hear each other once the game starts (after Audio 7).        
        # set_character_audio_volume {character_id} {target_volume} {fade_in_time} 
        for userID in self.UserIdToPlayerIndex.keys() :
            self.client.PushCommand("set_character_audio_volume", f"{userID} 0.0 0.5")
        
# Duration of game round: 30s 
# Pause in the game: 15s
# Number of rounds: 8

# Start of game loop ######################################################################################
# round: sound (ping), game clock or: PLAY - play mark on the display - turning on the lasers, color of the deposit
# End of game round: sound (ping x 2), pause timer or PAUZE - mark on display 0 turn off lasers, fade out deposit color

        self.client.PushCommand("set_laser_pointer_active", "true") 
        print("laser active")
        # time.sleep(3) # artificially added delay, because it is not known why, the laser does not immediately turn on. Maybe because of PushCommand

        for ri in range(self.NR): # number of rounds: 8
            self.client.PushCommand("fade_in", "1.0")      
            self.client.PushCommand("show_text", f"global_message \"Runda {ri+1}\" 1.0") 

            with open(DATA / f"{file_name}_round_{ri}.jsonl", "w") as file:
                while self.i < self.T : # Duration of a game round: 30s
                
                    self.H = np.zeros(self.game.n_agents)
                    time.sleep(1.0)   # every 1s the state of the game and the environment is updated 
                                # attention! it affects the duration of the round

                    print(self.H)
                    self.game.H = self.H
                    self.game.dynamics.run(1 / (self.T*self.NR)) # 1/self.T is an entire epoch in one round, 
                                                        # because the “run” for 1 is an entire epoch, i.e., a full restoration of the environment
                    self.i = self.i+1
                    self.cube_manager.scale_all_objects() # to reverse the scaling effect when the cursor goes off the object

                    envE = max(0, self.game.model.E / self.game.n_agents)
                    envK = self.game.model.envir.K / self.game.n_agents
                    self.cube_manager.sync_with_Et(envE, envK)
                
                    print(f"Et:EK:rQ:aQ:Et/EK: {envE} : {envK} : {len(self.cube_manager.removed_cubes)} : {len(self.cube_manager.avaliable_cubes)} : {envE/envK}")
                    # print(self.cube_manager.cubeScale)
                    wealth_dct = {}
                    for p_i in range(self.game.n_agents):
                        player_n = self.PlayerIndexToPlayerNr[p_i]
                        score_str=f"participant{player_n}_score_text \"Posiadane zasoby: {round(self.game.U[p_i], 2)}\" 1" 
                        self.client.SendGenericCommand("show_text", score_str) 
                        self.update_wealth(p_i, player_n)
                        wealth_dct[player_n] = round(self.game.U[p_i],2)

                    tmp = {
                        "Et": envE,
                        "EK": envK,
                        "rQ": len(self.cube_manager.removed_cubes),
                        "aQ": len(self.cube_manager.avaliable_cubes),
                        "Enviornment Condition": envE/envK,
                        **wealth_dct
                    }
                    file.write(json.dumps(tmp) + "\n")

                
# Pause in the game: 15s ################################################################

            self.i = 0 # round time reset
            # wylaczenie lasera
            self.client.PushCommand("set_laser_pointer_active", "false") 
            print("laser inactive")
            # sygnal poczatku przerwy
            self.client.SendGenericCommand("play_audio_clip", "signal.ogg source 0.1 0.0 false")
            self.client.PushCommand("show_text", f"global_message \"Przerwa\" 1.0") 
            # wyszarzenie wszyskich kostek na czas przerwy
            self.cube_manager.set_color_all_objects("#777777")
            time.sleep(2) # break time part 1 - czas na zakonczenie wyszarzania kostek

            # obliczenie stanu srodowiska
            envE = max(0, self.game.model.E / self.game.n_agents)
            envK = self.game.model.envir.K / self.game.n_agents
            EnviCondition = envE / envK 
            print(f"EnviCondition: {EnviCondition}")

            ## ustalenie parametrow do interwecnji GuestXR
            
            # 1. Środowisko (kostki)
            if 0.5 < EnviCondition : # the color of the cubes becomes ok [green]
                x_EP = True
                x_EN = not x_EP
            elif 0.3 < EnviCondition : # color of cubes becomes warning [orange]
                x_EP = False
                x_EN = not x_EP
            else: # color of cubes becomes critical [red]
                x_EP = False
                x_EN = not x_EP

            # 2. Środowisko (mgła)
            if EnviCondition <= 0.30 : # aktywacja mgły
                x_M = True
                x_BM = not x_M
            else :
                x_M = False
                x_BM = not x_M
                
            # 3. Podział bogactwa:
            if self.game.n_agents > 1 :
                for i in range(self.game.n_agents-1):
                    if self.playersWealthDistribution[i] != self.playersWealthDistribution[i+1] : break
                x_SN = (self.playersWealthDistribution[i] != self.playersWealthDistribution[i+1])
            else :
                x_SN = False  
            x_SP = not x_SN

            ###### interwencje GuestXR ######
            #################################
                            
            ## if 0.7 < EnviCondition and "Audio_3_EP_pl" in intervention_set: # Pierwsza interwencja zafiksowana na pierwsza przerwe
            if ri == 0 and "Audio_3_EP_pl" in intervention_set: # Pierwsza interwencja zafiksowana na pierwsza przerwe
                intervention = "Audio_3_EP_pl" 
                intervention_set -= {intervention}
                intervention_EP -= {intervention}
            elif x_M and "Audio_4_EN_pl" in intervention_set:
                intervention = "Audio_4_EN_pl"
                intervention_set -= {intervention}
                intervention_EN -= {intervention}
            elif x_EP and len(intervention_EP) > 0:
                intervention = random.choice(list(intervention_EP))
                intervention_set -= {intervention}
                intervention_EP -= {intervention}
            elif x_EN and len(intervention_EN) > 0:
                intervention = random.choice(list(intervention_EN))
                intervention_set -= {intervention}
                intervention_EN -= {intervention}
            elif x_EP and len(intervention_TPP) > 0:
                intervention = random.choice(list(intervention_TPP))
                intervention_set -= {intervention}
                intervention_TPP -= {intervention}
            elif x_EN and len(intervention_TPN) > 0:
                intervention = random.choice(list(intervention_TPN))
                intervention_set -= {intervention}
                intervention_TPN -= {intervention}
            elif x_SN and len(intervention_SN) > 0:
                intervention = random.choice(list(intervention_SN))
                intervention_set -= {intervention}
                intervention_SN -= {intervention}
            elif x_SP and len(intervention_SP) > 0:
                intervention = random.choice(list(intervention_SP))
                intervention_set -= {intervention}
                intervention_SP -= {intervention}
            else :
                intervention = ""                
            # wykonanie wybranej interwencji glosowej
            if intervention != "":
                print(f"play_audio_clip :: {intervention}.opus")
                self.client.PushCommand("play_audio_clip", f"{intervention}.opus ambientNoise 1.0 1.0 false") 
                
            # Zmiana kolory drzewa na czerwone
            if EnviCondition < 0.5:
                self.client.PushCommand("set_object_color", "---tree-- #FF0011 2.0") # changes the color of the tree
            else:
                self.client.PushCommand("set_object_color", "---tree-- #FFFFFF 2.0") # changes the color of the tree
                
            # Zmiana koloru środowiska na czerwone
            if EnviCondition < .7:
                self.client.PushCommand("fade_skybox_tint", "#FF0011 5") # changes color outside the window
            else:
                self.client.PushCommand("fade_skybox_tint", "#FFFFFF 5") # changes color outside the window
                self.client.PushCommand("play_audio_clip", "birds.ogg ambientNoise 0.2 1.0 true") # birds

            # aktywacja mgly i efekty dwiekowe
            if EnviCondition <= 0.3: # aktywacja mgły
                self.backFromHell = True
                self.client.PushCommand("enable_object", "ParticleSystem")
                self.client.PushCommand("fade_fog_color", "red 0.5")
                self.client.PushCommand("fade_fog_intensity", "0.5 0.5")
                self.client.PushCommand("play_audio_clip", "Sound_5_Industrial.opus ambientNoise 0.2 1.0 true")
            elif self.backFromHell:
                self.backFromHell = False
                self.client.PushCommand("disable_object", "ParticleSystem")


            time.sleep(10) # break time part 2 - w tym czasie napewno zmieszcza sie interwnecje w tym gloswe

            # Aktualizcja koloru kostek
            if 0.5 < EnviCondition:
                self.cube_manager.set_color_all_objects("#40982f") # the color of the cubes becomes ok [green]
            elif 0.3 < EnviCondition :
                self.cube_manager.set_color_all_objects("#af9410") # color of cubes becomes warning [orange]
            else:
                self.cube_manager.set_color_all_objects("#af1010") # color of cubes becomes critical [red]

            if ri < self.NR - 1 :
                # koniec rundy - dwieck konca i laser on
                self.client.SendGenericCommand("play_audio_clip", "signal.opus source 1.0 0.0 false")
                self.client.SendGenericCommand("play_audio_clip", "friend_request.ogg source 0.1 0.0 false")
                time.sleep(2) # break time part 3 - czas naz miane koloru kostek
                self.client.PushCommand("set_laser_pointer_active", "true") 
                print("laser active")
                time.sleep(1) # break time part 4 - czas na aktywacje lasera
            else : # jak ostatnia runda to nie ma dzieku konca przerwy i nie wlacza sie laser
                time.sleep(2) # break time part 3 - czas naz miane koloru kostek

# koniec gry #############################################################
 
        self.client.PushCommand("enable_object", "instructor")
# ClimateChange_Instruct_pl_08
        self.client.PushCommand("play_take", "ClimateChange_Instruct_pl_08")  # waiting for the end of the clip 
        print("Take 08 ......")
        time.sleep(16.404916666666665)

def main() -> None:
    config = None
    with open("SpaceRoom.json", 'r') as file:
        config = json.load(file)
         
    app = Application(config)
    print("test_app")
    app.connect()

# %%
if __name__ in "__main__":
    main()
