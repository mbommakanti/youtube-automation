@echo off
call venv\Scripts\activate
echo Virtual environment activated!
echo Current directory: %CD%
echo Python version:
python --version
cmd /k