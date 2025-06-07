@echo off
IF NOT EXIST venv (
    python -m venv venv
)

call venv\Scripts\activate

git pull
pip install -r requirements.txt

python main.py
