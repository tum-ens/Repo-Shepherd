@echo off
REM Step 1: Create virtual environment
python -m venv venv

REM Step 2: Activate the virtual environment
call venv\Scripts\activate

REM Step 3: Install requirements
pip install -r requirements.txt

REM Step 4: Run the Python file
python app\gui-dev\main.py

pause
