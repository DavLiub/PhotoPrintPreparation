@echo off
python -m pip install -U pip
python -m pip install -e .
set PYTHONPATH=%CD%\src
python -m unittest discover -s tests -v
