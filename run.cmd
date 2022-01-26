call .\venv\Scripts\activate.bat
uvicorn main:api --host "0.0.0.0" --port 8000 --forwarded-allow-ips ["*"]
