# `GuestXR Python Client`

This repo is for the Python Client of the Climate Game. In a nutshell, it sends commands to the GuestXR server that affect what people see in their headsets.

## Main dependencies

* .NET ([.NET](https://dotnet.microsoft.com/en-us/download); tested on v 7.0)
* _python3.12_ ([anaconda distribution](https://www.anaconda.com/products/distribution) is preferred)
* other _python_ dependencies are specified in `environment.yaml`

## Setup

1. Clone the repo: git@github.com:iss-obuz/gxr-climate-game.git.
2. Set up the proper virtual environment.
```bash
cd gxr-climate-game
conda env create --file environment.yaml
```
3. Activate `pre-commit`.
```bash
pre-commit install
```
3. Cross fingers.

## Running the game

In general, I would advise running the game from Visual Studio Code. First, you need to open the proper folder and activate the environment. When it is done, open `climate_game_pl.py`. In the script, there are a few parameters you can set. When you are done, save the script and run it. Only afterwards can players enter the experience.

## Testing the game

If you know what you are doing, it is possible to run the game in interactive mode. Open in Visual Code the script `test_climate_game_pl.py`. You can run chunk after chunk to add new effects to the game.
