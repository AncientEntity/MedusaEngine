# MedusaEngine

Medusa is a FOSS Python based game engine for creating 2D games in Python with Pygame. It's not intended to be packaged as a module but is meant to be embedded directly into your project files.

Game demos below

# Requirements
Python 3.11 or newer

requirements.txt: 
```
cx_Freeze==7.0.0
cx_Logging==3.2.0
lief==0.14.1
pygame-ce==2.4.1
pygbag==0.9.1  
```
- Make sure to double check the individual licenses for each requirement to know what you can and cannot do with them.
- Cx_freeze, cx_logging, and lief is only required if you use build/buildwindows.py
- pygbag is only required if you use build/buildweb.py

# Project Setup
- Setup instructions are intended for PyCharm. Setup for other IDEs may vary.

1. `git clone https://github.com/AncientEntity/MedusaEngine.git`
2. Open the project in PyCharm
3. Configure a new Python Interpreter/Virtual Environment (venv) for the project (Python 3.11>=)
4. Run `pip install -r requirements.txt` while in the venv (Inside PyCharm Terminal it should default to the venv automatically)
5. Done! Try running the run configuration "run game" as there is an example game that should run.

# Project Structure
Below is the intended project structure but doesn't necessarily need to be followed.
- `/build`: This directory contains build scripts and build outputs for the project. If you need to compile or build the project, you'll find the necessary scripts and configurations here.

- `/engine`: This directory contains engine files. These files are responsible for the core functionality of the engine, such as rendering, physics, and audio.

- `/game`: This directory contains the game files. Here you'll find the assets, scripts, and other resources that make up the game itself.

# Demos & Gifs

Knighty McKnightFace Demo [(play here)](https://anciententity.itch.io/knighty-mcknightyface) (source lives in master branch)

![python_EA7pzBiGDy](https://github.com/AncientEntity/MedusaEngine/assets/22735861/2d6d4a19-3c53-4a3e-b414-f3aecea981dd)

Knighty McKnightFace Demo [(play here)](https://anciententity.itch.io/knighty-mcknightyface) (source lives in master branch)

![python_BFsRluECuz](https://github.com/AncientEntity/MedusaEngine/assets/22735861/7ff670b8-0db8-4f6b-bd8f-63489d57ac3c)

Tiny Factory Demo [(play here)](https://anciententity.itch.io/tiny-factory-remastered) (source lives in tiny-factory-remake branch)

![chrome_qQIUbQQSkM](https://github.com/AncientEntity/MedusaEngine/assets/22735861/21df0074-4c44-4731-b59e-3c6df15cf031)

A* Pathfinding Demo [(play here)](https://anciententity.itch.io/medusa-astar-demo) (source lives in tilemap-pathfinding)

![python_JWMPJNHslx](https://github.com/user-attachments/assets/3a5f0afc-5813-4d55-9ef9-80f314c2cf8d)

