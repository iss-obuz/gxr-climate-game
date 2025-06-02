# %% 
import matplotlib.pyplot as plt
import json
from climate_game import PNG, DATA
import os
from collections import defaultdict
import re
import pandas as pd

# %%
rgx = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}")

def get_round(name: str) -> int:
    """Get the round number from the name of the file.

    Parameters
    ----------
    name
        name of the file

    Returns
    -------
        round number
    """
    rgx = re.compile(r"\d\.")
    return int(rgx.search(name).group().replace(".", ""))
    

# %%
fls_dct = defaultdict(list)
for item in os.scandir(DATA):
    fls_dct[rgx.search(item.name).group()] += [item]
    
fls_dct = { key : value for key, value in fls_dct.items() if len(value) == 8 }
# %%
for game in fls_dct:
    output = []
    for file_name in fls_dct[game]:
        with open(file_name, "r") as file:
            for line in file.readlines():
                tmp = json.loads(line)
                tmp.update({ "round" : get_round(file_name.name)})
                output.append(tmp)
    

    df = pd.DataFrame.from_dict(output)
    df = df.reset_index().sort_values(["round", "index"])
    fig, ax1 = plt.subplots(figsize = (9,4))
    fig.subplots_adjust(wspace=0.5, hspace=0.20, top=0.85, bottom=0.05)
    ax2 = ax1.twinx()


    ax1.plot(df.reset_index()["Enviornment Condition"], color = "black")
    if len(df.columns) < 9:
        continue
    if "2" in df.columns:
        ax2.plot(df.reset_index()["2"])
        ax2.plot(df.reset_index()["3"])
        ax2.plot(df.reset_index()["5"])
    else:
        ax2.plot(df.reset_index()["guestxr.oculusd@gmail.com"])
        ax2.plot(df.reset_index()["guestxr.oculusc@gmail.com"])
        ax2.plot(df.reset_index()["guestxrgogleb@gmail.com"])
    ax2.set_xlim(0,240)    
    for x in range(0, 240, 60):
        ax1.axvspan(x, x+30, facecolor='gray', alpha=.2)
    ax2.set_ylabel("Resources")
    ax1.set_ylabel("Environmentl Condition")
    plt.title(game)
    plt.savefig(PNG/f"{game}.png", dpi = 200)
    plt.show()

# %%
