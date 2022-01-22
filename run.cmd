call .\venv\Scripts\activate.bat
uvicorn --host "0.0.0.0" --port 8000 --reload main:api
