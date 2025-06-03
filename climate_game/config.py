config = {
    "appId": "40a25e24-4d21-4269-bd18-ad58062199a6",
    "voiceAppId": "5c4f5759-7d52-4be8-b507-987ce5dd77f3",
    "region": "EU",
    "theRoomName": "guestxr_spaceroom",
}
nicks_player_nr = {  # this number indicates to which position the user has been assigned
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
    "#af1010": 0,  ## red
    "#af9410": 0.3,  ## orange
    "#40982f": 0.5,  ## green
}
