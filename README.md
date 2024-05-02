# MedusaEngine

Medusa is a FOSS Python based game engine for creating 2D games in Python with Pygame. It's not intended to be packaged as a module but is meant to be embedded directly into your project files.

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
