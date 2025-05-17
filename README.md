# `GuestXR Python Client`

This repo is for the Python Client of the Climate Game. In a nutshell it sends commends to GuestXR server which affect what people see in their headset.

## Main dependencies

* .NET ([.NET](https://dotnet.microsoft.com/en-us/download); tested on v 7.0)
* _python3.12_ ([anaconda distribution](https://www.anaconda.com/products/distribution) is preferred)
* other _python_dependencies are specified in `requirements.yaml`

## Setup

1. Clone the repo: git@github.com:iss-obuz/gxr-climate-game.git.
2. Set up the proper virtual environment.
```bash
cd RedditTransmisogyny2025
conda env create --name YOURENVIRONMENTNAME  --file environment.yaml
```
3. Activate `pre-commit`.
```bash
pre-commit install
```
3. Cross fingers.

## Running the game

In general, I would advise to run the game from the Visual Code. First, you need to open the proper folder and activate environment. When it is done open `climate_game_pl.py`. In the script there are a few parameters you can set. When you are done. Save the script and run it. Only afterwards players can enter the experience.

## Testing the game

If you know what you are doing it is possible to run the game in the interactive mode. Open in Visual Code the script `test_climate_game_pl.py`. You can run chunk after chunk to add new effects to the game.