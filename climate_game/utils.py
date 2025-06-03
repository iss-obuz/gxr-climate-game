import re
import json
import pandas as pd

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
    rgx = re.compile(r"\d*\.")
    return int(rgx.search(name).group().replace(".", ""))
    
def merge_rounds(lst: list) -> list:
    """Takes a list of DirEntry and merges their content into a list of dictionaires.

    Parameters
    ----------
    lst
        a list of DirEntries

    Returns
    -------
        a list of dictionaries
    """
    output = []
    for file_name in lst:
        for line in open(file_name, "r"):
            tmp = json.loads(line)
            tmp.update({ "round" : get_round(file_name.name) })
            output.append(tmp)
    return output

def headset_name(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns with participants socres.

    Parameters
    ----------
    df
        dataframe with scores.

    Returns
    -------
        dataframe where the columns are uniform and straightforward (at least in the case of headsets' names)
    """
    headset_names = { "guestxrgogleb@gmail.com" : "Headset B",
            "guestxr.oculusc@gmail.com" : "Headset C",
            "guestxr.oculusd@gmail.com" : "Headset D"}
    if not all(item in df.columns for item in headset_names):
        player_to_index = { value: key for key, value in df["PlayerIndexToPlayerNr"][0].items() }
        index_to_nick = { value: key for key, value in df["NickNameToPlayerIndex"][0].items() }
        player_to_nick = { str(key) : index_to_nick[int(value)] for key, value in player_to_index.items() }
        df = df.rename(columns = player_to_nick) 
    df = df.rename(columns = headset_names)
    return df