from cx_Freeze import setup,Executable

build_options = {"include_files" : "data"}

setup(name = "Unnamed PyBulletHell",
      version = "0.1",
      description = "",
      options = {"build_exe" : build_options},
      executables=[Executable("main.py", base="Win32GUI")])