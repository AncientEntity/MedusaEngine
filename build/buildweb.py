import subprocess
from pathlib import Path

def GetAnswer(text):
    while True:
        print(text + " (Y/N): ")
        val = input().upper()[0]
        if val == "Y" or val == "N":
            return True if val[0] == "Y" else False
        else:
            print("Invalid answer. Please respond Y or N")

workingDirectory = Path.cwd()
templatePath = str(workingDirectory) + "\\build\\medusaweb.tmpl"

shouldUMEBlock = GetAnswer("Enable ume_block?")
getArchive = GetAnswer("Archive? (Y for itch.io uploads..., etc)")

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
    cl.append("main.py")
    return cl

cl = ConstructCL()
print(f"Building with: {cl}")
subprocess.run(cl)