import os, shutil

def CleanWeb():
    print("Cleaning Web")
    if(os.path.exists("build\\web")):
        shutil.rmtree("build\\web")
    if(os.path.exists("build\\web-cache")):
        shutil.rmtree("build\\web-cache")
    if(os.path.exists("build\\version.txt")):
        os.remove("build\\version.txt")
    print("Web Cleaned")

def CleanWindows():
    print("Cleaning Windows")
    if(os.path.exists("build\\WindowsOutput")):
        shutil.rmtree("build\\WindowsOutput")
    print("Windows Cleaned")

if __name__ == "__main__":
    print("Start Cleaning")
    CleanWeb()
    CleanWindows()
    print("Finished Cleaning")