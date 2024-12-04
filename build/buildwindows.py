from cx_Freeze import setup,Executable
import os

build_options = {"include_files" : ["engine","game"],
                 "build_exe" : "build/WindowsOutput"}

setup(name = "Unnamed MedusaEngine Game",
      version = "0.1",
      description = "",
      options = {"build_exe" : build_options},
      executables=[Executable("main.py", base="Win32GUI")])

def RemoveFiles(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".pyc"):
                os.remove(os.path.join(root,file))
                print(f"Removed Source File: {file}")

RemoveFiles("build/WindowsOutput/engine")
RemoveFiles("build/WindowsOutput/game")