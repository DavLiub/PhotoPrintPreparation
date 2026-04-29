@echo off
python -m pip install -U pip
python -m pip install -e .[image]
set PYTHONPATH=%CD%\src
python -m unittest discover -s tests -v
