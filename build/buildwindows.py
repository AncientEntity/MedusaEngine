from cx_Freeze import setup,Executable
import os, shutil

build_options = {"include_files" : ["engine","game"],
                 "build_exe" : "build/WindowsOutput"}

setup(name = "Unnamed MedusaEngine Game",
      version = "0.1",
      description = "",
      options = {"build_exe" : build_options},
      executables=[Executable("main.py", base="GUI")])

def RemoveFiles(directory):
    # Remove Source Files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".pyc"):
                os.remove(os.path.join(root,file))
                print(f"Removed Source File: {file}")

    # Remove Empty Folders
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir in dirs:
            joinedPath = os.path.join(root,dir)
            if not os.listdir(joinedPath):
                shutil.rmtree(joinedPath)
                print(f"Removed Empty Folder: {joinedPath}")

RemoveFiles("build/WindowsOutput/engine")
RemoveFiles("build/WindowsOutput/game")