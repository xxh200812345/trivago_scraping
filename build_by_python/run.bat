cd %~dp0

echo %cd%

set VIRTUALENV_PATH=trivago_venv

if exist %VIRTUALENV_PATH% (
    echo Virtual environment already exists
) else (
    echo Virtual environment does not exist, creating a new virtual environment...

    python -m venv "%VIRTUALENV_PATH%"
    
)
call %VIRTUALENV_PATH%\Scripts\activate

pip install -r requirements.txt
python trivago.py
