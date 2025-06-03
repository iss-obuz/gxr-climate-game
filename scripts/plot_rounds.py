# %% 
import matplotlib.pyplot as plt
from climate_game import PNG, DATA
from climate_game.utils import merge_rounds, headset_name
import os
from collections import defaultdict
import re
import pandas as pd

# %%
rgx = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}")
conditions = { 
              "2025_05_16_17_04" : "Interventions",
              "2025_05_16_16_12" : "Interventions",
              "2025_05_23_15_45" : "Intervnetions",
              "2025_05_20_15_15" : "No Interventions",
              "2025_05_20_16_12" : "No Interventions",
              "2025_05_21_16_07" : "No Interventions",
}
# %%
fls_dct = defaultdict(list)
for item in os.scandir(DATA):
    fls_dct[rgx.search(item.name).group()] += [item]
    
# %%
for game in conditions:
    print(f"Plot game {game} from {conditions[game]} condition.")
    output = merge_rounds(lst = fls_dct[game])
    df = pd.DataFrame.from_dict(output)
    df = df.reset_index().sort_values(["round", "index"])
    df = headset_name(df)

    fig, ax1 = plt.subplots(figsize = (9,5))
    fig.subplots_adjust(wspace=0.5, hspace=0.20, top=0.95, bottom=0.05)
    ax2 = ax1.twinx()


    ax1.plot(df.reset_index()["Enviornment Condition"], color = "black", linestyle='dashed', linewidth = .7)
    ax2.plot(df.reset_index()["Headset B"], label = "Headset B", linewidth = .9)
    ax2.plot(df.reset_index()["Headset C"], label = "Headset C", linewidth = .9)
    ax2.plot(df.reset_index()["Headset D"], label = "Headset D", linewidth = .9)
    ax2.legend(loc = "lower center", bbox_to_anchor = (.5, -.15), ncols = 3)
    ax2.set_xlim(-1,241) 
    ax1.set_ylim(0,1.1)
    for x in range(0, 240, 60):
        ax1.axvspan(x, x+30, facecolor='gray', alpha=.2)
    for x in range(0, 8,1):
        ax1.text(x = x * 30 + 15, y = 1.15, s = f"Round {x + 1}", horizontalalignment='center', verticalalignment='center')
    ax1.hlines(xmin = 0, xmax = 240,y = .5, color = "#af9410", linestyles = "dashed", linewidth = .7)
    ax1.hlines(xmin = 0, xmax = 240,y = .3, color = "#af1010", linestyles = "dashed", linewidth = .7)
    ax2.set_ylabel("Resources", rotation = 270)
    ax1.set_ylabel("Environment Condition")
    ax2.set_position([0.1,0.15,.8,.75])
    plt.savefig(PNG/f"{"_".join(conditions[game].lower().split())}_{game}.png", dpi = 200)
    if __name__ not in "__main__":
        plt.show()

# %%
