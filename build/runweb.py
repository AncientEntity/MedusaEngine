import subprocess
from pathlib import Path

workingDirectory = Path.cwd()
templatePath = str(workingDirectory) + "\\build\\medusaweb.tmpl"

subprocess.run([".venv\\Scripts\\pygbag.exe", "--template", templatePath, "--disable-sound-format-error", "main.py"])