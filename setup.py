from cx_Freeze import setup,Executable
import os, sys

includefiles = ['Resources/', 'README.md']
includes = []
excludes = ['Tkinter', 'numpy', 'scipy', 'email', 'xml', 'pyreadline', 'unitest', 'logging', 'pkg_resources', 'distutils']
packages = ['pygame']

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = 'Skeet-Shooting',
    version = '1.0',
    description = 'A simple 2D skeet shooting game.',
    author = 'Charles & Edward',
    author_email = 'shz620@outlook.com',
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
    executables = [Executable('skeetgame.py')]
)