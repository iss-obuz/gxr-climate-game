# %%
import matplotlib.pyplot as plt
from climate_game import DATA
import os
from collections import defaultdict
import re
import pandas as pd
import json

# %%
rgx = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}")
# %%
fls_dct = defaultdict(list)
for item in os.scandir(DATA):
    fls_dct[rgx.search(item.name).group()] += [item]

for item in fls_dct:
    fls_dct[item] = sorted(fls_dct[item], key=lambda x: x.name)


# %%
def create_df(dct: dict, dt: str) -> pd.DataFrame:
    """Converts a dictionary into a pd.DataFrame

    Parameters
    ----------
    dt
        a string with the date of the study.
    dct
        a dict with the names of the files. Keys
        are dates and values lists of DirectoryEntries.

    Returns
    -------
        a pd.DataFrame with the results of the whole game.
    """
    lst = []
    dct_rnm = {
        "guestxr.oculusd@gmail.com": "Headset D",
        "guestxroculusa@gmail.com": "Headset A",
        "guestxr.oculusc@gmail.com": "Headset C",
        "guestxrgogleb@gmail.com": "Headset B",
    }
    for item in dct[dt]:
        for line in open(item):
            tmp = json.loads(line)
            lst.append(tmp)
    return pd.DataFrame.from_dict(lst).rename(columns=dct_rnm).reset_index(drop=True)


# %%
df = create_df(fls_dct, dt="2025_12_01_12_22")
# %%
## Plot Resources
fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

ax1.plot(
    df["Enviornment Condition"],
    color="black",
    linestyle="dashed",
    linewidth=0.7,
)
for headset in ["Headset A", "Headset B", "Headset C", "Headset D"]:
    if headset in df.columns:
        ax2.plot(df[headset], label=headset, linewidth=0.8)
ax2.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncols=3)
ax2.set_xlim(-1, 241)
ax1.set_ylim(0, 1.1)
for x in range(0, 240, 60):
    ax1.axvspan(x, x + 30, facecolor="gray", alpha=0.2)
for x in range(0, 8, 1):
    ax1.text(
        x=x * 30 + 15,
        y=1.15,
        s=f"Round {x + 1}",
        horizontalalignment="center",
        verticalalignment="center",
    )
ax1.hlines(xmin=0, xmax=240, y=0.5, color="#af9410", linestyles="dashed", linewidth=0.7)
ax1.hlines(xmin=0, xmax=240, y=0.3, color="#af1010", linestyles="dashed", linewidth=0.7)
ax2.set_ylabel("Resources", rotation=270, labelpad=6)
ax1.set_ylabel("Environment Condition")
ax2.set_position([0.1, 0.15, 0.8, 0.75])
# %%
