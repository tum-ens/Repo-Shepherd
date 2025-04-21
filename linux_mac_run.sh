#!/bin/bash
# Step 1: Create virtual environment (if it doesn't already exist)
python3 -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Install requirements
pip install -r requirements.txt

# Step 4: Run the Python file
python app/gui-dev/main.py

# Optional: Pause the script until the user presses a key
read -p "Press any key to continue... " -n1 -s
echo
