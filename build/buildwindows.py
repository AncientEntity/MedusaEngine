from cx_Freeze import setup,Executable

build_options = {"include_files" : ["engine","game"], "build_exe" : "build/WindowsOutput"}

setup(name = "Unnamed MedusaEngine Game",
      version = "0.1",
      description = "",
      options = {"build_exe" : build_options},
      executables=[Executable("main.py", base="Win32GUI")])