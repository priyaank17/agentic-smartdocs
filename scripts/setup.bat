call npm install
call python -m venv .venv
call .venv/Scripts/activate
call python -m pip install --upgrade pip pipenv
call python -m pipenv install --dev --pre
