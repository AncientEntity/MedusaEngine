import os
import shutil
import subprocess
import sys
from pathlib import Path

skipAll = True if "--skipAll" in sys.argv else False

def GetAnswer(text, default):
    if(skipAll):
        return default

    while True:
        print(text + " (Y/N): ")
        val = input().upper()[0]
        if val == "Y" or val == "N":
            return True if val[0] == "Y" else False
        else:
            print("Invalid answer. Please respond Y or N")

workingDirectory = Path.cwd()
templatePath = str(workingDirectory) + "\\build\\medusaweb.tmpl"

shouldUMEBlock = GetAnswer("Enable ume_block?", True)
getArchive = GetAnswer("Archive? (Y for itch.io uploads..., etc)", False)

def ConstructCL():
    cl = [".venv\\Scripts\\pygbag.exe"]
    if shouldUMEBlock == False:
        cl.append("--ume_block")
        cl.append("0")
    if getArchive:
        cl.append("--archive")
    cl.append("--disable-sound-format-error") # Web builds only support OGG files, but sometimes you have both...
    cl.append("--template") # Web builds only support OGG files, but sometimes you have both...
    cl.append(templatePath) # Web builds only support OGG files, but sometimes you have both...
    cl.append("build\\webtemp\\main.py")
    return cl

if os.path.exists("build\\webtemp"):
    shutil.rmtree("build\\webtemp")
os.mkdir("build\\webtemp")
shutil.copytree("game", "build\\webtemp\\game")
shutil.copytree("engine", "build\\webtemp\\engine")
shutil.copy2("main.py", "build\\webtemp")
shutil.copy2("favicon.png", "build\\webtemp")

cl = ConstructCL()
print(f"Building with: {cl}")
subprocess.run(cl)