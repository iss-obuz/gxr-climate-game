# %%
import matplotlib.pyplot as plt
from climate_game import PNG, DATA
from climate_game.utils import merge_rounds, headset_name
import os
from collections import defaultdict
import re
import pandas as pd
import numpy as np

# %%
rgx = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}")
conditions = {
    "2025_05_16_17_04": "Interventions",
    "2025_05_16_16_12": "Interventions",
    "2025_05_23_15_45": "Interventions",
    "2025_05_20_15_15": "No Interventions",
    "2025_05_20_16_12": "No Interventions",
    "2025_05_21_16_07": "No Interventions",
}
# %%
fls_dct = defaultdict(list)
for item in os.scandir(DATA):
    fls_dct[rgx.search(item.name).group()] += [item]

# %%
for game in conditions:
    print(f"Plot game {game} from {conditions[game]} condition.")
    output = merge_rounds(lst=fls_dct[game])
    df = pd.DataFrame.from_dict(output)
    df = df.reset_index().sort_values(["round", "index"])
    df = headset_name(df)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    fig.subplots_adjust(wspace=0.5, hspace=0.20, top=0.95, bottom=0.05)
    ax2 = ax1.twinx()

    ax1.plot(
        df.reset_index()["Enviornment Condition"],
        color="black",
        linestyle="dashed",
        linewidth=0.7,
    )
    ax2.plot(df.reset_index()["Headset B"], label="Headset B", linewidth=0.9)
    ax2.plot(df.reset_index()["Headset C"], label="Headset C", linewidth=0.9)
    ax2.plot(df.reset_index()["Headset D"], label="Headset D", linewidth=0.9)
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
    ax1.hlines(
        xmin=0, xmax=240, y=0.5, color="#af9410", linestyles="dashed", linewidth=0.7
    )
    ax1.hlines(
        xmin=0, xmax=240, y=0.3, color="#af1010", linestyles="dashed", linewidth=0.7
    )
    ax2.set_ylabel("Resources", rotation=270)
    ax1.set_ylabel("Environment Condition")
    ax2.set_position([0.1, 0.15, 0.8, 0.75])
    plt.savefig(
        PNG / f"{'_'.join(conditions[game].lower().split())}_{game}.png", dpi=200
    )
    if __name__ not in "__main__":
        plt.show()

# %%
interventions_lst = []
no_interventions_lst = []
all_df = pd.DataFrame()
for game in conditions:
    output = merge_rounds(lst=fls_dct[game])
    df = pd.DataFrame.from_dict(output)
    df = df.reset_index().sort_values(["round", "index"]).reset_index()
    df = df.drop(columns=["index", "level_0"])
    df["index"] = [item for item in range(240)]
    df = headset_name(df)
    df["condition"] = conditions[game]
    df["average_player"] = df[["Headset B", "Headset C", "Headset D"]].apply(
        lambda x: np.mean(x), axis=1
    )
    if conditions[game] == "Interventions":
        interventions_lst.append(df["Headset B"].tolist()[-1])
        interventions_lst.append(df["Headset C"].tolist()[-1])
        interventions_lst.append(df["Headset D"].tolist()[-1])
    else:
        no_interventions_lst.append(df["Headset B"].tolist()[-1])
        no_interventions_lst.append(df["Headset C"].tolist()[-1])
        no_interventions_lst.append(df["Headset D"].tolist()[-1])
    if game != "2025_05_20_15_15":
        df["average_player_corrected"] = df[
            ["Headset B", "Headset C", "Headset D"]
        ].apply(lambda x: np.mean(x), axis=1)
    else:
        df["average_player_corrected"] = df[["Headset B", "Headset C"]].apply(
            lambda x: np.mean(x), axis=1
        )
    all_df = pd.concat([all_df, df])

# %%
all_df = (
    all_df.groupby(["index", "condition"])[
        ["Enviornment Condition", "average_player", "average_player_corrected"]
    ]
    .mean()
    .reset_index()
)

# %%
fig, ax1 = plt.subplots(figsize=(9, 5))

ax1.plot(
    all_df.query("condition == 'Interventions'").reset_index()["average_player"],
    linewidth=1.5,
    label="Interventions",
)
ax1.plot(
    all_df.query("condition == 'No Interventions'").reset_index()[
        "average_player_corrected"
    ],
    linewidth=1.5,
    label="No Interventions",
)
ax1.plot(
    all_df.query("condition == 'No Interventions'").reset_index()["average_player"],
    linewidth=1.5,
    color="orange",
    linestyle="dashed",
)
ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.17), ncols=2, fontsize=13)
ax1.set_xlim(-1, 241)
for x in range(0, 240, 60):
    ax1.axvspan(x, x + 30, facecolor="gray", alpha=0.2)
for x in range(0, 8, 1):
    ax1.text(
        x=x * 30 + 15,
        y=14.75,
        s=f"Round {x + 1}",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=12,
        fontdict={"weight": "bold"},
    )
ax1.set_ylabel("Wealth\n(accumulated profit)", fontsize=12, fontdict={"weight": "bold"})
plt.tight_layout()

plt.savefig(PNG / "average_wealth.png", dpi=200)
if __name__ not in "__main__":
    plt.show()
# %%
fig, ax1 = plt.subplots(figsize=(9, 5))

ax1.plot(
    all_df.query("condition == 'Interventions'").reset_index()["Enviornment Condition"],
    linewidth=1.5,
    label="Interventions",
)
ax1.plot(
    all_df.query("condition == 'No Interventions'").reset_index()[
        "Enviornment Condition"
    ],
    linewidth=1.5,
    label="No Interventions",
)
ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.17), ncols=2, fontsize=13)
ax1.set_xlim(-1, 241)
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
        fontsize=12,
        fontdict={"weight": "bold"},
    )
ax1.hlines(xmin=0, xmax=240, y=0.5, color="#af9410", linestyles="dashed", linewidth=1.5)
ax1.hlines(xmin=0, xmax=240, y=0.3, color="#af1010", linestyles="dashed", linewidth=1.5)
ax1.set_ylabel("Environment Condition", fontsize=12, fontdict={"weight": "bold"})
plt.tight_layout()

plt.savefig(PNG / "average_environment.png", dpi=200)
if __name__ not in "__main__":
    plt.show()
# %%
