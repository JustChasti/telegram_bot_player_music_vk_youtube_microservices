install rabbitmq
python -m venv venv 
pip install -r requirements.txt

configure config.py
2 requests to server now - read their description in views/main.py

uvicorn application:app --reload